import sys
sys.path.append('/usr/local/lib/python3.10/dist-packages')

from selenium  import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions
#from selenium.webdriver.chrome import service
#from webdriver_manager.chrome import ChromeDriverManager

import time
import json

timeout = 10

#global driver
#selenium_grid_url = '172.17.0.3:4444'
GRID_HOST = '192.168.1.131:4444'
def selenium_connect() -> WebDriver:

    print("SELENIUM GRID Test Execution Started")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('w3c', True)
    # Try to catch XHR response
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL"}
    )
    
    # webdriver_service = service.Service(ChromeDriverManager().install())
    # webdriver_service.start()

    driver = webdriver.Remote(
    #webdriver_service.service_url,
    command_executor='http://'+GRID_HOST+'/wd/hub',
    options=options,
    )
    
    #maximize the window size
    driver.maximize_window()
    
    #navigate to babelio.com
    driver.get("https://www.babelio.com/")
    print(driver.title)
    time.sleep(5)

    try:
        fuck_cookie_box = driver.find_element(By.CLASS_NAME, "button__acceptAll") #"Continue without accepting")
        fuck_cookie_box.click()
    except Exception as e:
        print("PAS DE BOUTON COOKIE ACCEPT")

    return driver

def selenium_find(driver, query):
    print("Saisie dans la searchbox")
    searchbox = driver.find_element(By.ID, "searchbox")
    #searchbox.send_keys('Chloe Wilkox ordonne moi volume 3')
    
    searchbox.clear()
    searchbox.send_keys(query)

    sleep_pause(2)
    
    # result_box = driver.find_element(By.CLASS_NAME,"ui-autocomplete")
    # search_result = result_box.get_attribute('outerHTML') #'innerHTML')

    #nb link found
    try:
        #driver.waitForElementPresent("ui-menu-item")
        nb_link = driver.find_elements(By.CLASS_NAME, "ui-menu-item") #"ui-corner-all"))
        #/html/body/ul/li/a
        #print("NB LINK FOUND: ", nb_link.size())
        print("NB LINK FOUND: ", str(len(nb_link)))
        #print(search_result)
        
        #sleep_pause(5)
        founded = False
        fcount = 0
        # Sleep added because sometime response appears later
        while founded == False and fcount < 60:
                
            fcount += 1
            logs_raw = driver.get_log("performance")
            
            requests = [json.loads(lr["message"])["message"] for lr in logs_raw]
            log_write("log.json", str(requests))
            print("LOG  - Done")

            for log in filter(log_filter, requests):
                request_id = log["params"]["requestId"]
                log_write("log1.json", str(request_id),"a")
                resp_url = log["params"]["response"]["url"]
                #print(f"Caught {resp_url}")
                log_write("log2.json", str(resp_url)+'\n','a')
                if 'aj_recherche' in resp_url:
                    founded = True
                    print("AJ_RECHERCHE FOUNDED !!! in : " + str(fcount))
                    #response = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                    response = get_browser_request_body(driver, request_id)
                    log_write("log3.json", str(response)+"\n",'a')

            sleep_pause(2)

    except Exception as e:
        selenium_close(driver)
        print(e)
        exit("NB LINK ERROR")

    return response
    #time.sleep(5)

def get_browser_request_body(driver: WebDriver, request_id: str) -> str:

    # Retrieve the response body
    print("In get_browser_request_body")
    try:
        browser_response = driver.execute(
            driver_command="executeCdpCommand",
            params={
                "cmd": "Network.getResponseBody",
                "params": {"requestId": request_id},
            },
        )
    except:
        print('Error pour retrouver le XHR')
        return None
    return browser_response["value"]["body"].split("\n")[-1]

#close the browser
def selenium_close(driver):
    driver.close()
    driver.quit()
    print("Test Execution Successfully Completed!")

def log_filter(log_):
    #print("Try to filter")
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        #and "json" in log_["params"]["response"]["mimeType"]
    )

def log_write(filename, content, method='w'):
    f = open("/code/"+filename, method)
    f.write(content)
    f.close()

def sleep_pause(seconds):
    x=1
    while x <= seconds:
        time.sleep(1)
        #print("Sleep: ", i)
        sys.stdout.write("Sleep: %d%%  \r" % (x) )
        sys.stdout.flush()
        x+=1

# driver = selenium_connect()
# result = selenium_find(driver, 'Chloe Wilkox ordonne moi volume 2')
# print(result)
# selenium_close(driver)