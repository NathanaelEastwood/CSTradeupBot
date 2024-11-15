DROP TABLE IF EXISTS rarities
DROP TABLE IF EXISTS skins
DROP TABLE IF EXISTS skins2
DROP TABLE IF EXISTS collections

create table collections(
	ID INT IDENTITY(1, 1) PRIMARY KEY,
	COLLECTION_NAME varchar(255) UNIQUE
)

CREATE TABLE skins2 (
	ID int IDENTITY(1, 1) PRIMARY KEY,
    STEAM_NAME_ID bigint,
	FULL_NAME varchar(255),
	WEAPON_NAME varchar(255),
	SKIN_NAME varchar(255),
    CONDITION varchar(255),
	RARITY int,
	CURRENT_BUY float,
	CURRENT_SELL float,
	COLLECTION int FOREIGN KEY REFERENCES collections(ID),
    MIN_FLOAT float,
    MAX_FLOAT float
)

create table skins (
	ID int IDENTITY(1, 1) PRIMARY KEY,
    STEAM_NAME_ID bigint,
	FULL_NAME varchar(255),
	WEAPON_NAME varchar(255),
	SKIN_NAME varchar(255),
    CONDITION varchar(255),
	RARITY int,
	CURRENT_BUY float,
	CURRENT_SELL float,
	COLLECTION int FOREIGN KEY REFERENCES collections(ID)
)

create table rarities (
    VALUE INT PRIMARY KEY,
    TEXT VARCHAR(255)
)