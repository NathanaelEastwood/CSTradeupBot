import json
import pyodbc
from selenium import webdriver
from selenium.common import ElementNotSelectableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

with open('config.json', 'r') as file:
    config = json.load(file)
with open('Skins_List2.json', 'r', encoding="utf_8") as file:
    skins_list = json.load(file)

def openSQLConnection():
    SERVER = config["DB_Server"]
    DATABASE = "CounterSkins"
    PORT = config["DB_Port"]
    cnxn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};PORT={PORT};Trusted_Connection=Yes')
    return cnxn.cursor()



def scrapeCsGoStash(cursor):
    for i in range(1609, 1610):
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument("--window-size=1920,1080")
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            driver = webdriver.Chrome(options=options)
            driver.get(f"https://stash.clash.gg/skin/{i}")
            min_value = driver.find_element(By.CLASS_NAME,"wear-min-value").get_attribute("data-wearmin")
            max_value = driver.find_element(By.CLASS_NAME, "wear-max-value").get_attribute("data-wearmax")
            weapon_name = driver.find_element(By.CSS_SELECTOR,
                                              "body > div.container.main-content > div:nth-child(2) > div.col-md-10 > div > div.col-md-7.col-widen > div.well.result-box.nomargin > h1 > a:nth-child(1)").text
            skin_name = driver.find_element(By.CSS_SELECTOR,
                                        "body > div.container.main-content > div:nth-child(2) > div.col-md-10 > div > div.col-md-7.col-widen > div.well.result-box.nomargin > h1 > a:nth-child(2)").text
            print(f"Got float values for skin name: {weapon_name} | {skin_name}")
            skin_name = skin_name.replace("'", "''")
            sql = f"UPDATE skins2 SET MIN_FLOAT = {min_value}, MAX_FLOAT = {max_value} WHERE WEAPON_NAME = '{weapon_name}' AND SKIN_NAME = '{skin_name}'"
            cursor.execute(sql)
            cursor.commit()
        except NoSuchElementException:
            print("Could not select element")

cursor = openSQLConnection()
scrapeCsGoStash(cursor)

