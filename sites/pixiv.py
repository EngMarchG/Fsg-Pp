import sys
sys.path.append("..")

import time
import urllib.request
import os
import re
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import date, datetime
from random import randint
from commands.driver_instance import create_url_headers, tab_handler
from commands.exec_path import imgList
from commands.universal import searchQuery, save_Search, continue_Search, contains_works
from ai.classifying_ai import img_classifier


def getOrderedPixivImages(driver,exec_path,user_search,num_pics,num_pages,searchTypes,viewRestriction,imageControl,
                          n_likes,n_bookmarks,n_views, start_date=0,end_date=0, user_name=0, pass_word=0):
    global image_locations, image_names, ultimatium, ai_mode, prev_search
    image_names = imgList(mode=1)
    image_locations = []
    prev_search = 0
    link = "https://www.pixiv.net/tags/illustration"
    success_login = False

    filters = {
        "likes": 0 if not n_likes else n_likes,
        "bookmarks": 0 if not n_bookmarks else n_bookmarks,
        "viewcount": 0 if not n_views else n_views,
    }
    searchLimit = {"pagecount": num_pages, "imagecount": num_pics}

    start_date = start_date if date_handler(start_date) else ""
    end_date = date.today() if not date_handler(end_date) else end_date

    if 1 in imageControl:
        continue_Search(driver, link, mode=0)
    else:
        driver.get(link)

    # Will use those when not logged in
    bar_search = '//input[@placeholder="Search works"]'
    li_search = "//h3[contains(text(), 'Works') or contains(text(), 'Illustrations and Manga') or contains(text(), 'Illustrations')]/ancestor::section[1]/div[2]//li"
    premium_search = "//h3[contains(text(), 'Popular works')]/ancestor::section[1]/div[2]//li"
    search_param = {
        "bar_search": bar_search,
        "li_search": li_search,
        "premium_search": premium_search,
    }

    # Check if logged in otherwise log in with credentials
    try:
        # Explicit wait to check for favorite button (only appears for logged in users)
        WebDriverWait(driver, timeout=6).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add to your favorites')]")))
        
        if driver.find_elements(By.XPATH, "//button[contains(text(), 'Add to your favorites')]"):
            success_login = True

        elif user_name and pass_word:
            print("Logging in...")
            if login_handler(driver, exec_path, user_name, pass_word):
                success_login = True

        if not success_login:
            print("Failed! You are not logged in...")

    except:
        print("Failed! You are not logged in...")
        pass
    
    if 1 not in imageControl:
        searchQuery(user_search, driver, search_param["bar_search"], isLoggedIn=success_login)
    time.sleep(2)

    if start_date and not success_login:
        driver.get(driver.current_url + f"?scd={start_date}&ecd={end_date}")
        time.sleep(2)
    elif start_date and success_login:
        cur_url = driver.current_url.split("?")
        driver.get(cur_url[0] + f"?scd={start_date}&ecd={end_date}&" + cur_url[1])
        time.sleep(2)

    premiumSearch = 1 if 0 in searchTypes else 0
    freemiumSearch = 1 if 1 in searchTypes else 0
    pg_friendly = 1 if 0 in viewRestriction else 0
    r_18 = 1 if 1 in viewRestriction else 0
    ultimatium = 1 if 0 in imageControl else 0
    order_by_oldest = 1 if 2 in imageControl else 0
    ai_mode = 1 if 3 in imageControl else 0

    if not contains_works(driver, search_param["li_search"]):
        print("No works found...")
        return []
    
    if premiumSearch == 1:
        search_image(driver, exec_path, filters, search_param)

    # Switch to english
    try:
        english_span = driver.find_element(By.XPATH, "//span[contains(text(), 'English')]")
        driver.execute_script("arguments[0].click();", english_span)
    except:
        pass

    # Apply filters if logged in
    if success_login:
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div[5]/nav/a[2]").click()
            print("Illustrations only")
            time.sleep(1)

            mode = ""
            order = ""

            if pg_friendly == 1 and r_18 == 1:
                print("PG Friendly and r-18")
            elif pg_friendly == 1:
                mode = "mode=safe&"
                print("PG Friendly")
            elif r_18 == 1:
                mode = "mode=r18&"
                print("r-18")
            if order_by_oldest == 1:
                order = "order=date&"
                print("Order by oldest")

            cur_url = driver.current_url.split("?")
            driver.get(cur_url[0] + f"?{order}{mode}" + cur_url[1])
        except:
            pass
    
    # Click show all results
    try:
        time.sleep(1)
        show_all_div = driver.find_element(By.XPATH, "//div[contains(text(), 'Show all')]")
        if show_all_div:
            driver.find_element(By.XPATH, '//*[@class="sc-d98f2c-0 sc-s46o24-1 dAXqaU"]').click()
    except:
        pass
    
    prev_search = len(image_locations)
    curr_page = driver.current_url

    if freemiumSearch:
        while len(image_locations) < num_pics*num_pages:
            search_image(driver,exec_path,filters,search_param=search_param,searchLimit=searchLimit)
            if not valid_page(driver) and len(image_locations) < num_pics*num_pages:
                print("Reached end of search results")
                break
    driver.quit()

    return image_locations


def search_image(driver,exec_path,filters,search_param,searchLimit={"pagecount": 1, "imagecount": 99}):
    # Searches using premium or freemium
    search_type = awaitPageLoad(driver=driver,searchLimit=searchLimit,search_param=search_param)
    if search_type == -1:
        return
    
    # The main image searcher
    for page in range(searchLimit["pagecount"]):
        
        temp_img_len = len(image_locations)
        WebDriverWait(driver, timeout=9).until(
            EC.presence_of_element_located(
                (By.XPATH, search_param["li_search"] + "//a")))  
        images = search_image_type(search_type, driver, search_param=search_param)

        for image in images:
            if len(image_locations) - prev_search >= searchLimit["imagecount"]*searchLimit["pagecount"] or len(image_locations) - temp_img_len >= searchLimit["imagecount"]:
                break
            image = image.find_element(By.XPATH, "." + "/" + "/a")
            imageLink = image.find_elements(By.XPATH, ".//img")

            if image.get_attribute("href").rsplit("/", 1)[-1] not in image_names:
                checker = 0
                if ai_mode == 1:
                    try:
                        # Dl the image thumbnail from the grid
                        img_loc = thumbnailDownloader(imageLink=imageLink, image=image, driver=driver, exec_path=exec_path, mode=0)

                        if img_classifier(img_loc):
                            print("AI Mode: I approve this image")
                        else:
                            print("AI Mode: Skipping this image")
                            checker = 1
                        os.remove(img_loc)
                    except:
                        checker = 1
                if checker:
                    continue

                try:
                    if sum(filters.values()) == 0 and len(imageLink): # Dl the image directly from the grid
                        thumbnailDownloader(imageLink=imageLink, image=image, driver=driver, exec_path=exec_path)
                    
                    else: # Dl the image from the image page (opens a new tab)
                        driver, tempImg = tab_handler(driver=driver, image=image)
                        WebDriverWait(driver, timeout=11).until(EC.presence_of_element_located((By.XPATH, "//div[@role='presentation']")))
                        tempDL = driver.find_element(By.XPATH, "//div[@role='presentation']//img")

                        fetchImageData = driver.find_elements(By.TAG_NAME, "dd")
                        imagePopularity = parseImageData(
                            filters=filters, Data=fetchImageData)
                        time.sleep(1)

                        if filterOptions(filters, imagePopularity=imagePopularity): # Check if image filters are satisfied
                            tempDLLink = tempDL.get_attribute("src")

                            # Dl the original rez image
                            if ultimatium:
                                tempDLLink = tempDLLink.replace(
                                    "img-master", "img-original"
                                ).replace("_master1200", "")

                            download_image(imageLink=tempDLLink, exec_path=exec_path, driver=driver)
                        else:
                            print("\nImage filters not satisfied...")
                        driver = tab_handler(driver=driver)
                        time.sleep(0.3)

                # In case of stale element or any other errors
                except:
                    if driver.window_handles[-1] != driver.window_handles[0]:
                        print("\nI ran into an error, moving on...")
                        driver = tab_handler(driver=driver)
                    time.sleep(randint(1, 3) + randint(0, 9) / 10)
                    continue

            else:
                print("\nImage already exists, moving to another image...")
            save_Search(driver, mode=0)
        if not valid_page(driver):
            break


######## FUNCTIONS PRONE TO CHANGE ########
def login_handler(driver, exec_path, user_name, pass_word):
    time.sleep(5)
    login_btn = driver.find_elements(By.XPATH, "//*[@class='sc-oh3a2p-4 gHKmNu']//a")[1]
    login_btn.click()

    WebDriverWait(driver, timeout=11).until(
        EC.presence_of_element_located((By.XPATH, "//*[@class='sc-2o1uwj-0 elngKN']"))
    )
    user_btn = driver.find_element(
        By.XPATH, "//*[@class='sc-2o1uwj-0 elngKN']"
    ).find_elements(By.TAG_NAME, "fieldset")
    user_btn[0]

    actions = ActionChains(driver)
    actions.click(user_btn[0]).send_keys(user_name).perform()
    time.sleep(0.5)
    actions.click(user_btn[1]).send_keys(pass_word).perform()

    # Log in button
    driver.find_element(By.XPATH,"//button[contains(text(), 'Log In')]").click()

    return True


def download_image(imageLink, exec_path, driver, mode=1):
    tempDLName = imageLink.rsplit("/", 1)[-1]
    img_loc = f"./{exec_path.folder_path}/{tempDLName}"
    if not ultimatium or not mode:
        installUrlOpeners(driver=driver,mode=0)
    else:
        installUrlOpeners(imageLink)
    try:
        requestUrlretrieve(imageLink=imageLink, img_loc=img_loc)
    except:
        imageLink = imageLink.rsplit(".",1)[0]+".png"
        requestUrlretrieve(imageLink, img_loc=img_loc)
    
    print(f"\n{imageLink}")
    if mode:
        image_locations.append(f"./{exec_path.folder_path}/{tempDLName}")
        image_names.append(f"{tempDLName.split('.')[0]}")
    else:
        return img_loc


def thumbnailDownloader(imageLink, image, driver, exec_path, mode=1):
    imageLink = image_type(imageLink=imageLink, mode=mode)

    action = ActionChains(driver=driver)
    action.move_to_element(image.find_element(By.XPATH, ".//img")).perform()

    return download_image(imageLink=imageLink, exec_path=exec_path, driver=driver, mode=mode)


######## URLLIB LIBRARY ########
def installUrlOpeners(driver,mode=1): # Mode 0 means its a thumbnail
    if ultimatium and mode:
        urllib.request.install_opener(create_url_headers(driver))
    else:
        urllib.request.install_opener(create_url_headers(driver.current_url))

def requestUrlretrieve(imageLink, img_loc): # Download the image
    urllib.request.urlretrieve(imageLink, img_loc)


######## HELPER FUNCTIONS (UNLIKELY TO CHANGE) ########
# Handles the search type (premium or freemium)
def search_image_type(search_type, driver, search_param):
    if search_type == 0:
        return driver.find_elements(By.XPATH, search_param["premium_search"])
    elif search_type == 1:
        return driver.find_elements(By.XPATH, search_param["li_search"])


# Handles the image type (if mode then it is not a thumbnail, so switch it to view res else Max res)
def image_type(imageLink, mode=0):
    imageLink = imageLink[0].get_attribute("src")
    if mode: # View res
        imageLink = re.sub(r"c/.*?/.*?/", "img-master/", imageLink)
        imageLink = imageLink.replace("square", "master").replace("custom", "master")

        if ultimatium: # Max res
            imageLink = imageLink.replace("img-master", "img-original").replace("_master1200", "")
    return imageLink


# Handles finding the popular or freemium section
def awaitPageLoad(driver, searchLimit, search_param, search_type=0):
    # Waits on the page to load (for popular or freemium)
    if searchLimit["imagecount"] == 99:
        try:
            WebDriverWait(driver, timeout=12).until(
                EC.presence_of_element_located(
                    (By.XPATH, search_param["premium_search"])
                )
            )
            print("Premium section found, searching for images...")
        except:
            print("No popular section")
            search_type = -1
            return search_type
    else:
        try:
            WebDriverWait(driver, timeout=12).until(
                EC.presence_of_element_located((By.XPATH, search_param["li_search"]))
            )
            print("\nFreemium section found, searching for images...")
        except:
            driver.refresh()
            time.sleep(12)
        if not driver.find_elements(By.XPATH, search_param["li_search"]):
            return
        search_type = 1
    return search_type


def filterOptions(filters, imagePopularity):
    for key in filters.keys():
        if filters[key] > imagePopularity[key]:
            return False
    return True


def parseImageData(Data, filters):
    parsedData = {}
    for iter, key in enumerate(filters.keys()):
        parsedData[key] = int(Data[iter].text.replace(",", ""))
    return parsedData


def valid_page(driver):
    cur_url = driver.current_url
    try:
        next_page = (
            driver.find_element(By.XPATH, '//*[@class="sc-xhhh7v-0 kYtoqc"]')
            .find_elements(By.XPATH, ".//a")[-1]
            .get_attribute("href")
        )
        if cur_url == next_page:
            return 0
        if next_page:
            driver.get(next_page)
        return 1
    except:
        return 0


def date_handler(sel_date):
    temp = sel_date.split("-")
    try:
        datetime(int(temp[0]), int(temp[1]), int(temp[2]))
    except ValueError:
        return 0
    return 1