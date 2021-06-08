import pytesseract
import re


def captcha(driver):
    path = r"D:/autofill_temp/captcha.png"

    # Get the location of element on the page Point
    captcha = driver.find_element_by_id('capt')
    success = captcha.screenshot(path)

    key = pytesseract.image_to_string(path)
    txtCaptcha = driver.find_element_by_xpath('//*[@id="txtCaptcha"]')
    txtCaptcha.send_keys(re.sub("[^0-9]", "", key))
