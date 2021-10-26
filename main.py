import sys
from numpy import ones, uint8
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from configparser import ConfigParser
from time import localtime, strftime
from pytesseract import image_to_string
from re import sub
from os import getcwd
import cv2 as cv
from threading import Thread, Barrier
import time


class Parser:
    id = []
    temperature = ""

    def _read_config(self):
        config = ConfigParser()
        config.read('info_group.ini')

        self.id = list(config['default']['ID'].split(','))
        self.temperature = config['default']['tempature']
        if self.temperature == "":
            self.temperature = "36.0"
        print("body temperature is set " + self.temperature)

    def get_config(self):
        self._read_config()
        return self.id, self.temperature


class Filler:
    url = 'https://www.nanya.com/tw/Page/115/%e5%93%a1%e5%b7%a5%e5%81%a5%e5%ba%b7%e5%9b%9e%e5%a0%b1%e8%a1%a8'
    t_config = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789'

    def __init__(self, id, temp):
        print("{} filler initial...\n".format(id))
        self.key = ""
        self.id = id
        self.temperature = temp

        # initial driver
        self.driver = webdriver.Firefox()
        self.driver.get(self.url)

        self.captcha()

    def fillbox(self):
        is_agree = self.driver.find_element_by_css_selector("input#IsAgree_Y + label")
        is_agree.click()
        emp_id = self.driver.find_element_by_name("Emp_ID")
        emp_id.send_keys(self.id)

        meas_method = self.driver.find_element_by_css_selector("input#Meas_Method_Ear + label")
        meas_method.click()

        temperature = self.driver.find_element_by_name("Temperature")
        temperature.send_keys(self.temperature)

        Take_AntFvrMed_N = self.driver.find_element_by_css_selector("input#Take_AntFvrMed_N + label")
        Take_AntFvrMed_N.click()

        IsHighRisk_N = self.driver.find_element_by_css_selector("input#IsHighRisk_N + label")
        IsHighRisk_N.click()
        IsPas7DMedCare_N = self.driver.find_element_by_css_selector("input#IsPas7DMedCare_N + label")
        IsPas7DMedCare_N.click()
        IsPas14DTest_None = self.driver.find_element_by_css_selector("input#IsPas14DTest_None + label")
        IsPas14DTest_None.click()

        IsPas14DTest_None = self.driver.find_element_by_css_selector("input#IsPas14DTest_None + label")
        IsPas14DTest_None.click()
        # Agree_RapidTest_Y = driver.find_element_by_css_selector('input#Agree_RapidTest_Y + label')
        # Agree_RapidTest_Y.click()
        IsConfirm_Y = self.driver.find_element_by_css_selector("input#IsConfirm_Y + label")
        IsConfirm_Y.click()

        txtCaptcha = self.driver.find_element_by_xpath('//*[@id="txtCaptcha"]')
        txtCaptcha.send_keys(self.key)

        assert "No results found." not in self.driver.page_source  # Debugger

    def captcha(self):
        captcha_path = getcwd() + r"\captcha_{}.png".format(self.id)

        # Get the location of element on the page Point
        captcha = self.driver.find_element_by_id('capt')
        success = captcha.screenshot(captcha_path)
        if success is False:
            print("Captcha Capture Error!\n")

        # image process
        self.imgProc(captcha_path)

        self.key = image_to_string(captcha_path, config=self.t_config)
        self.key = sub("[^0-9]", "", self.key)  # regex substituted non digit character
        print("captcha: " + self.key)

    def imgProc(self, path):
        # image read by GRAYSCALE mode
        im = cv.imread(path, cv.IMREAD_GRAYSCALE)
        # gray -> blur -> adaptive threshold
        # gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        # blur = cv.GaussianBlur(gray, (5, 5), 0)
        # thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

        # erosion -> threshold -> dilation
        kernel = ones((3, 3), uint8)
        erosion = cv.erode(im, kernel, iterations=1)
        _, thresh = cv.threshold(erosion, 90, 255, cv.THRESH_BINARY)
        dilation = cv.dilate(thresh, kernel, iterations=1)
        cv.imwrite(path, dilation)

    def confirm_click(self):
        # c = '.btn.small.next-button.survey-page-button.user-generated.notranslate'
        # send_btn = driver.find_element_by_css_selector(c)
        try:
            send_btn = self.driver.find_element_by_css_selector('button.btn_lightBlueWrap:nth-child(2)')
            send_btn.click()
            alert = self.driver.switch_to.alert
            print("Warning!!\t" + alert.text)
            alert.accept()
            return False

        except NoAlertPresentException:
            return True
        except:
            print("Unexpected error:", sys.exc_info()[0])

    def reset_click(self):
        reset_btn = self.driver.find_element_by_css_selector('button.btn:nth-child(1)')
        reset_btn.click()
        print("Reset...\n")

        # read new captcha
        self.captcha()

    def exec_success(self):
        string = self.driver.find_element_by_xpath("//*[text()='您的員工健康回報表已成功送出，謝謝。']").text
        print(string)
        #   driver.get_screenshot_as_file(r'./' + Timestamp + '.png')
        time_stamp = strftime("%a%d%b%Y%H%M", localtime())
        self.driver.save_screenshot("screenshot" + time_stamp + ".png")

        # add timestamp
        img = cv.imread("./screenshot" + time_stamp + ".png")
        cv.putText(img, strftime("%a, %d %b %Y %H:%M:%S", localtime()), (30, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv.LINE_AA)
        cv.imwrite("./screenshot" + time_stamp + ".png", img)

        self.driver.close()


def main():
    parser = Parser()
    id_list, temperature = parser.get_config()

    filler_list = []
    for i in id_list:
        filler_list.append(Filler(i, temperature))

    for f in filler_list:
        fill(f)


def fill(f):
    # initial Filler object
    # do main task
    try:
        f.fillbox()
    except:
        print("Unexpected error:", sys.exc_info()[0])

    # if anything goes wrong... do it again!
    if f.confirm_click() is False:
        print("Error! Restart program!!\n")
        f.reset_click()
        f.fillbox()
        f.confirm_click()

    # check final execute result
    f.exec_success()


if __name__ == '__main__':
    main()
    input("Pause...")
