from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
import configparser
from time import gmtime, strftime
import pytesseract
import re

Timestamp = strftime("%d%b%Y%H%M%S")
url = 'https://www.nanya.com/tw/Page/115/%e5%93%a1%e5%b7%a5%e5%81%a5%e5%ba%b7%e5%9b%9e%e5%a0%b1%e8%a1%a8'


def _read_config():
    config = configparser.ConfigParser()
    config.read('info.ini')

    i = config['default']['ID']
    t = config['default']['tempature']
    if t == "":
        t = "36"
        print("body temperature is set 36.")
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
    IsConfirm_Y = driver.find_element_by_css_selector("input#IsConfirm_Y + label")
    IsConfirm_Y.click()

    assert "No results found." not in driver.page_source  # Debugger


def confirm_click():
    # c = '.btn.small.next-button.survey-page-button.user-generated.notranslate'
    # send_btn = driver.find_element_by_css_selector(c)
    send_btn = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/section/div/form/div/div[11]/button[2]')
    send_btn.click()


def captcha(driver):
    path = r"D:/autofill_temp/captcha.png"

    # Get the location of element on the page Point
    captcha = driver.find_element_by_id('capt')
    success = captcha.screenshot(path)

    key = pytesseract.image_to_string(path)
    txtCaptcha = driver.find_element_by_xpath('//*[@id="txtCaptcha"]')
    txtCaptcha.send_keys(re.sub("[^0-9]", "", key))


if __name__ == '__main__':
    # Read config
    id, t = _read_config()

    # iniatial driver
    driver = webdriver.Firefox()
    driver.get(url)

    # do main task
    main(id, t)
    captcha(driver)
    confirm_click()

    #   driver.get_screenshot_as_file(r'./' + Timestamp + '.png')

    #   input("press anything to continue")
    # close driver
    driver.close()
