import errno
import re
import sys
import time

from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from configparser import ConfigParser
from time import gmtime, strftime
from pytesseract import image_to_string
from re import sub
from os import getcwd
from os import execv
import cv2 as cv

# Timestamp = strftime("%d%b%Y%H%M%S")
url = 'https://www.nanya.com/tw/Page/115/%e5%93%a1%e5%b7%a5%e5%81%a5%e5%ba%b7%e5%9b%9e%e5%a0%b1%e8%a1%a8'
t_config = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789'


def _read_config():
    config = ConfigParser()
    config.read('info.ini')

    i = config['default']['ID']
    t = config['default']['tempature']
    if t == "":
        t = "36.0"
        print("body temperature is set 36.0")
    return i, t


def main(id, body_temp):
    Is_Agree = driver.find_element_by_css_selector("input#IsAgree_Y + label")
    Is_Agree.click()

    Emp_ID = driver.find_element_by_name("Emp_ID")
    Emp_ID.send_keys(id)

    Meas_Method = driver.find_element_by_css_selector("input#Meas_Method_Ear + label")
    Meas_Method.click()

    Temperature = driver.find_element_by_name("Temperature")
    Temperature.send_keys(body_temp)

    Take_AntFvrMed_N = driver.find_element_by_css_selector("input#Take_AntFvrMed_N + label")
    Take_AntFvrMed_N.click()

    IsHighRisk_N = driver.find_element_by_css_selector("input#IsHighRisk_N + label")
    IsHighRisk_N.click()
    IsPas7DMedCare_N = driver.find_element_by_css_selector("input#IsPas7DMedCare_N + label")
    IsPas7DMedCare_N.click()
    IsPas14DTest_None = driver.find_element_by_css_selector("input#IsPas14DTest_None + label")
    IsPas14DTest_None.click()

    IsPas14DTest_None = driver.find_element_by_css_selector("input#IsPas14DTest_None + label")
    IsPas14DTest_None.click()
    # Agree_RapidTest_Y = driver.find_element_by_css_selector('input#Agree_RapidTest_Y + label')
    # Agree_RapidTest_Y.click()
    IsConfirm_Y = driver.find_element_by_css_selector("input#IsConfirm_Y + label")
    IsConfirm_Y.click()

    assert "No results found." not in driver.page_source  # Debugger


def captcha(driver):
    path = getcwd() + '\captcha.png'

    # Get the location of element on the page Point
    captcha = driver.find_element_by_id('capt')
    success = captcha.screenshot(path)

    key = image_to_string(path, config=t_config)
    txtCaptcha = driver.find_element_by_xpath('//*[@id="txtCaptcha"]')
    txtCaptcha.send_keys(sub("[^0-9]", "", key))
    print("captcha:" + key)


def confirm_click():
    # c = '.btn.small.next-button.survey-page-button.user-generated.notranslate'
    # send_btn = driver.find_element_by_css_selector(c)
    try:
        send_btn = driver.find_element_by_css_selector('button.btn_lightBlueWrap:nth-child(2)')
        send_btn.click()
        alert = driver.switch_to.alert
        print("Warning!Input Value Error!\t" + alert.text )
        alert.accept()
        reset_click()
        return False

        # input("Press Any Key To Exit...")
        # sys.exit(1)
    except NoAlertPresentException:
        return True
    except:
        print("Unexpected error:", sys.exc_info()[0])
        # input("Press Any Key To Exit...")
        # sys.exit(1)


def reset_click():
    reset_btn = driver.find_element_by_css_selector('button.btn:nth-child(1)')
    reset_btn.click()
    print("Reset...\n")


def add_timestamp():
    img = cv.imread("./screenshot.png")
    cv.putText(img, strftime("%a, %d %b %Y %H:%M:%S", gmtime()), (30, 40),
               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv.LINE_AA)
    cv.imwrite("./screenshot.png", img)


if __name__ == '__main__':
    # Read config
    id, t = _read_config()

    # iniatial driver
    driver = webdriver.Firefox()
    driver.get(url)

    # do main task
    try:
        main(id, t)
        captcha(driver)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        input("Pause...")

    if confirm_click() is False:
        print("\nError! Restart program!!\n")
        main(id, t)
        captcha(driver)
        confirm_click()

    string = driver.find_element_by_xpath("//*[text()='您的員工健康回報表已成功送出，謝謝。']").text
    print(string)

    #   driver.get_screenshot_as_file(r'./' + Timestamp + '.png')
    driver.save_screenshot("screenshot.png")
    add_timestamp()

    #   input("press anything to continue")
    # close driver
    driver.close()
    input("Press Any Key To Exit...")
