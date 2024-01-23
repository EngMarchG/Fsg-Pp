import os
import time
import asyncio
import aiohttp

from random import randint
from selenium.webdriver.common.by import By
from commands.driver_instance import tab_handler, download_file
from commands.exec_path import imgList
from commands.universal import *
from ai.classifying_ai import img_classifier

async def getOrderedZerochanImages(driver, exec_path, user_search, num_pics, num_pages, n_likes, filters, imageControl):
    global image_locations, image_names, ultimatium, ai_mode
    image_names = imgList(mode=1)
    image_locations = []

    ai_mode = 1 if filters else 0
    filters={'likes': 0 if not n_likes else n_likes}
    searchLimit={'pagecount': num_pages,'imagecount':num_pics}
    user_search = user_search.replace(" ","+").capitalize()
    link = "https://www.zerochan.net/" + user_search

    if not imageControl:
        driver.get(link)
    if imageControl:
        continue_Search(driver, link, mode=2)

    if driver.current_url == "https://www.zerochan.net/":
        print("You continued for the first time, but there was no previous search to continue from!")
        driver.get(driver.current_url + 'angry')

    
    is_valid_search(driver)
    if not contains_works(driver, '//*[@id="thumbs2"]'):
        print("No works found...")
        return []

    while len(image_locations) < num_pics*num_pages:
        await search_image(driver,exec_path,filters,searchLimit=searchLimit)
        if not valid_page(driver, ["XPATH"], ["//*[@class='pagination']//a"]) and len(image_locations) < num_pics*num_pages:
            print("Reached end of search results")
            break
    driver.quit()

    return image_locations


async def search_image(driver, exec_path, filters, searchLimit):
    filter_link = "https://www.zerochan.net/register"

    # The main image searcher
    temp_img_len = len(image_locations)
    save_Search(driver=driver, mode=2)
    contains_works(driver, '//*[@id="thumbs2"]')
    images = driver.find_elements(By.XPATH, "//*[@id='thumbs2']//li")

    for curr_iter,image in enumerate(images):
        tempImg = image.find_element(By.XPATH,".//a").get_attribute("href")
        if len(image_locations) >= searchLimit['imagecount']*searchLimit['pagecount'] or len(image_locations) - temp_img_len >= searchLimit['imagecount']:
            break
        try:
            tempDLLink = image.find_elements(By.XPATH, ".//p//a")[0].get_attribute("href")
            if tempDLLink.split(".")[-1] not in ["jpg","png","jpeg"]:
                tempDLLink = image.find_elements(By.XPATH, ".//p//a")[1].get_attribute("href")
            tempDLAttr = tempDLLink.split("/")[-1]
            counts = tempDLAttr.count(".")-1
            tempDLAttr = tempDLAttr.replace(".", " ", counts).encode("ascii", "ignore").decode("ascii")

            if tempImg == filter_link or tempDLAttr in image_names:
                print("\nImage already exists, moving to another image...")
                continue

            rand_time = randint(0,1) + randint(0,9)/10
            await asyncio.sleep(rand_time)     

            if int(image.find_element(By.XPATH, './/*[@class="fav"]').get_property("text"))>filters["likes"]:
                await download_file(tempDLLink, f"./{exec_path.folder_path}/{tempDLAttr}")
                image_locations.append(f"./{exec_path.folder_path}/{tempDLAttr}")
                image_names.append(f"{tempDLAttr}")
                print(f"\n{tempDLLink}")
                if ai_mode:
                    if img_classifier(image_locations[-1]):
                        print("AI Mode: I approve this image")
                    else:
                        os.remove(image_locations[-1])
                        image_locations.pop()
                        image_names.pop()
                        print("AI Mode: Skipping this image")
            else:
                break

        # In case of stale element or any other errors
        except Exception as e:
            if driver.window_handles[-1] != driver.window_handles[0]:
                print(f"I ran into an error, closing the tab and moving on...{e}")
                driver = tab_handler(driver=driver)
            time.sleep(randint(1,3) + randint(0,9)/10)
            continue


def is_valid_search(driver):
    try:
        titles = driver.find_element(By.XPATH, "//*[@id='children']//a").get_attribute("href")
        if titles:
            driver.get(titles)
    except:
        pass