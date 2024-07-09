# Complete solution to catch XHR Response was found here
# https://stackoverflow.com/questions/72121479/cdp-with-remote-webdriver-webdriver-object-has-no-attribute-execute-cdp-cmd
# Thanks to @Borys Oliinyk

import json
import time
import logging
import sys
sys.path.append('/usr/local/lib/python3.10/dist-packages')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_browser() -> WebDriver:
    chrome_options = Options()
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_experimental_option(
    #     "prefs",
    #     {
    #         "intl.accept_languages": "en,en_US",
    #         "profile.managed_default_content_settings.images": 2,
    #     },
    # )
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # chrome_options.set_capability("browserVersion", "latest")
    # chrome_options.set_capability(
    #     "selenoid:options", {"enableVNC": True, "enableVideo": False}
    # )

    return webdriver.Remote(
        command_executor="http://192.168.1.131:4444",
        options=chrome_options,
    )


def get_browser_request_body(driver: WebDriver, request_id: str) -> str:
    browser_response = driver.execute(
        driver_command="executeCdpCommand",
        params={
            "cmd": "Network.getResponseBody",
            "params": {"requestId": request_id},
        },
    )
    return browser_response["value"]["body"].split("\n")[-1]


def get_browser_performance_logs(driver: WebDriver) -> list[dict]:
    browser_response = driver.execute(
        driver_command="getLog", params={"type": "performance"}
    )
    return browser_response["value"]


def intercept_json_by_url_part(driver: WebDriver, url_part: str) -> str | None:
    performance_logs = get_browser_performance_logs(driver=driver)

    for log in performance_logs:
        message = log["message"]

        if "Network.response" not in log["message"]:
            continue

        params = json.loads(message)["message"].get("params")
        response = params.get("response") if params else None

        if response and url_part in response["url"]:
            logger.info(f"Found required url part in url: {response['url']}")
            return get_browser_request_body(
                driver=driver, request_id=params["requestId"]
            )


def main() -> None:
    driver = prepare_browser()
    driver.maximize_window()

    print("Browser is ok!")
    #driver.get("https://demo.realworld.io")
    driver.get("https://www.babelio.com/")

    searchbox = driver.find_element(By.ID, "searchbox")
    #searchbox.send_keys('Chloe Wilkox ordonne moi volume 3')
    
    searchbox.send_keys("Chloe Wilkox ordonne moi volume 2")

    time.sleep(60)

    response = intercept_json_by_url_part(driver=driver, url_part="aj_recherche")
    print(response)

    """
    Response:
    {"tags":["est","enim","ipsum","repellat","exercitationem","eos","quia","tenetur","facilis","consequatur"]}
    """
    time.sleep(30)

    driver.close()
    driver.quit()
    print("Test Execution Successfully Completed!")


if __name__ == "__main__":
    main()
