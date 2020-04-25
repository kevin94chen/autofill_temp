from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import configparser
from time import gmtime, strftime

Timestamp = strftime("%d%b%Y%H%M%S")
url = 'https://zh.surveymonkey.com/r/EmployeeHealthCheck?fbclid=IwAR1gE86MoL4RoPFxpyigUXuV2HIHfoY9epKwmAqrrIMYl8O_s6Z3O09qqmo'


def _read_config():
    config = configparser.ConfigParser()
    config.read('info.ini')

    i = config['default']['tsmcID']
    t = config['default']['tempature']
    if t == "":
        t = "36"
        print("body temperature is set 36.")
    return i, t


def main(id, body_temp):
    radio_btn_agree = driver.find_element_by_id("430334642_2860832437")
    radio_btn_agree.send_keys(Keys.SPACE)
    tsmc_id = driver.find_element_by_id("430334639")
    tsmc_id.send_keys(id)
    temp_meas_mthd = driver.find_element_by_id("430334644_2860832441")
    temp_meas_mthd.send_keys(Keys.SPACE)
    temp = driver.find_element_by_id("430334640")
    temp.send_keys(body_temp)
    symptom = driver.find_element_by_id("430334646_2860832447")
    symptom.send_keys(Keys.SPACE)
    confirm = driver.find_element_by_id("430334641_2860832427")
    confirm.send_keys(Keys.SPACE)
    take_med = driver.find_element_by_id("447437405_2965044714")
    take_med.send_keys(Keys.SPACE)

    assert "No results found." not in driver.page_source  # Debugger


def confirm_click():
    c = '.btn.small.next-button.survey-page-button.user-generated.notranslate'
    send_btn = driver.find_element_by_css_selector(c)
    send_btn.click()


if __name__ == '__main__':
    # Read config
    id, t = _read_config()

    # iniatial driver
    driver = webdriver.Firefox()
    driver.get(url)

    # do main task
    main(id, t)
    confirm_click()

#   driver.get_screenshot_as_file(r'./' + Timestamp + '.png')

#   input("press anything to continue")
    # close driver
    driver.close()
