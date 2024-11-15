class CSSkinType:
    def __init__(self, row):
        self.id = row[0]
        self.steam_item_id = row[1]
        self.full_name = row[2]
        self.weapon_name = row[3]
        self.skin_name = row[4]
        self.wear_text = row[5]
        self.rarity = row[6]
        self.current_buy = row[7]
        self.current_sell = row[8]
        self.collection_id = row[9]
        self.min_float = row[10]
        self.max_float = row[11]

    def __lt__(self, other):
        return self.id > other.id

class CSSkinInstance:
    def __init__(self, weapon_name: str, skin_name: str, rarity: int, wear_float: float, collection_id: int):
        self.weapon_name = weapon_name
        self.skin_name = skin_name
        self.collection_id = collection_id
        self.rarity = rarity
        self.wear_float = wear_float
