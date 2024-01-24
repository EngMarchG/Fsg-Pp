import time 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def searchQuery(user_search, driver, elem, mode=1, execute_times=[1,1]):
    """
    Performs a search query on a webpage.

    Args:
        user_search (str): The search term.
        driver (selenium.webdriver.Chrome): The webdriver instance.
        elem (str): The XPATH of the search bar element.
        mode (int, optional): Determines the search mode. If 0, specific to pixiv only. Defaults to 1.
        execute_times (list, optional): A list of two integers. The first integer specifies the number of times to press the down arrow key, 
        and the second integer specifies the number of times to press the enter key. 
        If only one integer is provided, it is used for both actions. Defaults to [1,1].
    """
    # If execute_times is not a list, convert it to a list
    # set the second element to previous if it is not provided
    if not isinstance(execute_times, list) or len(execute_times) == 1:
        execute_times = [execute_times, execute_times]

    user_search = user_search.lower()
    WebDriverWait(driver, timeout=15).until(EC.presence_of_element_located((By.XPATH, elem)))
    search_bar = driver.find_element(By.XPATH, elem)

    try:
        search_bar.click()
        if not mode:
            time.sleep(1.8)
    except Exception as e:
        time.sleep(3)
        
    search_bar_update(driver=driver, elem=elem, user_search=user_search)
        
    if not mode:
        specific_Query(driver=driver, search_bar=search_bar, user_search=user_search)
        time.sleep(1.2)
    else:
        for i in range(execute_times[0]):
            search_bar.send_keys(Keys.ARROW_DOWN)
            time.sleep(1.2)
        for i in range(execute_times[1]):
            time.sleep(0.6)
            search_bar.send_keys(Keys.ENTER)


def search_bar_update(driver, elem, user_search, to_append=False, to_execute=[]):
    """
    Updates the search bar of a webpage and executes the provided actions if any.

    Args:
        driver (selenium.webdriver.Chrome): The webdriver instance.
        elem (str): The XPATH of the search bar element.
        to_append (str, optional): The string to append to the search bar. Defaults to False.
        to_execute (list, optional): The list of actions to execute. Defaults to [].
    """
    search_bar = driver.find_element(By.XPATH, elem)
    try:
        if to_append:
            driver.execute_script("arguments[0].value+=arguments[1]", search_bar, user_search)
        else:
            driver.execute_script('arguments[0].value=arguments[1]', search_bar, user_search)
        
        if to_execute:
            # Make each ele in to_execute uppercase just in case
            to_execute = [ele.upper() for ele in to_execute]
            for action in to_execute:
                search_bar.send_keys(getattr(Keys, action))
    except Exception as e:
        pass


def save_Search(driver, mode=0):
    """
    Saves the current URL of the webdriver to a file.

    Args:
        driver (selenium.webdriver.Chrome): The webdriver instance.
        mode (int, optional): The line number in the file to save the URL to, offset by 1. Defaults to 0.
    """
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
    except FileNotFoundError:
        line_to_modify = mode + 1  # Line number to modify based on mode
        new_line_content = driver.current_url  # Content to write to the line

        with open("./commands/url.txt", "w") as file:
            lines = ['\n'] * line_to_modify
            lines[line_to_modify - 1] = new_line_content + '\n'
            file.writelines(lines)


def continue_Search(driver, link, mode=0):
    """
    Continues a search from a saved URL, or from a provided URL if no saved URL exists.

    Args:
        driver (selenium.webdriver.Chrome): The webdriver instance.
        link (str): The URL to navigate to if no saved URL exists.
        mode (int, optional): The line number in the file to read the URL from, offset by 1. Defaults to 0.
    """
    try:
        with open("./commands/url.txt", "r") as file:
            lines = file.readlines()

        line_to_read = mode + 1  # Line number to read based on mode

        if len(lines) >= line_to_read and lines[line_to_read - 1].strip() != '':
            url = lines[line_to_read - 1].strip()
            driver.get(url)
            return 1
        else:
            driver.get(link)
    except:
        driver.get(link)


def specific_Query(driver, search_bar, user_search):
    """
    Performs a specific search query based on the provided search term.
    Currently for pixiv only

    Args:
        driver (selenium.webdriver.Chrome): The webdriver instance.
        search_bar (WebElement): The search bar element.
        user_search (str): The search term.
    """
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


def contains_works(driver, elem, find_by="XPATH",timeout=15):
    """
    Checks if a specific element is present on the page within a given timeout period.

    Args:
        driver (webdriver): Selenium webdriver instance used for page navigation.
        elem (str): The name of the element to find on the page.
        find_by (str, optional): The method to locate the element on the page. Can be BY.XPATH, BY.CLASS_NAME, BY.ID, etc. Defaults to "XPATH".
        timeout (int, optional): The maximum amount of time (in seconds) to wait for the element to appear. Defaults to 15.

    Returns:
        bool: True if the element is found within the timeout period, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((getattr(By, find_by), elem)))
        return True
    except TimeoutException:
        return False


def valid_page(driver, find_by, ele_names, target_attr="href", get_next_page=True):
    """ 
    Checks if the current page is valid and navigates to the next page if it exists.

    Args:
        driver (webdriver): Selenium webdriver instance used for page navigation.
        find_by (list): List of methods to locate elements on the page. Each method corresponds to a name in `ele_names`. 
                        Methods can be BY.XPATH, BY.CLASS_NAME, BY.ID, etc.
        ele_names (list): List of names of the elements to find on the page. Each name corresponds to a method in `find_by`.
        target_attr (str, optional): The attribute of the element to retrieve. Defaults to "href".
        get_next_page (bool, optional): If True, the function will navigate to the next page if it exists. Defaults to True.

    Returns:
        str or int: If a next page is found and `get_next_page` is True, returns the URL of the next page. 
                    If the current page is the last page or an error occurs, returns 0.
    """
    cur_url = driver.current_url
    # Check if find_by and ele_names are lists and if not, convert them to lists
    if not isinstance(find_by, list):
        find_by = [find_by]
    if not isinstance(ele_names, list):
        ele_names = [ele_names]

    # If find_by is shorter than ele_names, repeat the last element of find_by until it is the same length as ele_names
    while len(find_by) < len(ele_names):
        find_by.append(find_by[-1])
        
    try:
        next_page = driver
        for i in range((len(ele_names))):
            next_page = next_page.find_elements(getattr(By, find_by[i]), ele_names[i])[-1]

        if cur_url == next_page.get_attribute(target_attr):
            return 0
        if next_page:
            if get_next_page:
                driver.get(next_page.get_attribute(target_attr))
            return driver.current_url
    except Exception as e:
        #print(f"Error while finding next page: {e}")
        return 0


def sanitize_name(filename):
    """
    Removes invalid characters from a filename.

    Args:
        filename (str): The filename to sanitize.

    Returns:
        str: The sanitized filename.
    """
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.encode("ascii", "ignore").decode("ascii")