import os
import re
import sys
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from random import randint
from datetime import date, datetime
from commands.driver_instance import create_url_headers, tab_handler, download_file
from commands.exec_path import imgList
from commands.universal import *
from ai.classifying_ai import img_classifier

sys.path.append("..")

async def getOrderedPixivImages(driver,exec_path,user_search,num_pics,num_pages,searchTypes,viewRestriction,imageControl,
                          n_likes,n_bookmarks,n_views, start_date=0,end_date=0, user_name=0, pass_word=0):
    global image_locations, image_names, ultimatium, ai_mode, prev_search
    image_names = imgList(mode=1)
    image_locations = []
    prev_search = 0
    link = "https://www.pixiv.net/tags/illustration"
    success_login = False
    is_search_continued = 0

    filters = {
        "likes": 0 if not n_likes else n_likes,
        "bookmarks": 0 if not n_bookmarks else n_bookmarks,
        "viewcount": 0 if not n_views else n_views,
    }
    searchLimit = {"pagecount": num_pages, "imagecount": num_pics}

    start_date = start_date if date_handler(start_date) else ""
    end_date = date.today() if not date_handler(end_date) else end_date

    if 1 in imageControl:
        is_search_continued = continue_Search(driver, link, mode=0)
    else:
        driver.get(link)

    # Will use those when not logged in
    search_param = {
        "bar_search": generate_xpath_query("//input", "@placeholder", "search works"),
        "li_search": generate_xpath_query("//h3", "text()", "works", "illustrations and manga", "illustrations") + "/ancestor::section[1]/div[2]//li",
        "premium_search": generate_xpath_query("//h3", 'text()', 'popular works') + "/ancestor::section[1]/div[2]//li",
    }

    # Check if logged in otherwise log in with credentials
    try:
        # Check for create an account (only appears for non-logged in users). Must wait page.
        contains_works(driver, search_param["bar_search"])
        time.sleep(1)
        logged_out_button = driver.find_elements(By.XPATH, case_insensitive_xpath_contains("//a", 'Create an account'))

        if not logged_out_button:
            success_login = True
        elif user_name and pass_word:
            print("Logging in...")
            if login_handler(driver, exec_path, user_name, pass_word):
                success_login = True

        if not success_login:
            print("Failed! You are not logged in...")

    except Exception as e:
        print(f"Failed! You are not logged in... Exception: {e}")
    
    if not success_login:
        is_lang_en(driver)

    if not is_search_continued:
        searchQuery(user_search, driver, search_param["bar_search"], mode=0)
    time.sleep(2)

    if start_date and not success_login:
        driver.get(driver.current_url + f"?scd={start_date}&ecd={end_date}")
        time.sleep(2)
    elif start_date and success_login:
        cur_url = driver.current_url.split("?")
        driver.get(cur_url[0] + f"?scd={start_date}&ecd={end_date}&" + cur_url[1])
        time.sleep(2)

    ultimatium = 1 if 0 in imageControl else 0
    ai_mode = 1 if 3 in imageControl else 0

    if not contains_works(driver, search_param["li_search"]):
        print("No works found...")
        return []
    
    # Search for images in the premium section
    premium_pics = 0
    if 0 in searchTypes:
        await search_image(driver, exec_path, filters, search_param)
        premium_pics = len(image_locations)

    # Switch to english
    try:
        english_span = driver.find_element(By.XPATH, "//span[contains(text(), 'English')]")
        driver.execute_script("arguments[0].click();", english_span)
    except:
        pass


    # Apply filters if logged in
    try:
        if success_login:
            driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div[3]/div/div[5]/nav/a[2]").click()
            print("Illustrations only")
            time.sleep(1)

            mode = ""
            order = ""

            if 0 in viewRestriction and 1 in viewRestriction:
                print("PG Friendly and r-18")
            elif 0 in viewRestriction:
                mode = "mode=safe&"
                print("PG Friendly")
            elif 1 in viewRestriction:
                mode = "mode=r18&"
                print("r-18")
            if 2 in imageControl:
                order = "order=date&"
                print("Order by oldest")

            cur_url = driver.current_url.split("?")
            driver.get(cur_url[0] + f"?{order}{mode}" + cur_url[1])
        else:
            if contains_works(driver, case_insensitive_xpath_contains("//div", 'Show all')):
                driver.find_element(By.XPATH, case_insensitive_xpath_contains("//div", 'Show all')).click()
    except Exception as e:
        print(f"Failed to apply filters or show all works... Exception: {e}")
    
    prev_search = len(image_locations)
    curr_page = driver.current_url

    if 1 in searchTypes or searchTypes == []:
        while len(image_locations) - premium_pics < num_pics*num_pages:
            await search_image(driver,exec_path,filters,search_param=search_param,searchLimit=searchLimit)
            if len(image_locations) < num_pics*num_pages and not valid_page(driver, ['XPATH', 'XPATH'], ['//*[@class="sc-xhhh7v-0 kYtoqc"]', './/a']):
                print("Reached end of search results")
                break
    driver.quit()

    return image_locations


async def search_image(driver,exec_path,filters,search_param,searchLimit={"pagecount": 1, "imagecount": 99}):
    # Searches using premium or freemium
    search_type = awaitPageLoad(driver=driver,searchLimit=searchLimit,search_param=search_param)
    if search_type == -1:
        return
    
    # The main image searcher
    for page in range(searchLimit["pagecount"]):
        temp_img_len = len(image_locations) 
        contains_works(driver, search_param["li_search"] + "//div//a")
        images = search_image_type(search_type, driver, search_param=search_param)

        for image in images:
            if len(image_locations) - prev_search >= searchLimit["imagecount"]*searchLimit["pagecount"] or len(image_locations) - temp_img_len >= searchLimit["imagecount"]:
                break
            
            image = image.find_element(By.XPATH, ".//div//a")
            imageLink = image.find_elements(By.XPATH, ".//img")

            if image.get_attribute("href").rsplit("/", 1)[-1] not in image_names:
                if ai_mode == 1 and await process_ai_mode(imageLink, image, driver, exec_path):
                    continue # Skip the image if AI mode is on and it is not approved

                try:
                    if sum(filters.values()) == 0 and len(imageLink): # Dl the image directly from the grid
                        await thumbnailDownloader(imageLink=imageLink, image=image, driver=driver, exec_path=exec_path)
                    
                    else: # Dl the image from the image page (opens a new tab)
                        driver, tempImg = tab_handler(driver=driver, image=image)
                        contains_works(driver, "//div[@role='presentation']")
                        tempDL = driver.find_element(By.XPATH, "//div[@role='presentation']//img")

                        imagePopularity = parseImageData(filters=filters, 
                                                         Data=driver.find_elements(By.TAG_NAME, "dd"))
                        time.sleep(1)

                        if filterOptions(filters, imagePopularity=imagePopularity): # Check if image filters are satisfied
                            tempDLLink = tempDL.get_attribute("src")

                            # Dl the original resolution image
                            if ultimatium:
                                tempDLLink = tempDLLink.replace("img-master", "img-original"
                                ).replace("_master1200", "")

                            await download_image(imageLink=tempDLLink, exec_path=exec_path, driver=driver)
                        else:
                            print("\nImage filters not satisfied...")
                        driver = tab_handler(driver=driver)
                        time.sleep(0.3)

                # In case of stale element or any other errors
                except Exception as e:
                    if driver.window_handles[-1] != driver.window_handles[0]:
                        print(f"\nI ran into an error, moving on...{e}")
                        driver = tab_handler(driver=driver)
                    time.sleep(randint(1, 3) + randint(0, 9) / 10)
                    continue

            else:
                print("\nImage already exists, moving to another image...")
            save_Search(driver, mode=0)
        if not valid_page(driver, ['XPATH', 'XPATH'], ['//*[@class="sc-xhhh7v-0 kYtoqc"]', './/a']):
            break


######## FUNCTIONS PRONE TO CHANGE ########
def login_handler(driver, exec_path, user_name, pass_word):
    time.sleep(5)
    login_btn = driver.find_elements(By.XPATH, "//*[@class='sc-oh3a2p-4 gHKmNu']//a")[1]
    login_btn.click()

    contains_works(driver, "//*[@class='sc-2o1uwj-0 elngKN']")
    user_btn = driver.find_element(
        By.XPATH, "//*[@class='sc-2o1uwj-0 elngKN']"
    ).find_elements(By.TAG_NAME, "fieldset")
    user_btn[0]

    actions = ActionChains(driver)
    actions.click(user_btn[0]).send_keys(user_name).perform()
    time.sleep(0.5)
    actions.click(user_btn[1]).send_keys(pass_word).perform()

    # Log in button
    driver.find_element(By.XPATH,"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]").click()

    return True


async def download_image(imageLink, exec_path, driver, mode=1):
    tempDLName = imageLink.rsplit("/", 1)[-1]
    img_loc = f"./{exec_path.folder_path}/{tempDLName}"
    headers = get_selenium_headers(driver)

    for attempt in range(2):
        try:
            await download_file(imageLink, img_loc, headers)
        except Exception as e:  # Catch the exception raised by download_file
            if attempt < 1:  # Only retry if this is the first attempt
                imageLink = imageLink.rsplit(".",1)[0]+".png"
                headers = installUrlOpeners(imageLink)
            else:
                raise  # Re-raise the exception if this is the second attempt
        else:
            print(f"\n{imageLink}")
            if mode:
                image_locations.append(f"./{exec_path.folder_path}/{tempDLName}")
                image_names.append(f"{tempDLName.split('.')[0]}")
            return img_loc


async def thumbnailDownloader(imageLink, image, driver, exec_path, mode=1):
    imageLink = image_type(imageLink=imageLink, mode=mode)

    action = ActionChains(driver=driver)
    action.move_to_element(image.find_element(By.XPATH, ".//img")).perform()

    return await download_image(imageLink=imageLink, exec_path=exec_path, driver=driver, mode=mode)


def is_lang_en(driver):
    try:
        anchors = driver.find_elements(By.XPATH, '//*[@class="sc-93qi7v-2 hbGpVM"]//a')
        for n_iter,anchor in enumerate(anchors):
            if anchor.get_attribute("lang") =="en":
                driver.execute_script("arguments[0].click();", anchor)
    except Exception as e:
        # You are either in english or they changed the xpath
        pass


######## HEADER CONSTRUCTION ########
def installUrlOpeners(driver,mode=1): # Mode 0 means its a thumbnail
    if ultimatium and mode:
        header = create_url_headers(driver)
    else:
        header = create_url_headers(driver.current_url)
    return header

def get_selenium_headers(driver):
    headers = {
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8,ru;q=0.7,ja;q=0.6,en-GB;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.pixiv.net/',  # Important to include referer
        'User-Agent': driver.execute_script("return navigator.userAgent;"),  # Get dynamic User-Agent from browser
        'Sec-CH-UA': driver.execute_script("return navigator.userAgentData.brands.map(b => b.brand + ';v=' + b.version).join(', ');"),
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': driver.execute_script("return navigator.userAgentData.platform;"),
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Connection': 'keep-alive',
        'Priority': 'i',
    }
    return headers


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
            contains_works(driver, search_param["premium_search"], timeout=10)
            print("Premium section found, searching for images...")
        except:
            print("No popular section")
            search_type = -1
            return search_type
    else:
        try:
            contains_works(driver, search_param["li_search"])
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


def date_handler(sel_date):
    temp = sel_date.split("-")
    try:
        datetime(int(temp[0]), int(temp[1]), int(temp[2]))
    except ValueError:
        return 0
    return 1


async def process_ai_mode(imageLink, image, driver, exec_path):
    try:
        # Dl the image thumbnail from the grid
        img_loc = await thumbnailDownloader(imageLink=imageLink, image=image, driver=driver, exec_path=exec_path, mode=0)
        decision = True

        if img_classifier(img_loc):
            print("AI Mode: I approve this image")
            decision = False
        else:
            print("AI Mode: Skipping this image")
        os.remove(img_loc)
        return decision
    except:
        print("AI Mode: Skipping this image due to an error")
        return True
    

def case_insensitive_xpath_contains(xpath, text):
    return f"{xpath}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"


def generate_xpath_query(base_xpath, attribute, *args):
    return base_xpath + "[" + " or ".join(f"translate({attribute}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = '{arg.lower()}'" for arg in args) + "]"