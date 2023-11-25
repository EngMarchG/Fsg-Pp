import time
import urllib.request
import os
import re
from random import randint
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from commands.driver_instance import create_url_headers, tab_handler
from commands.exec_path import imgList
from commands.universal import searchQuery, save_Search, continue_Search, contains_works
from ai.classifying_ai import img_classifier


def getOrderedYandexImages(
    driver, exec_path, user_search, num_pics, filters, imageOrientation):
    global image_locations, image_names, ai_mode
    image_names = imgList(mode=2)
    ai_mode = True if 0 in filters else False
    recents = True if 1 in filters else False

    image_locations = []
    link = "https://yandex.com/images/search?isize=large&"
    link = link + "text=" + user_search.replace(" ", "+").replace("_", "+")
    if imageOrientation:
        orientations = ["horizontal", "vertical", "square"]
        link += f"&iorient={orientations[imageOrientation]}"
    driver.get(link)

    WebDriverWait(driver, timeout=11).until(
        EC.presence_of_element_located((By.XPATH, '//*[@class="SerpList"]'))
    )

    driver.find_element(
        By.XPATH,
        "//*[@class='SimpleImage SimpleImage_showPlaceholderIcon SerpItem-Thumb']//a",
    ).click()

    grid_search(driver, num_pics, exec_path, user_search)

    time.sleep(20)
    driver.close()

    return image_locations


def grid_search(driver, num_pics, exec_path, user_search):
    WebDriverWait(driver, timeout=11).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(@class, 'MMGallery-Item')]")
        )
    )
    images = driver.find_elements(By.XPATH, "//*[@class='MMGallery-Container']/*")

    for image in images:
        # Navigate the webpage and filter the image link 
        try:
            if len(image_locations) >= num_pics:
                break

            driver.execute_script("arguments[0].click();", image)
            time.sleep(0.5)
            imageLink = driver.find_element(
                By.XPATH,
                '//*[@class="OpenImageButton OpenImageButton_text OpenImageButton_sizes MMViewerButtons-OpenImageSizes"]//a',
            ).get_attribute("href")

            if (imageLink.rsplit("/",1)[-1].encode("ascii", "ignore")
                .decode("ascii")) in image_names:
                print("\nImage already exists, moving to another image...")
                continue
        except:
            print("\nI ran into an error finding the image, closing the tab and moving on...")
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
            continue
        
        # Ai mode check
        try:
            if ai_mode:
                checker = ai_dl(image, exec_path, driver, user_search)
                if checker:
                    continue
        except Exception as e: # TODO: Implement proper exception handling in case of http error 404
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
            checker = ai_dl(image, exec_path, driver, user_search, site="https://yandex.com/")
        except:
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
            print("\nAI mode failed to check the image, skipping...")
            continue
        
        # Download the image
        try:
            download_image(
                exec_path=exec_path,
                driver=driver,
                image=imageLink,
                user_search=user_search,
            )
        except: # TODO: Use the same exception handling as above to try and redownload the image
            print("\nI ran into an error downloading, closing the tab and moving on...")
            time.sleep(randint(0, 1) + randint(0, 9) / 10)


def download_image(exec_path, driver, image, user_search, mode=1, site=0):
    tempDLAttr = image
    matching = re.search(r"([^/]+\.(?:jpg|jpeg|png|webp))", image.rsplit("/", 1)[-1])

    if not matching:
        tempDLAttr += ".png"
    if tempDLAttr.startswith('//'):
        tempDLAttr = 'https:' + tempDLAttr

    tempDLName = (
    re.search(r"([^/]+\.(?:jpg|jpeg|png|webp))", tempDLAttr.rsplit("/", 1)[-1])
    .group(1)
    .encode("ascii", "ignore")
    .decode("ascii"))
    
    if not mode:
        tempDLName = re.sub(r'[\\/*?:"<>|]', "", tempDLName)
    img_loc = f"./{exec_path.folder_path}/{tempDLName}"
    
    # User other site headers (to be implemented properly)
    if site:
        urllib.request.install_opener(create_url_headers(tempDLAttr, site=site))
        urllib.request.urlretrieve(tempDLAttr, img_loc)

    urllib.request.install_opener(create_url_headers(tempDLAttr))
    urllib.request.urlretrieve(tempDLAttr, img_loc)

    if mode:
        print(f"\n{tempDLAttr}")
        image_locations.append(img_loc)
        image_names.append(f"{tempDLName.split('.')[0]}")
    return img_loc


def ai_dl(image, exec_path, driver, user_search, site=""):
    checker = 0
    image_thumbnail = image.find_element(
        By.XPATH, './/*[@class="MMThumbImage-Image"]'
    ).get_attribute("style")

    # Filter url from the style attribute
    image_thumbnail = re.findall(r'url\("(.+?)"\)', image_thumbnail)[0]

    # Download the image thumbnail
    image_loc = download_image(
        exec_path=exec_path,
        driver=driver,
        image=image_thumbnail,
        user_search=user_search,
        mode=0,
        site=site
    )

    # Check if the image is good or not and delete the image
    if img_classifier(image_loc):
        print("AI Mode: I approve this image")
    else:
        print("AI Mode: Skipping this image")
        checker = 1
    os.remove(image_loc)
    return checker
