import json
import time
import urllib.request
import re
from urllib.error import HTTPError
import pyodbc
from URLParser import URLParser

with open('Skins_List2.json', 'r', encoding="utf_8") as file:
    skins_list = json.load(file)

with open('config.json', 'r') as file:
    config = json.load(file)

wear_map = {
    "Factory New",
    "Minimal Wear",
    "Field-Tested",
    "Well-Worn",
    "Battle-Scarred"
}

rarity_map = {
    "Consumer Grade" : 0,
    "Consumer": 0,
    "Base Grade" : 0,
    "Base": 0,
    "Industrial Grade": 1,
    "Industrial": 1,
    "Mil-Spec": 2,
    "High Grade": 2,
    "High": 2,
    "Restricted": 3,
    "Remarkable": 3,
    "Classified": 4,
    "Exotic": 4,
    "Covert": 5,
    "Extraordinary": 5,
    "Rare Special": 6,
    "Rare": 6,
    "Gloves": 6,
    "Knives": 6
}

def openSQLConnection():
    SERVER = config["DB_Server"]
    DATABASE = "CounterSkins"
    PORT = config["DB_Port"]
    cnxn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};PORT={PORT};Trusted_Connection=Yes')
    return cnxn.cursor()

def get_collections(cursor):
    sql = "SELECT * FROM collections"
    cursor.execute(sql)
    cs2_collections = cursor.fetchall()
    collections_map = {}
    for collection in cs2_collections:
        collections_map[collection[1]] = collection[0]

    return collections_map

def get_skins(collections_map):
    counter = 0
    parser = URLParser()
    failure_count = 0
    for skin in skins_list:
        for wear in wear_map:
            try:
                url = parser.parse(config["Steam_Market_Search_Address"], skin["weapon"], skin["skin"], wear)
                steam_store_page = urllib.request.urlopen(url).read().decode("utf-8")

                item_name = f"{skin["weapon"]} | {skin["skin"]} ({wear})"
                g_rgAssets = re.findall(r'g_rgAssets = .*', steam_store_page)
                g_rgAssets = g_rgAssets[0].replace('g_rgAssets = ', '')
                g_rgAssets = g_rgAssets[:-2]
                loaded_json = json.loads(g_rgAssets)
                print("doing something")
                if '730' in loaded_json:
                    items = next(iter(loaded_json['730'].values()))
                    first_item = next(iter(items.values()))
                    description_idx = -1
                    description_value = first_item["descriptions"][description_idx]["value"]
                    while not collections_map.get(description_value) and -description_idx < len(first_item["descriptions"]):
                        description_idx -= 1
                        description_value = first_item["descriptions"][description_idx]["value"]

                    collection = description_value

                    item_id = re.findall(r'Market_LoadOrderSpread.*', steam_store_page)
                    item_id = item_id[0].split("(")[1].split(")")[0].strip()

                    price_data_url = f"https://steamcommunity.com/market/itemordershistogram?country=GB&language=english&currency=2&item_nameid={item_id}"
                    price_json = json.load(urllib.request.urlopen(price_data_url))

                    buy = price_json["highest_buy_order"] if price_json["highest_buy_order"] else "NULL"
                    sell = price_json["lowest_sell_order"] if price_json["lowest_sell_order"] else "NULL"
                    print(f"Attempting to insert values: {item_name} | {item_id} | {skin["weapon"]} | {skin["skin"]} | {wear} | {rarity_map[skin["quality"]]} | {buy} | {sell} | {collections_map[collection]}")
                    item_name = item_name.replace("'", "''")
                    skin_name = skin["skin"].replace("'", "''")
                    insert_statement = f"INSERT INTO skins2 (FULL_NAME, STEAM_NAME_ID, WEAPON_NAME, SKIN_NAME, CONDITION, RARITY, CURRENT_BUY, CURRENT_SELL, COLLECTION) VALUES ('{item_name}', {item_id},'{skin["weapon"]}', '{skin_name}', '{wear}', {rarity_map[skin["quality"]]}, {buy}, {sell}, {collections_map[collection]})"
                    cursor.execute(insert_statement)
                    cursor.commit()
                    counter += 1
                    print(f"Completed skin number {counter}/{len(skins_list * 5)}")
            except HTTPError as HttpExcept:
                print(
                    f"Exception occurred while trying to request data on: {skin}, Exception: {HttpExcept} - Waiting out cooldown period")
                failure_count += 1
                time.sleep(620)
            except Exception as exception:
                try:
                    print(f"Exception occurred while trying to process: {skin} with wear: {wear}, Exception: {exception}")
                    file = open('failed_records.txt', "a")
                    file.write(skin)
                    file.close()
                except:
                    print("Could not output skin name to log file")
            finally:
                time.sleep(13)

cursor = openSQLConnection()
collections = get_collections(cursor)
get_skins(collections)