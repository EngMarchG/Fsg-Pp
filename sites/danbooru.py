import os
import time

from random import randint
from selenium.webdriver.common.by import By
from commands.driver_instance import tab_handler, download_file
from commands.exec_path import imgList
from commands.universal import *
from ai.classifying_ai import img_classifier


async def getOrderedDanbooruImages(driver, user_search, num_pics, num_pages, filters, bl_tags, inc_tags, exec_path, imageControl):
    global image_locations, bl_tags_list, inc_tags_list, image_names, ai_mode, rating_filters
    image_names = imgList(mode=0)
    image_locations = []
    link = "https://danbooru.donmai.us/"
    is_search_continued = 0

    # Must pay attention if imageControl gets other features later!
    if imageControl:
        is_search_continued = continue_Search(driver, link, mode=1)
    else:
        driver.get(link)

    # Rating Filter Creation
    rating_filters = ["e"] if 2 in filters else []
    rating_filters = ["s","e"] if 3 in filters else []
    rating_filters = ["q","s","e"] if 4 in filters else []

    # Tag list creation
    match_type = 1 if 1 in filters else 0
    r_18 = pg_lenient() if 2 in filters else []
    r_18 = pg_strict() if 3 in filters else r_18
    ai_mode = 1 if 5 in filters else 0

    # Replace spaces to make spaces feasible by the user
    user_search = user_search.replace(" ", "_")

    bl_tags_list = create_filter_tag_list(bl_tags, r_18)
    inc_tags_list = create_tag_list(inc_tags, match_type) if inc_tags else []
    
    if not is_search_continued:
        searchQuery(user_search, driver, '//*[@name="tags"]', execute_times=2)
        if 0 in filters:
            time.sleep(1.2)
            search_bar_update(driver, '//*[@name="tags"]', " order:score", to_append=True, to_execute=["ENTER"])
    
    if not contains_works(driver, '//*[@class="posts-container gap-2"]'):
        print("No works found...")
        return []
    
    if ai_mode:
        contains_works(driver, '//*[@class="popup-menu-content"]')
        driver.get(driver.find_element(By.XPATH, '(//*[@class="popup-menu-content"]//li)[6]//a').get_attribute("href"))

    curr_page = driver.current_url
    while len(image_locations) < num_pics*num_pages:
        await pages_to_search(driver, num_pages, num_pics, exec_path)
        if curr_page == driver.current_url and len(image_locations) < num_pics*num_pages:
            print("Reached end of search results")
            break
        curr_page = driver.current_url
    driver.close()

    return image_locations


async def pages_to_search(driver, num_pages, num_pics, exec_path):
    for i in range(num_pages):
        contains_works(driver, '//*[@class="posts-container gap-2"]')
        # Selects the picture grids
        images = driver.find_element(
            By.XPATH, '//*[@class="posts-container gap-2"]'
        ).find_elements(By.CLASS_NAME, "post-preview-link")
        await grid_search(driver, num_pics, images, exec_path, num_pages)
        save_Search(driver, mode=1)
        if not valid_page(driver, ["CLASS_NAME"], ["paginator-next"]) or len(image_locations) >= num_pics*num_pages:
            break


async def grid_search(driver, num_pics, images, exec_path, num_pages):
    temp_img_len = len(image_locations)
    for n_iter, image in enumerate(images):
        if len(image_locations) >= num_pics*num_pages or len(image_locations) - temp_img_len >= num_pics:
            break

        try:
            if sanitize_name(image.find_element(By.XPATH, ".//img").get_attribute('src').split("/")[-1].split(".")[0]) in image_names:
                print("\nImage already exists, moving to another image...")
                continue

            # Has to be checked this way otherwise tags are not visible in headless mode
            img_tags = driver.find_elements(By.CLASS_NAME, "post-preview")[n_iter].get_attribute('data-tags')
            img_rating = driver.find_elements(By.CLASS_NAME, "post-preview")[n_iter].get_attribute('data-rating')

            if filter_ratings(img_rating,rating_filters) and filter_tags(bl_tags_list, inc_tags_list, img_tags):
                
                
                if ai_mode:
                    checker = 0
                    image_loc = await download_image(exec_path=exec_path, 
                                                     search_ele=image.find_element(By.XPATH, ".//img"),
                                                     search_attrib="src",
                                                     delete_image=1)
                    if img_classifier(image_loc):
                        print("AI Mode: I approve this image")
                    else:
                        print("AI Mode: Skipping this image")
                        checker = 1
                    os.remove(image_loc)
                    if checker:
                        continue

                driver, tempImg = tab_handler(driver=driver,image=image)
                contains_works(driver, '//*[@id="post-option-download"]/a')
                await download_image(exec_path=exec_path, 
                                     search_ele=driver.find_element(By.XPATH, '//*[@id="post-option-download"]/a'),
                                     search_attrib="href")
                driver = tab_handler(driver=driver)

            else:
                print("\nFilters did not match/Not an image, moving to another image...")

        except Exception as e:
            print(f"\nI ran into an error, closing the tab and moving on...{e}")
            if driver.window_handles[-1] != driver.window_handles[0]:
                driver = tab_handler(driver=driver)
            time.sleep(randint(0,2) + randint(0,9)/10)


async def download_image(exec_path, search_ele, search_attrib, delete_image=0):
    tempDLAttr = search_ele.get_attribute(search_attrib)
    tempDLName = sanitize_name(search_ele.get_attribute("download") if search_attrib != "src" 
                               else tempDLAttr.split("/")[-1])
    img_loc = f"./{exec_path.folder_path}/{tempDLName}"
    print(f"\n{tempDLAttr.split('?')[0]}")
    
    # Download the image
    await download_file(tempDLAttr, img_loc)

    if not delete_image:
        image_locations.append(img_loc)
        image_names.append(f"{tempDLName.split('.')[0]}")
    return img_loc


######## HELPER FUNCTIONS UNLIKELY TO CHANGE ########
def filter_ratings(img_rating,rating_filters):
    if img_rating not in rating_filters:
        return True
    return False


def filter_tags(bl_tags_list, inc_tags_list, img_tags):
    # Hashmap of picture's tags for O(1) time searching
    img_hash = {}
    for img_tag in img_tags.split(" "):
        img_hash[img_tag] = 1

    # Included tags (exact match or not exact)
    if inc_tags_list and inc_tags_list[-1] == 1:
        inc_tags_list.pop()
        for tag in inc_tags_list:
            if not img_hash.get(tag, 0):
                return False
    elif inc_tags_list:
        cond = False
        for tag in inc_tags_list:
            if img_hash.get(tag, 0):
                cond = True
                break
        if not cond:
            return False

    # Note that bl_tags_list is never empty since it filters videos
    for tag in bl_tags_list:
        if img_hash.get(tag,0):
            return False
    return True


def create_tag_list(inc_tags, match_type):
    temp_tags = [tag.lstrip().replace(" ","_") for tag in inc_tags.split(",")]
    if match_type:
        temp_tags.append(1)
    return temp_tags


def create_filter_tag_list(bl_tags, r_18):
    temp_tags = ["animated", "video", "sound"]
    if bl_tags:
        temp_tags += [tag.lstrip().replace(" ","_") for tag in bl_tags.split(",")]
    if r_18:
        temp_tags += r_18
    return temp_tags


def pg_lenient():
    return ["sex","penis","vaginal","completely_nude","nude","exposed_boobs","ahegao","cum","no_panties","no_bra", 
            "nipple_piercing", "anal_fluid","uncensored", "see-through", "pussy", "cunnilingus", "oral", "ass_focus",
            "anal", "sex_from_behind", "cum_on_clothes", "cum_on_face", "nipple","nipples", "missionary"
            "fellatio", "rape", "breasts_out","cum_in_pussy", "condom", "dildo", "sex_toy", "cum_in_mouth", "heavy_breathing", "cum_on_tongue"
            "panties", "panty_pull", "nude_cover", "underwear_only","grabbing_own_breast","ass_grab","censored","areola_slip","areolae","torn_pantyhose","micro_bikini","steaming_body"]


def pg_strict():
    return pg_lenient() + ["piercings", "cleavage","boobs","thongs","fellatio_gesture", "mosaic_censoring", "ass", "mosaic_censoring", 
                            "covered_nipples", "thigh_focus", "thighs", "bikini", "swimsuit", "grabbing_another's_breast", "huge_breasts", 
                            "foot_focus", "licking_foot", "foot_worship", "shirt_lift","clothes_lift", "underwear", "panties_under_pantyhose"]
