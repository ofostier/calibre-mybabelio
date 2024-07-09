import sys
sys.path.append('/usr/local/lib/python3.10/dist-packages')
from selenium  import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

timeout = 10

#global driver
selenium_grid_url = '172.17.0.3:4444'
def selenium_connect():

    print("SELENIUM GRID Test Execution Started")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Remote(
    command_executor='http://'+selenium_grid_url+'/wd/hub',
    options=options
    )
    #maximize the window size
    driver.maximize_window()
    time.sleep(10)
    #navigate to browserstack.com
    driver.get("https://www.babelio.com/")
    time.sleep(5)
    print(driver.title)

    try:
        fuck_cookie_box = driver.find_element(By.CLASS_NAME, "button__acceptAll") #"Continue without accepting")
        fuck_cookie_box.click()
    except Exception as e:
        print("PAS DE BOUTON COOKIE ACCEPT")

    return driver

def selenium_find(driver, query):
    searchbox = driver.find_element(By.ID, "searchbox")
    #searchbox.send_keys('Chloe Wilkox ordonne moi volume 3')
    
    searchbox.send_keys(query)

    # for request in driver.requests:
    #     if request.response:
    #         print(
    #             request.url,
    #             request.response.status_code,
    #             request.response.headers['Content-Type'],
    #             request.response.body,
    #         )

    time.sleep(2)
    
    result_box = driver.find_element(By.CLASS_NAME,"ui-autocomplete")
    search_result = result_box.get_attribute('outerHTML') #'innerHTML')

    #nb link found
    try:
        nb_link = (driver.findElements(By.CLASS_NAME, "ui-corner-all"))
        print("NB LINK FOUND: ", nb_link)
        #print(search_result)
    except:
        selenium_close(driver)

    return search_result
    #time.sleep(5)

#close the browser
def selenium_close(driver):
    driver.close()
    driver.quit()
    print("Test Execution Successfully Completed!")

def log_filter(log_):
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        and "json" in log_["params"]["response"]["mimeType"]
    )

# driver = selenium_connect()
# result = selenium_find(driver, 'Chloe Wilkox ordonne moi volume 2')
# print(result)
# selenium_close(driver)