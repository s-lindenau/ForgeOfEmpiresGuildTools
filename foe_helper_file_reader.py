#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
import os.path
import tempfile
import zipfile

GUILD_MEMBER_STATS_SUBSTRING = "FoeHelperDB_GuildMemberStat"
PLAYER_TABLE = "player"
GREAT_BUILDINGS_KEY = "greatbuildings"
GREAT_BUILDING_THE_ARC = "The Arc"
GREAT_BUILDING_OBSERVATORY = "Observatory"
GREAT_BUILDING_ATOMIUM = "Atomium"
STATUE_NAME = "Statue of Honor - Lv."

# todo make configurable
FOE_LANGUAGE = "en"
FOE_SERVER = "en20"
FOE_WORLD_NAME = "Vingrid"
PLAYER_PROFILE_LINK_TEMPLATE = "https://foestats.com/{language}/{server}/players/profile/?server={server}&world={world}&id={player_id}"

logging.basicConfig(level=logging.INFO)


def read_foe_data(zip_path: str) -> dict[str, any]:
    """
    Reads FoE data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).
        Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        dict: A dictionary of FoE data including server, world name, and players.
    """

    foe_tools_data = {
        "language": FOE_LANGUAGE,
        "server": FOE_SERVER,
        "world": FOE_WORLD_NAME,
        "player_profile_link_template": PLAYER_PROFILE_LINK_TEMPLATE,
        "players": read_players(zip_path)
    }
    return foe_tools_data


def read_players(zip_path: str) -> dict[str, dict]:
    """
    Reads player data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).

    Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        dict: A dictionary of player data.
    """

    players_from_file = {}
    logging.info(f"Processing file: {zip_path}")

    is_zip = zipfile.is_zipfile(zip_path)
    if not is_zip:
        logging.error(f"The file {zip_path} is not a valid ZIP file.")
        return players_from_file

    # Extract all files to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:

        logging.info(f"Extracting ZIP contents to temporary directory: {temp_dir}")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        guild_member_stats_path = find_file_path_with_substring(temp_dir, GUILD_MEMBER_STATS_SUBSTRING)
        if guild_member_stats_path is None:
            logging.error(f"Could not find the {GUILD_MEMBER_STATS_SUBSTRING} JSON file in the ZIP.")
            return players_from_file

        try:
            logging.info(f"Processing extracted file: {guild_member_stats_path}")
            # Load the JSON data from the file
            with open(guild_member_stats_path, mode="r", encoding="utf-8") as file:
                dexie_db = json.load(file)

            database = extract_database(dexie_db)
            players_table = extract_table(database, PLAYER_TABLE)

            for row in players_table["rows"]:
                player_guild_id = row.get("id")
                player_id = row.get("player_id")
                player_name = row.get("name")
                player_age = row.get("era")
                logging.debug(f"Processing player: {player_id}")

                great_buildings = row.get(GREAT_BUILDINGS_KEY)
                arc = extract_great_building_by_name(great_buildings, GREAT_BUILDING_THE_ARC)
                observatory = extract_great_building_by_name(great_buildings, GREAT_BUILDING_OBSERVATORY)
                atomium = extract_great_building_by_name(great_buildings, GREAT_BUILDING_ATOMIUM)

                # TODO: guild buildings appear twice: once with a "power" entry and once with a "resources":"goods" entry. Great buildings are also in this list!
                guild_buildings = row.get("guildbuildings")
                statue = extract_guild_buildings_by_name(guild_buildings, STATUE_NAME, False)

                players_from_file[player_name] = {
                    "Age": player_age,
                    "id": player_guild_id,
                    "player_id": player_id,
                    "Arc": extract_great_building_level(arc),
                    "Observatory": extract_great_building_level(observatory),
                    "Atomium": extract_great_building_level(atomium),
                    "Statue": extract_guild_buildings(statue),
                }

        except Exception as e:
            logging.error(f"Failed to process file {guild_member_stats_path}: {e}", exc_info=e)

    return players_from_file


def extract_database(dexie_db):
    if "data" in dexie_db:
        format_name = dexie_db["formatName"]
        database_name = dexie_db["data"]["databaseName"]
        logging.info(f"Reading database format: {format_name}, database name: {database_name}")
        return dexie_db["data"]["data"]
    else:
        logging.error("No 'data' key found in the JSON structure!")
        return {}


def extract_table(database, table_name):
    for table in database:
        if table.get("tableName") == table_name:
            return table
    else:
        logging.error(f"Table '{table_name}' not found in the database!")
        return {
            "rows": []
        }


def find_file_path_with_substring(directory, substring):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if substring in file:
                return os.path.join(root, file)
    return None


def extract_great_building_by_name(buildings, building_name):
    if buildings is None:
        return None
    for building in buildings:
        if building.get("name") == building_name:
            return building
    return None


def extract_guild_buildings_by_name(buildings, building_name, exact=True):
    if buildings is None:
        return None

    guild_buildings = buildings["buildings"]
    if guild_buildings is None:
        return None

    guild_buildings_by_name = []
    for building in guild_buildings:
        if exact:
            if building.get("name") == building_name:
                guild_buildings_by_name.append(building)
        else:
            if building.get("name").startswith(building_name):
                guild_buildings_by_name.append(building)
    return guild_buildings_by_name


def extract_great_building_level(building):
    if building is None:
        return 0
    return building.get("level", 0)


def extract_guild_buildings(buildings):
    guild_buildings = []
    if buildings is not None:
        for building in buildings:
            guild_buildings.append(
                {
                    "Age": building["era"],
                    "Level": building["level"]
                }
            )
    return guild_buildings


def format_profile_link_template(foe_data, current_player):
    link_template = foe_data.get("player_profile_link_template", "")
    return link_template.format(
        language = foe_data.get("language", ""),
        server = foe_data.get("server", ""),
        world = foe_data.get("world", ""),
        player_id = current_player.get("player_id", ""))


if __name__ == '__main__':
    import sys

    if sys.argv.__len__() != 2:
        print(f"Usage: {sys.argv[0]} <path_to_foe_helper_export_zip_file>")
        sys.exit(1)

    zip_path_command_line_argument = sys.argv[1]
    players = read_players(zip_path_command_line_argument)
    logging.info(f" --- Total players found: {len(players)} --- ")
    for player in players:
        logging.info(f"Player: {player}: {players[player]}")
