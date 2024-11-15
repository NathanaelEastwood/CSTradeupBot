import json
from ctypes import c_ushort

import pyodbc
import heapq

from SkinObject import CSSkinType

condition_list = ["Battle-Scarred", "Well-Worn", "Field-Tested", "Minimal Wear", "Factory New"]

with open('config.json', 'r') as file:
    config = json.load(file)

def openSQLConnection():
    SERVER = config["DB_Server"]
    DATABASE = "CounterSkins"
    PORT = config["DB_Port"]
    cnxn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};PORT={PORT};Trusted_Connection=Yes')
    return cnxn

cursor = openSQLConnection().cursor()

def get_collections():
    sql = "SELECT * FROM collections"
    cursor.execute(sql)
    cs2_collections = cursor.fetchall()
    collections_map = {}
    for collection in cs2_collections:
        collections_map[collection[1]] = collection[0]

    return collections_map

def get_skins_with_rarity_and_condition(rarity: int, condition: str):
    sql = f"SELECT * FROM skins2 WHERE RARITY = {rarity} AND CONDITION = '{condition}'"
    cursor.execute(sql)
    skins = cursor.fetchall()
    result = []
    for skin in skins:
        result.append(CSSkinType(skin))
    return result

def get_skins_from_collection_with_rarity_and_condition(rarity: int, condition: str, collection: int):
    sql = f"SELECT * FROM skins2 WHERE RARITY = {rarity} AND CONDITION = '{condition}' AND COLLECTION = {collection}"
    cursor.execute(sql)
    skins = cursor.fetchall()
    result = []
    for skin in skins:
        result.append(CSSkinType(skin))
    return result

def get_skins_from_collection_with_rarity(collection: int, rarity: int):
    sql = f"SELECT * FROM skins2 WHERE RARITY = {rarity} AND COLLECTION = {collection}"
    cursor.execute(sql)
    skins = cursor.fetchall()
    result = []
    for skin in skins:
        result.append(CSSkinType(skin))
    return result

def get_highest_ratios(collections_map, quantity_to_return):
    result = []
    heapq.heapify(result)
    for collection in collections_map.keys():
        for rarity in range(0, 5):
            for i in range(len(condition_list) - 1):
                low_skins = get_skins_from_collection_with_rarity_and_condition(rarity, condition_list[i], collections_map[collection])
                high_skins = get_skins_from_collection_with_rarity_and_condition(rarity + 1, condition_list[i], collections_map[collection])
                if len(low_skins) > 0 and len(high_skins) > 0:
                    cheapest_intake = min(low_skins, key=lambda x: x.current_sell)
                    most_expensive_output = max(high_skins, key=lambda x: x.current_buy)
                    ratio = (cheapest_intake.current_sell * 10) / most_expensive_output.current_buy
                    # for now, compare similar wear (need to implement wear factor)
                    # a tradeup ratio of 1 means for rarity y, price(y) * 10 = price(y + 1)
                    # i.e. lower_rarity * 10/higher_rarity (lower is better)
                    try:
                        heapq.heappush(result, (-ratio, (cheapest_intake, most_expensive_output)))
                    except Exception as ex:
                        print(f"Error trying to HEAPQ PUSH, {ratio}, Exception: {ex}")
    return heapq.nlargest(quantity_to_return, result)

def read_output(input_list):
    for i in range(10):
        print(f"Trade up with ratio {input_list[i][0]} found between intake {input_list[i][1][0].full_name} and output: {input_list[i][1][1].full_name} on condition: {input_list[i][1][1].wear_text}")

def find_filler_collection_for_rarity(rarity):
    collections = get_collections()
    result = []
    heapq.heapify(result)
    for collection in collections:
        skins = get_skins_from_collection_with_rarity(collections[collection], rarity)
        if len(skins) > 0:
            heapq.heappush(result, (-len(skins), collection))

    best_fillers = heapq.nlargest(5, result)
    for filler in best_fillers:
        print(f"Found filler from collection: {filler[1]}, with {-filler[0]} skins in it.")

collections = get_collections()
read_output(get_highest_ratios(collections, 10))
