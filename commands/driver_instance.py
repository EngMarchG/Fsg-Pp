import os
import aiohttp
import asyncio
import logging
import urllib.request
from selenium import webdriver

# Change this per your needs
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3"


async def create_driver_async(profile=0):
    """
    Creates a driver instance for selenium, with options to make it more human-like.
    Uses asyncio to make it asynchronous and create the driver in a separate thread.

    Args:
        profile (int, optional): Use a profile to keep cookies (used for pixiv). Defaults to 0.

    Returns:
        driver: A selenium driver instance.
    """
    loop = asyncio.get_event_loop()
    driver = await loop.run_in_executor(None, create_driver, profile)
    return driver


def create_driver(profile=0):
    """
    Creates a driver instance for selenium, with options to make it more human-like.

    Args:
        profile (int, optional): Use a profile to keep cookies (used for pixiv). Defaults to 0.

    Returns:
        driver: A selenium driver instance.
    """
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
    options.add_argument("--log-level=3")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--headless")

    user_data_dir = os.path.abspath(os.getcwd())+"/commands/profile"
    if profile:
        options.add_argument(f"user-data-dir={user_data_dir}")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)

    # Make it more human-like
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Not recommended to change (default waits for page to fully load)
    options.page_load_strategy = 'normal'

    # Remove logs from console
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.ERROR)

    # Create driver instance (using service is not required)
    driver = webdriver.Chrome(options=options)
    return driver


def create_url_headers(tempImg, site=0, use_urllib=False):
    """
    Creates a dictionary of headers for HTTP requests.

    Args:
        tempImg (str): The URL of the image.
        site (str, optional): used as the referrer. If not provided, the URL of the image is used.
        use_urllib (bool, optional): Whether to use urllib to build an opener with the headers. Defaults to False.

    Returns:
        dict or urllib.request.OpenerDirector: If use_urllib is False, returns a dictionary of headers.
    """
    if not site:
        site = tempImg
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'X-Requested-With': 'XMLHttpRequest',
        'Upgrade-Insecure-Requests': '1',
        'Referer': f'{site}',
        'Host': f'{tempImg.split("/")[2]}',
        'Content-Type': 'application/json; charset=UTF-8',
        'Connection': 'keep-alive',
        'user-agent': f'{USER_AGENT}'
    }
    if use_urllib:
        opener = urllib.request.build_opener()
        opener.addheaders = list(headers.items())
        return opener
    return headers


def tab_handler(driver, image=0):
    """
    Handles tab opening and closing.

    Args:
        driver (selenium.webdriver.Chrome): The webdriver instance.
        image (WebElement, optional): The image element. If provided, a new tab is opened with the image. Defaults to 0.

    Returns:
        driver: The webdriver instance.
    """
    if image:
        tempImg = image.get_attribute("href")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(f"{tempImg}")
        return driver, tempImg

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return driver


async def download_file(url, destination, headers=None, allow_redirects=False):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, allow_redirects=allow_redirects) as response:
            if response.status == 200:
                data = await response.content.read()
                content_length = response.headers.get('Content-Length')
                if content_length and len(data) != int(content_length):
                    raise Exception("Failed to download")

                with open(destination, 'wb') as fd:
                    fd.write(data)
                
            else:
                raise Exception("Failed to download")
