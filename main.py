import sys
import numpy as np

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from configparser import ConfigParser
from time import localtime, strftime
from pytesseract import image_to_string
from re import sub
from os import getcwd
import cv2 as cv


class Filler:
    url = 'https://www.nanya.com/tw/Page/115/%e5%93%a1%e5%b7%a5%e5%81%a5%e5%ba%b7%e5%9b%9e%e5%a0%b1%e8%a1%a8'
    driver = webdriver.Firefox()
    id = ""
    temperature = ""
    t_config = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789'
    key = ""

    def __init__(self):
        self._read_config()
        # initial driver
        self.driver.get(self.url)
        self.captcha()

    def _read_config(self):
        config = ConfigParser()
        config.read('info.ini')

        self.id = config['default']['ID']
        self.temperature = config['default']['tempature']
        if self.temperature == "":
            self.temperature = "36.0"
            print("body temperature is set 36.0")
        # return i, temperature

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

        txtCaptcha = Filler.driver.find_element_by_xpath('//*[@id="txtCaptcha"]')
        txtCaptcha.send_keys(sub("[^0-9]", "", self.key))

        assert "No results found." not in self.driver.page_source  # Debugger

    def captcha(self):
        captcha_path = getcwd() + r"\captcha.png"

        # Get the location of element on the page Point
        captcha = self.driver.find_element_by_id('capt')
        success = captcha.screenshot(captcha_path)
        if success is False:
            print("captcha Capture Error!\n")

        # image process
        self.imgProc(captcha_path)

        self.key = image_to_string(captcha_path, config=self.t_config)
        print("captcha:" + self.key)

    def imgProc(self, path):
        # image read by GRAYSCALE mode
        im = cv.imread(path, cv.IMREAD_GRAYSCALE)
        # gray -> blur -> adaptive threshold
        # gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        # blur = cv.GaussianBlur(gray, (5, 5), 0)
        # thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)

        # erosion -> threshold -> dilation
        kernel = np.ones((3, 3), np.uint8)
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
    # initial Filler object
    filler = Filler()

    # do main task
    try:
        filler.fillbox()
    except:
        print("Unexpected error:", sys.exc_info()[0])

    # if anything goes wrong... do it again!
    if filler.confirm_click() is False:
        print("\nError! Restart program!!\n")
        filler.reset_click()
        filler.fillbox()
        filler.confirm_click()

    # check final execute result
    filler.exec_success()



if __name__ == '__main__':
    main()
    input("Press Any Key To Exit...")
