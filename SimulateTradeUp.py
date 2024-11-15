import json
import pyodbc

from SkinObject import CSSkinInstance, CSSkinType

wear_breakpoints = {
    0.07 : "Factory New",
    0.15 : "Minimal Wear",
    0.38 : "Field-Tested",
    0.45 : "Well-Worn",
    1 : "Battle-Scarred",
}

with open('config.json', 'r') as file:
    config = json.load(file)

def openSQLConnection():
    SERVER = config["DB_Server"]
    DATABASE = "CounterSkins"
    PORT = config["DB_Port"]
    cnxn = pyodbc.connect(
    f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};PORT={PORT};Trusted_Connection=Yes')
    return cnxn.cursor()


def calculate_wear_from_float(wear_float: float):
    resultant_wear = ""
    keys = list(wear_breakpoints.keys())
    for i in range(0, 4):
        if keys[i + 1] > wear_float:
            resultant_wear = wear_breakpoints[keys[i + 1]]
            break

    return resultant_wear

def get_skins_from_collection_with_rarity(collection_id: int, rarity: int, cursor):
    sql = f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY SKIN_NAME ORDER BY ID) AS row_num FROM skins2 WHERE COLLECTION = {collection_id} AND RARITY = {rarity}) t WHERE row_num = 1;"
    cursor.execute(sql)
    skins = cursor.fetchall()
    result = []
    for skin in skins:
        result.append(CSSkinType(skin))
    return result

def get_skins_with_weapon_name_skin_name_and_wear(weapon_name: str, skin_name: str, wear: str, cursor):
    skin_name = skin_name.replace("'", "'")
    sql = f"SELECT TOP (1) * FROM skins2 WHERE WEAPON_NAME = '{weapon_name}' AND SKIN_NAME = '{skin_name}' AND CONDITION = '{wear}'"
    cursor.execute(sql)
    skin = cursor.fetchall()
    result = CSSkinType(skin[0])

    return result

def simulate(input_skins: [CSSkinInstance]):
    cursor = openSQLConnection()
    collections_frequency_map = {}
    overall_rarity = input_skins[0].rarity
    total_float = 0
    input_cost = 0
    for skin in input_skins:
        wear = calculate_wear_from_float(skin.wear_float)
        total_float += skin.wear_float
        input_cost += get_skins_with_weapon_name_skin_name_and_wear(skin.weapon_name, skin.skin_name, wear, cursor).current_sell
        if collections_frequency_map.get(skin.collection_id) is None:
            collections_frequency_map[skin.collection_id] = 1
        else:
            collections_frequency_map[skin.collection_id] += 1

    avg_float = total_float/10
    total_outcomes = 0
    outcome_skins = []

    for included_collection in collections_frequency_map.keys():
        skins = get_skins_from_collection_with_rarity(included_collection, overall_rarity + 1, cursor)
        total_outcomes += len(skins) * collections_frequency_map[included_collection]
        outcome_skins.extend(skins)

    # calculate the float/wear of each outcome and therefore price
    overall_profitability = 0
    for skin in outcome_skins:
        outcome_float = avg_float * (skin.max_float - skin.min_float) + skin.min_float
        resultant_wear = calculate_wear_from_float(outcome_float)
        resultant_skin = get_skins_with_weapon_name_skin_name_and_wear(skin.weapon_name, skin.skin_name, resultant_wear, cursor)
        skin_probability = collections_frequency_map[skin.collection_id] / total_outcomes
        skin_profitability = resultant_skin.current_buy - input_cost
        overall_profitability += skin_profitability * skin_probability
        print(f"{skin.weapon_name} | {skin.skin_name} | {resultant_wear} with this profitability: {skin_profitability} at probability {skin_probability} with a float of {outcome_float}")

    print(f"Overall Profitability: {overall_profitability}")

skin1 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.065, 6)
skin2 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.065, 6)
skin3 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.065, 6)
skin4 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.065, 6)
skin5 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.065, 6)
skin6 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.79, 6)
skin7 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.79, 6)
skin8 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.79, 6)
skin9 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.79, 6)
skin10 = CSSkinInstance("XM1014", "Blue Spruce", 0, 0.79, 6)

input = [skin1, skin2, skin3, skin4, skin5, skin6, skin7, skin8, skin9, skin10]

simulate(input)










