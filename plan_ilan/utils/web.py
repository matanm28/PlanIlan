import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

open_drivers_list = []

os.environ['WDM_LOG_LEVEL'] = '0'

def get_chrome_driver(open_window=False) -> webdriver.Chrome:
    chrome_options = Options()
    if not open_window:
        chrome_options.add_argument('--headless')
    driver_manager = ChromeDriverManager().install()
    logging.info(f'Instantiating ChromeWebDriver object {"with" if open_window else "without"} open window')
    driver = webdriver.Chrome(driver_manager, options=chrome_options)
    return driver


def close_chrome_driver(driver: webdriver.Chrome):
    driver.close()
    logging.info('Closed ChromeWebDriver')
