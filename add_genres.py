import time
from selenium import webdriver
import getpass
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCROLL_PAUSE_TIME = 0.5
ANIME_LINK_PATH = ".//td[@class='data title clearfix']//a"
ANIME_TAG_PATH = ".//td[@class='data tags']"

browser = webdriver.Chrome(executable_path=r'C:\\Users\AlexN\Documents\\Python Projects\\MALGenreAdder\\chromedriver.exe')
browser.get('https://myanimelist.net/login.php')


def open_mal():
    # Log in to MAL
    python_selector = browser.find_element_by_xpath("//*[@id='loginUserName']")
    username = input("Username for https://myanimelist.net/login.php: ")
    python_selector.send_keys(username)
    python_selector = browser.find_element_by_xpath("//*[@id='login-password']")
    python_selector.click()
    password = getpass.getpass("Password for https://myanimelist.net/login.php: ")
    python_selector.send_keys(password)
    python_selector = browser.find_element_by_xpath("//*[@id='dialog']/tbody/tr/td/form/div/p[6]/input")
    python_selector.submit()

    # Navigate to list
    navigate_to_list()

    scroll_to_bottom()

    table = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='list-container']/div[4]/div/table")))
    table_bodies = table.find_elements_by_xpath(".//tbody[@class='list-item']")
    
    non_edited_table_bodies = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, ".//tbody[@class='list-item']/tr[1]/td[@class='data tags']/div[not(span)]")))
    print("Animes to add genres to: " + str(len(non_edited_table_bodies)))

    num_bodies = len(table_bodies)
    non_edited_num_bodies = len(non_edited_table_bodies)

    if non_edited_num_bodies > 290:
        scroll_to_bottom()

    for i in range(0, non_edited_num_bodies, 1):

        # If near bottom of page (item #300) -> scroll to load more data if not at end of list
        scroll_to_bottom()
        # Click on anime link to navigate to info page
        anime_data = get_link(ANIME_LINK_PATH)
        anime_data[1].send_keys(Keys.RETURN)

        # Switch broswer since navigating to new page
        browser_after = browser.window_handles[0]
        browser.switch_to.window(browser_after)

        # Find anime info column (left side of page with list of genres)
        inner_table_row = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='content']/table//tbody//tr")), message='Couldn\'t find anime info column on info page.')
        details_column = inner_table_row.find_element_by_xpath(".//td[@class='borderClass']//div")
        genres = details_column.find_elements_by_xpath(".//span[@itemprop='genre']")

        genres_list = []
        num_genres = len(genres)
        for j in range(0, num_genres):
            genres_list.append(genres[j].get_attribute('textContent'))

        # Navigate back to list of anime
        navigate_to_list()
        # Need to scroll to bottom every time we navigate back to list because page refreshes
        # and the max number of items loaded in list initially is 300
        if anime_data[0] >= 300:
            scroll_to_bottom()
            time.sleep(1)
        # Click on tag link
        td_link = get_link(ANIME_TAG_PATH)[1]
        td_link.find_element_by_xpath(".//a[@class='edit']").send_keys(Keys.RETURN)
        textarea = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//textarea")))
        for genre in genres_list:
            textarea.send_keys(genre, ", ")
    # Click back on "All Anime" link to exit textbox and save edit to final anime in list
    all_anime_link = browser.find_element_by_xpath("//*[@id='status-menu']/div/a[1]")
    all_anime_link.send_keys(Keys.RETURN)
    browser.quit()
    print("All genres updated in MAL for user: https://myanimelist.net/animelist/" + username)


def get_link(link_xpath):
    table = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='list-container']/div[4]/div/table")))
    table_body = WebDriverWait(table, 10).until(EC.presence_of_element_located((By.XPATH, ".//tbody[@class='list-item']/tr[1]/td[@class='data tags']/div[not(span)]")))
    
    tr = table_body.find_element_by_xpath("../../..")
    anime_id = int(tr.find_element_by_xpath(".//td[@class='data number']").text)
    link = tr.find_element_by_xpath(link_xpath)
    return (anime_id, link)


def scroll_to_bottom():
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='list-container']/div[4]/div/table")))
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            return
        last_height = new_height


def navigate_to_list():
    python_selector = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='header-menu']/div[2]/a/i")))
    python_selector.click()
    python_selector = browser.find_element_by_xpath("//*[@id='header-menu']/div[2]/div/ul/li[1]/a")
    python_selector.click()
    browser_after = browser.window_handles[0]
    browser.switch_to.window(browser_after)


if __name__ == "__main__":
    open_mal()
