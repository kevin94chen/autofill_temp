from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import configparser
from time import gmtime, strftime

Timestamp = strftime("%d%b%Y%H%M%S")
url = 'http://219.87.157.3:8080/bt/Bt'


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

    v_id = driver.find_element_by_id("empId")
    v_id.send_keys(id)

    temp_meas_mthd = driver.find_element_by_xpath("//select[@name='tmpType']/option[text()='額溫(Forehead)']")
    temp_meas_mthd.click()
    #temp_meas_mthd = driver.find_element_by_id("430334644_2860832441")
    #temp_meas_mthd.send_keys(Keys.SPACE)

    temp = driver.find_element_by_id("bt")
    temp.send_keys(body_temp)


    take_med = driver.find_element_by_xpath("//select[@name='tookAntipyretics']/option[text()='否/No']")
    take_med.click()
    #take_med = driver.find_element_by_id("447437405_2965044714")
    #take_med.send_keys(Keys.SPACE)

    take_med = driver.find_element_by_xpath("//select[@name='symptoms']/option[text()='以上皆無/I do not have the above symptoms']")
    take_med.click()
    #symptom = driver.find_element_by_id("430334646_2860832447")
    #symptom.send_keys(Keys.SPACE)




    assert "No results found." not in driver.page_source  # Debugger


def confirm_click():
    confirm = driver.find_element_by_id("submit")
    confirm.click()


#    c = '.btn.small.next-button.survey-page-button.user-generated.notranslate'
#    send_btn = driver.find_element_by_css_selector(c)
#    send_btn.click()


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

#    input("press anything to continue")
    # close driver
    driver.close()
