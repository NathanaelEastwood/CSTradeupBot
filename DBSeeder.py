# we need to loop through every name in item_names to populate the following fields,
# item_id || rarity || current_buy || current_sell || collection
# for collection probably worth foreign keying it to another table
import json
from urllib.error import HTTPError

import pyodbc
import urllib.request
import re
from URLParser import URLParser
import time

def insertData():
    return None

def openSQLConnection():
    SERVER = config["DB_Server"]
    DATABASE = "CounterSkins"
    PORT = config["DB_Port"]
    cnxn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};PORT={PORT};Trusted_Connection=Yes')
    return cnxn

# def get_proxy_opener(index):
#     proxy_address = f"{proxy_list[index]["ip"]}:{proxy_list[index]["port"]}"
#     handler = urllib.request.ProxyHandler({'http': proxy_address,
#                                  'https': proxy_address})
#     opener = urllib.request.build_opener(handler)
#     return opener

# with open('proxy_list.json', 'r', encoding="utf8") as file:
#     proxy_list = json.load(file)

# proxy_index = 0
# proxy_opener = get_proxy_opener(proxy_index)

with open('config.json', 'r') as file:
    config = json.load(file)

cursor = openSQLConnection().cursor()
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

sql = "SELECT * FROM collections"
cursor.execute(sql)
cs2_collections = cursor.fetchall()
collections_map = {}
for collection in cs2_collections:
    collections_map[collection[1]] = collection[0]

with open('item_names.txt', encoding="utf-8") as file_object:
    line = file_object.readline()
    counter = 0
    parser = URLParser()
    failure_count = 0
    while len(line) > 0 and failure_count < 3:
        try:
            item_id = line.split(':')[1].strip()
            item_name = line.split('(')[0].strip().replace('"', "")
            weapon_name = item_name.split("|")[0]
            skin_name = item_name.split("|")[1]
            item_condition = line.split('(')[1].split(')')[0]
            url = parser.parse(config["Steam_Market_Search_Address"], line)
            steam_store_page = urllib.request.urlopen(url).read().decode("utf-8")
            # steam_store_page = proxy_opener.open(url).read().decode("utf-8")
            g_rgAssets = re.findall(r'g_rgAssets = .*', steam_store_page)
            g_rgAssets = g_rgAssets[0].replace('g_rgAssets = ', '')
            g_rgAssets = g_rgAssets[:-2]
            loaded_json = json.loads(g_rgAssets)
            items = next(iter(loaded_json['730'].values()))
            first_item = next(iter(items.values()))
            description_idx = -1
            description_value = first_item["descriptions"][description_idx]["value"]
            while not collections_map.get(description_value) and -description_idx < len(first_item["descriptions"]):
                description_idx -= 1
                description_value = first_item["descriptions"][description_idx]["value"]

            collection = description_value
            rarity = first_item["type"].split(" ")[0]
            print(f"Successfully found data for skins with these details: {item_name} | {item_condition} | {item_id} | {collection} | {rarity} | Rarity Map Values: {rarity_map[rarity]}")

            price_data_url = f"https://steamcommunity.com/market/itemordershistogram?country=GB&language=english&currency=2&item_nameid={item_id[:-1]}"
            price_json = json.load(urllib.request.urlopen(price_data_url))

            buy = price_json["highest_buy_order"]
            sell = price_json["lowest_sell_order"]

            print(f"Fetched price data with buy: {buy} and sell: {sell}")


            insert_statement = f"INSERT INTO skins (FULL_NAME, STEAM_NAME_ID, WEAPON_NAME, SKIN_NAME, CONDITION, RARITY, CURRENT_BUY, CURRENT_SELL, COLLECTION) VALUES ('{item_name}', {item_id[:-1]},'{weapon_name}', '{skin_name}', '{item_condition}', {rarity_map[rarity]}, {buy}, {sell}, {collections_map[collection]})"
            print(f"Successfully inserted, completing {counter}/13,693")
            cursor.execute(insert_statement)
            cursor.commit()
            counter += 1
            line = file_object.readline()
            failure_count = 0
        except HTTPError as HttpExcept:
            print(f"Exception occurred while trying to request data on: {line}, Exception: {HttpExcept} - Waiting out cooldown period")
            failure_count += 1
            time.sleep(620)
        except Exception as exception:
            try:
                print(f"Exception occurred while trying to process: {line}, Exception: {exception}")
                file = open('failed_records.txt', "a")
                file.write(line)
                file.close()
            except:
                print("Could not output skin name to log file")
            counter += 1
            line = file_object.readline()
        finally:
            time.sleep(13)
        # run our query here to get rarity, current_buy, current_sell, collection etc

