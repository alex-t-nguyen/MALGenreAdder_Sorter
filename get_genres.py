
import gzip
import time
import getpass
import os.path
import xml.etree.cElementTree as ET
import pandas as pd
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 60

command = str(sys.argv[1])
user_genre = str(sys.argv[2])

if command.upper() == 'E':
    browser = webdriver.Chrome()
    browser.get('https://myanimelist.net/login.php')
else:
    path = str(sys.argv[3])


def main():
    global df_xml

    if command.upper() == 'E':
        login()
        navigate_to_list()
        python_selector = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/a[6]")))
        python_selector.send_keys(Keys.RETURN)
        export_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/input")))
        export_button.click()
        WebDriverWait(browser, 5).until(EC.alert_is_present(), 'Timed out waiting for confirmation popup to appear.')
        alert_export_popup = browser.switch_to.alert
        alert_export_popup.accept()
        export_link = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='dialog']/tbody/tr/td/div/a")))
        export_link.click()
        export_text = export_link.text

        list_filepath = "C:/Users/AlexN/Downloads/{0}".format(export_text)

        print("MAL list file: " + list_filepath)
        seconds = 0

        # Wait for file to complete downloading
        while not os.path.exists(list_filepath):
            time.sleep(1)
            seconds += 1
            if seconds > TIMEOUT:
                break
        # Unzip .gz file and convert data to pandas dataframe
        df_xml = unzip_mal(list_filepath)

        browser.quit()
    else:
        # path = input("Enter file path of list to use: ") -> added as batch file command line argument
        df_xml = unzip_mal(path)

    # user_genre = input("Enter genre to search for: ") -> added as batch file command line argument
    plan_to_watch_shows = []
    for index, row in df_xml.iterrows():
        if row['my_status'] == "Plan to Watch":
            plan_to_watch_shows.append(row)

    final_anime_list = []
    for anime in plan_to_watch_shows:
        if anime['my_tags'] is None:
            continue
        genres_list = anime['my_tags'].split(", ")
        for genre in genres_list:
            if genre.lower() == user_genre.lower():
                final_anime_list.append(anime['series_title'])

    # Write all anime titles to .txt file with specified genre
    with open("C:/Users/AlexN/Desktop/AnimeList.txt", "w", encoding="utf-8") as anime_list_file:
        anime_list_file.write("------------- GENRE: " + user_genre.capitalize() + " -------------\n")
        for anime in final_anime_list:
            anime_list_file.write(anime + "\n")

    # If no animes in list -> file not created, so can't open file -> return message
    if len(final_anime_list) == 0:
        print("No \"Plan to watch\" animes available with genre: " + user_genre)
    else:
        os.startfile("C:/Users/AlexN/Desktop/AnimeList.txt")


def login():
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


def export_or_upload():
    user_command = input("Do you want to export a list from MAL or upload a current list? [E/U]: ")
    return user_command


def navigate_to_list():
    python_selector = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='header-menu']/div[2]/a/i")), message="Unable to login. Check your login credentials again...")
    python_selector.click()
    python_selector = browser.find_element_by_xpath("//*[@id='header-menu']/div[2]/div/ul/li[1]/a")
    python_selector.click()
    browser_after = browser.window_handles[0]
    browser.switch_to.window(browser_after)


def unzip_mal(filepath):
    with gzip.open(filepath, 'rb') as f_in:
        parsed_xml = ET.parse(f_in)
        # "user_id", "user_name", "user_export_type", "user_total_anime", "user_total_watching",
        #                    "user_total_completed", "user_total_onhold",
        #                    "user_total_dropped", "user_total_plantowatch"
        df_cols = ["series_animedb_id", "series_title", "series_type",
                   "series_episodes", "my_id",
                   "my_watched_episodes", "my_start_date", "my_finish_date", "my_rated", "my_score", "my_dvd",
                   "my_storage", "my_status",
                   "my_comments", "my_times_watched", "my_rewatch_value", "my_tags", "my_rewatching",
                   "my_rewatching_ep", "update_on_import"]
        df_xml_converted = pd.DataFrame(columns=df_cols)

        # Create pandas dataframe object (table)
        for node in parsed_xml.getroot():
            series_animedb_id = node.find('series_animedb_id')
            series_title = node.find('series_title')
            series_type = node.find('series_type')
            series_episodes = node.find('series_episodes')
            my_id = node.find('my_id')
            my_watched_episodes = node.find('my_watched_episodes')
            my_start_date = node.find('my_start_date')
            my_finish_date = node.find('my_finish_date')
            my_rated = node.find('my_rated')
            my_score = node.find('my_score')
            my_dvd = node.find('my_dvd')
            my_storage = node.find('my_storage')
            my_status = node.find('my_status')
            my_comments = node.find('my_comments')
            my_times_watched = node.find('my_times_watched')
            my_rewatch_value = node.find('my_rewatch_value')
            my_tags = node.find('my_tags')
            my_rewatching = node.find('my_rewatching')
            my_rewatching_ep = node.find('my_rewatching_ep')
            update_on_import = node.find('update_on_import')

            df_xml_converted = df_xml_converted.append(pd.Series(
                [get_value_of_node(series_animedb_id), get_value_of_node(series_title), get_value_of_node(series_type),
                 get_value_of_node(series_episodes),
                 get_value_of_node(my_id), get_value_of_node(my_watched_episodes), get_value_of_node(my_start_date),
                 get_value_of_node(my_finish_date),
                 get_value_of_node(my_rated), get_value_of_node(my_score), get_value_of_node(my_dvd),
                 get_value_of_node(my_storage), get_value_of_node(my_status),
                 get_value_of_node(my_comments), get_value_of_node(my_times_watched),
                 get_value_of_node(my_rewatch_value), get_value_of_node(my_tags),
                 get_value_of_node(my_rewatching), get_value_of_node(my_rewatching_ep),
                 get_value_of_node(update_on_import)], index=df_cols), ignore_index=True)

        return df_xml_converted


def get_value_of_node(node):
    """ return node text or None"""
    return node.text if node is not None else None


if __name__ == "__main__":
    main()
