import os
import re
import time
import urllib.request
import urllib.parse
import aiohttp

from random import randint
from selenium.webdriver.common.by import By
from commands.driver_instance import create_url_headers, download_file
from commands.exec_path import imgList
from commands.universal import contains_works, sanitize_name
from ai.classifying_ai import img_classifier


async def getOrderedYandexImages(driver, exec_path, user_search, num_pics, filters, imageOrientation):
    global image_locations, image_names, ai_mode
    image_names = imgList(mode=2)
    start_pos = 0
    ai_mode = True if 0 in filters else False
    recents = True if 1 in filters else False

    image_locations = []
    link = "https://yandex.com/images/search?isize=large&"
    link = link + "text=" + user_search.replace(" ", "+").replace("_", "+")
    if recents:
        link += "&recent=7D"
    if imageOrientation:
        orientations = ["horizontal", "vertical", "square"]
        link += f"&iorient={orientations[imageOrientation]}"
    driver.get(link)

    while len(image_locations) < num_pics:
        start_pos = await grid_search(driver, num_pics, exec_path, user_search, start_pos)
    driver.quit()

    return image_locations


async def grid_search(driver, num_pics, exec_path, user_search, start_pos):
    contains_works(driver, "//*[@class='SimpleImage SimpleImage_showPlaceholderIcon SerpItem-Thumb']//a")
    
    images = driver.find_elements(By.XPATH,"//*[@class='SimpleImage SimpleImage_showPlaceholderIcon SerpItem-Thumb']//a")
    images = images[start_pos:]

    for image in images:
        # Navigate the webpage and filter the image link 
        try:
            if len(image_locations) >= num_pics:
                break

            driver.execute_script("arguments[0].click();", image)
            contains_works(driver, '//*[@class="MMViewerButtons"]')
            imageLink = driver.find_element(
                By.XPATH,
                '//*[@class="MMViewerButtons"]//div//a',
            ).get_attribute("href")

            imageLink = re.sub(r'(\.(jpg|jpeg|png|webp)).*$', r'\1', imageLink)
            if sanitize_name(imageLink.rsplit("/",1)[-1]) in image_names:
                print("Image already exists, moving to another image...\n")
                continue
        except Exception as e:
            print(f"I ran into an error finding the image, closing the tab and moving on...\n {e}")
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
            continue
        
        # Ai mode check
        try:
            if ai_mode:
                checker = await ai_dl(image, exec_path, driver, user_search)
                if checker:
                    continue
        except Exception as e:
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
            print(f"AI mode failed to check the image, skipping...\n {e}")
            continue
        
        # Download the image
        try:
            await download_image(
                exec_path=exec_path,
                driver=driver,
                image=imageLink,
                user_search=user_search,
            )
        except Exception as e:
            print(f"I ran into an error downloading, closing the tab and moving on...\n{e}")
            time.sleep(randint(0, 1) + randint(0, 9) / 10)
    return len(images)


async def download_image(exec_path, driver, image, user_search, mode=1, site=0):
    tempDLAttr = image
    matching = re.search(r"([^/]+\.(?:jpg|jpeg|png|webp))", image.rsplit("/", 1)[-1])

    if not matching:
        tempDLAttr += ".png"
    if tempDLAttr.startswith('//'):
        tempDLAttr = 'https:' + tempDLAttr

    tempDLName = (
    re.search(r"([^/]+\.(?:jpg|jpeg|png|webp))", tempDLAttr.rsplit("/", 1)[-1])
    .group(1).encode("ascii", "ignore").decode("ascii"))
    
    if not mode:
        tempDLName = sanitize_name(tempDLName)
    img_loc = f"./{exec_path.folder_path}/{tempDLName}"
    
    # Download the image
    headers = create_url_headers(tempDLAttr, site=site)
    try:
        await download_file(tempDLAttr, img_loc, headers, allow_redirects=True)
    except Exception:
        # Try the alternative URL
        alternative_url = extract_and_decode_img_url(driver.current_url)
        headers = create_url_headers(alternative_url, site=tempDLAttr)
        tempDLAttr = alternative_url  # Update the URL for the next iteration
        await download_file(tempDLAttr, img_loc, headers, allow_redirects=True)

    if mode:
        print(f"{tempDLAttr}\n")
        image_locations.append(img_loc)
        image_names.append(f"{tempDLName.split('.')[0]}")
    return img_loc


async def ai_dl(image, exec_path, driver, user_search, site=""):
    checker = 0
    image_thumbnail = image.find_element(By.XPATH, './/img').get_attribute("src")

    # Download the image thumbnail
    image_loc = await download_image(
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
        print("AI Mode: Skipping this image\n")
        checker = 1
    os.remove(image_loc)
    return checker


def extract_and_decode_img_url(url):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    img_url_encoded = query_params.get('img_url', [None])[0]
    if img_url_encoded is not None:
        img_url_decoded = urllib.parse.unquote(img_url_encoded)
        return img_url_decoded
    else:
        return None
