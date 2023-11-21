from selenium import webdriver
import urllib.request
import os
import logging

def create_driver(profile=0):
    # Options to make it more human-like
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    options.add_argument("--log-level=3")


    user_data_dir = os.path.abspath(os.getcwd())+"/commands/profile"
    if profile:
        options.add_argument(f"user-data-dir={user_data_dir}")
    prefs = {"credentials_enable_service": False,
     "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    # to supress the error messages/logs?
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #  options.page_load_strategy = 'normal' #eager #none #normal

    # Remove logs from console
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.ERROR)

    driver = webdriver.Chrome(options=options)
    return driver

def create_url_headers(tempImg):
    opener = urllib.request.build_opener()
    opener.addheaders = [
            ('Accept', 'application/json, text/javascript, */*; q=0.01'),
            ('X-Requested-With', 'XMLHttpRequest'),
            ('Referer', f'{tempImg}'),
            ('Host', f'https//{tempImg.split("/")[2]}'),
            ('Content-Type', 'application/json; charset=UTF-8'),
            ('Connection', 'keep-alive'),
            ('user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
        ]
    return opener

def tab_handler(driver, image=0):
    if image:
        tempImg = image.get_attribute("href")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f"{tempImg}")
        return driver, tempImg

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return driver