from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def searchQuery(user_search, driver, elem, mode=0, score="", isLoggedIn=True):
    if isLoggedIn == False:
        anchors = driver.find_elements(By.XPATH, '//*[@class="sc-93qi7v-2 hbGpVM"]//a')
        for n_iter,anchor in enumerate(anchors):
            if anchor.get_attribute("lang") =="en":
                driver.execute_script("arguments[0].click();", anchor)
        
    user_search = user_search.lower()
    WebDriverWait(driver, timeout=15).until(EC.presence_of_element_located((By.XPATH, elem)))
    search_bar = driver.find_element(By.XPATH, elem)

    try:
        search_bar.click()
        if not mode:
            time.sleep(1.8)
        driver.execute_script('arguments[0].value=arguments[1]', search_bar, user_search)
    except:
        time.sleep(3)
        driver.execute_script('arguments[0].value=arguments[1]', search_bar, user_search)
        
    if not mode:
        specific_Query(driver=driver, search_bar=search_bar, user_search=user_search)
    else:
        time.sleep(1)
        search_bar.send_keys(Keys.ARROW_DOWN)
        time.sleep(2)
    
    if mode:
        search_bar.send_keys(Keys.ARROW_DOWN)
        time.sleep(1.2)
        search_bar.send_keys(Keys.ENTER)
    time.sleep(0.3)

    try:
        driver.execute_script("arguments[0].value+=arguments[1]", search_bar, score)
        search_bar.send_keys(Keys.ENTER)
    except:
        pass


def save_Search(driver, mode=0):
    try:
        with open("./commands/url.txt", "r+") as file:
            lines = file.readlines()

            line_to_modify = mode + 1  # Line number to modify based on mode
            new_line_content = driver.current_url  # Content to write to the line

            if line_to_modify > len(lines):
                lines.extend(['\n'] * (line_to_modify - len(lines)))
            elif lines[line_to_modify - 1].strip() == new_line_content:
                # If the line already has the same content, no action is needed
                return

            lines[line_to_modify - 1] = new_line_content + '\n'

            file.seek(0)
            file.writelines(lines)
            file.truncate()
    except:
        line_to_modify = mode + 1  # Line number to modify based on mode
        new_line_content = driver.current_url  # Content to write to the line

        with open("./commands/url.txt", "w") as file:
            lines = ['\n'] * line_to_modify
            lines[line_to_modify - 1] = new_line_content + '\n'
            file.writelines(lines)



def continue_Search(driver, link, mode=0):
    try:
        with open("./commands/url.txt", "r") as file:
            lines = file.readlines()

        line_to_read = mode + 1  # Line number to read based on mode

        if len(lines) >= line_to_read and lines[line_to_read - 1].strip() != '':
            url = lines[line_to_read - 1].strip()
            driver.get(url)
        else:
            driver.get(link)
    except:
        driver.get(link)


def specific_Query(driver, search_bar, user_search):
    # Replace underscores with spaces and append the full search term
    user_search_words = user_search.replace("_", " ").split()
    user_search_words.append(''.join(user_search_words))
    full_query_found = False
    query_to_click = None

    try:
        for user_word in user_search_words:
            time.sleep(1.2)
            driver.execute_script('arguments[0].value=arguments[1]', search_bar, user_word)
            time.sleep(1)
            search_bar.send_keys(Keys.SPACE)
            time.sleep(2.5)

            search_bar_queries = driver.find_elements(By.XPATH, '//*[@class="sc-1974j38-2 kjWkkt"]//a')
            for query in search_bar_queries:
                query_text = query.find_element(By.XPATH, './/div').text.lower()
                if len(query.find_elements(By.XPATH, './/div//div[2]')) > 0:
                    query_text = query.find_element(By.XPATH, './/div//div[2]').text.lower()

                if all(word in query_text for word in user_search_words[:-1]):
                    query_to_click = query
                    full_query_found = True
                    time.sleep(0.3)
                    break

            if full_query_found:
                break

    except Exception as e:
        pass

    if full_query_found:
        driver.execute_script("arguments[0].click();", query_to_click)
    else:
        # If full query not found, just press Enter
        search_bar.send_keys(Keys.ENTER)


def contains_works(driver, elem):
    try:
        WebDriverWait(driver, timeout=9).until(EC.presence_of_element_located((By.XPATH, elem)))
        return True
    except:
        return False
    
    