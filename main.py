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
import LineAPI


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

    ''' 
    tesseract config: 
        --psm <page segmentation method> | --oem <OCR engine mode> | tessedit_char_whitelist | outputbase
    '''
    # t_config = '--psm 3 --oem 3 -c tessedit_char_whitelist=0123456789 outputbase digits'
    t_config = '--psm 3 --oem 3 outputbase digits'

    # Firefox headless option, optimize scrape performance
    ff_option = webdriver.FirefoxOptions()
    ff_option.headless = True
    ff_option.add_argument('--log-level=3')
    ff_option.add_argument('--disable-gpu')
    ff_option.add_argument('--disable-dev-shm-usage')

    def __init__(self, id, temp):
        print("{} filler initial...\n".format(id))
        self.key = ""
        self.id = id
        self.temperature = temp

        # initial driver
        self.driver = webdriver.Firefox(options=self.ff_option)
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
        kernel = np.ones((3, 3), dtype=np.uint8)
        # kernel = np.ones((3, 3))

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
        # string = self.driver.find_element_by_xpath("//*[text()='您的員工健康回報表已成功送出，謝謝。']").text
        string = self.driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/section/div/p[1]").text

        print(string)
        # driver.get_screenshot_as_file(r'./' + Timestamp + '.png')
        time_stamp = strftime("%a%d%b%Y%H%M", localtime())
        self.driver.save_screenshot("screenshot" + time_stamp + ".png")

        # add timestamp
        img_dir = getcwd() + "./screenshot" + time_stamp + ".png"
        img = cv.imread(img_dir)
        cv.putText(img, strftime("%a, %d %b %Y %H:%M:%S", localtime()), (30, 40),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv.LINE_AA)
        cv.imwrite(img_dir, img)

        # self.send_msg()
        self.driver.close()

    # def send_msg(self):
    #     LineAPI.send_to_line(self.id)


def main():
    parser = Parser()
    id_list, temperature = parser.get_config()

    for i in id_list:
        fill(Filler(i, temperature))

    # send message
    LineAPI.send_to_line("{}".format(pass_list))


def fill(f: Filler):
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

    try:
        # check final execute result
        f.exec_success()
        pass_list.append(f.id)
    except Exception as e:
        print("{} not execute success.\n{}".format(f.id, e))
        fail.append(f.id)


if __name__ == '__main__':
    fail = []
    pass_list = []
    main()
    print("Fail id: {}".format(fail))
    input("Pause...")
