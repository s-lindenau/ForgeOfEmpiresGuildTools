#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
import os.path
import tempfile
import zipfile

from model.database import Database
from model.players import Players

# Change to DEBUG for more verbose output
LOG_LEVEL = logging.INFO

GUILD_MEMBER_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_GuildMemberStat"
GUILD_MEMBER_STATS_PLAYER_TABLE = "player"

GUILD_EXPEDITION_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_GexStat"
GUILD_EXPEDITION_PARTICIPATION_TABLE = "participation"
GUILD_EXPEDITION_PARTICIPANTS_ROWS = "participants"
GUILD_EXPEDITION_RANKING_TABLE = "ranking"
GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY = "gexweek"

GUILD_BUILDINGS_KEY = "guildbuildings"
GREAT_BUILDINGS_KEY = "greatbuildings"
GREAT_BUILDING_THE_ARC = "The Arc"
GREAT_BUILDING_OBSERVATORY = "Observatory"
GREAT_BUILDING_ATOMIUM = "Atomium"

# todo make configurable or detect from data
FOE_LANGUAGE_DEFAULT = "en"
PLAYER_PROFILE_LINK_TEMPLATE = "https://foestats.com/{language}/{server}/players/profile/?server={server}&world={world}&id={player_id}"

DEFAULT_SCORE_ZERO = 0


def read_foe_data(zip_path: str) -> dict[str, any]:
    """
    Reads FoE data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).
        Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        dict: A dictionary of FoE data including server information and players.
    """

    foe_server_info = {
        "language": FOE_LANGUAGE_DEFAULT,
        "server": "",
        "world": "",
        "guild_id": "",
        "guild_name": "",
    }

    foe_player_data = read_players(zip_path, foe_server_info)

    foe_tools_data = {
        "player_profile_link_template": PLAYER_PROFILE_LINK_TEMPLATE,
        "server_info": foe_server_info,
        "players": foe_player_data.get_all_players(),
    }
    return foe_tools_data


def read_players(zip_path: str, server_info: dict) -> Players:
    """
    Reads player data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).

    Args:
        zip_path (str): Path to the ZIP file.
        server_info (dict): A dictionary to store server information (language, server, world).

    Returns:
        Players: An instance of the Players class containing player data.
    """

    players_from_file = Players()
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

        # Guild members list
        guild_member_stats_path = find_file_path_with_substring(temp_dir, GUILD_MEMBER_STATS_FILE_NAME_SUBSTRING)
        if guild_member_stats_path is None:
            logging.error(f"Could not find the {GUILD_MEMBER_STATS_FILE_NAME_SUBSTRING} JSON file in the ZIP.")
            return players_from_file

        try:
            logging.info(f"Processing extracted file: {guild_member_stats_path}")
            process_guild_members_file(guild_member_stats_path, players_from_file)
        except Exception as e:
            logging.error(f"Failed to process file {guild_member_stats_path}: {e}", exc_info=e)

        # Guild expedition stats, also has general information on Guild Name and Server name
        guild_expedition_stats_path = find_file_path_with_substring(temp_dir, GUILD_EXPEDITION_STATS_FILE_NAME_SUBSTRING)
        if guild_expedition_stats_path is None:
            logging.error(f"Could not find the {GUILD_EXPEDITION_STATS_FILE_NAME_SUBSTRING} JSON file in the ZIP.")
            return players_from_file

        try:
            logging.info(f"Processing extracted file: {guild_expedition_stats_path}")
            process_guild_expedition_file(guild_expedition_stats_path, players_from_file, server_info)
        except Exception as e:
            logging.error(f"Failed to process file {guild_expedition_stats_path}: {e}", exc_info=e)

    return players_from_file


def process_guild_members_file(guild_member_stats_path, players_from_file: Players):
    # Load the JSON data from the file
    with open(guild_member_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    players_table = database.get_table(GUILD_MEMBER_STATS_PLAYER_TABLE)

    for row in players_table.rows:
        player_rank_in_guild = row.get("rank")[1]   # array of size 2: [previous rank, current rank]
        player_id = row.get("player_id")
        player_name = row.get("name")
        player_age = row.get("era")
        player_deleted_date = row.get("deleted")    # timestamp of when deleted, 0 when still active in guild
        logging.debug(f"Processing player: {player_id}")

        if player_deleted_date > 0:
            # deleted players are no longer relevant for the guild
            continue

        great_buildings = row.get(GREAT_BUILDINGS_KEY)
        arc = get_great_building_by_name(great_buildings, GREAT_BUILDING_THE_ARC)
        observatory = get_great_building_by_name(great_buildings, GREAT_BUILDING_OBSERVATORY)
        atomium = get_great_building_by_name(great_buildings, GREAT_BUILDING_ATOMIUM)

        # TODO: guild buildings appear twice: once with a "power" entry and once with a "resources":"goods" entry. Great buildings are also in this list!
        guild_buildings = row.get(GUILD_BUILDINGS_KEY)
        # todo: process guild buildings

        parsed_player_data = {
            "Age": player_age,
            "id": player_rank_in_guild,
            "player_id": player_id,
            "Arc": get_great_building_level(arc),
            "Observatory": get_great_building_level(observatory),
            "Atomium": get_great_building_level(atomium),
            "ExpeditionStats": get_expedition_stats(),
            "ExpeditionStatsPrevious": get_expedition_stats()
        }
        players_from_file.add_player(player_id, player_name, parsed_player_data)


def process_guild_expedition_file(guild_expedition_stats_path, players_from_file: Players, server_info: dict):
    # Load the JSON data from the file
    with open(guild_expedition_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    expedition_participation_table = database.get_table(GUILD_EXPEDITION_PARTICIPATION_TABLE)
    expedition_weeks_sorted_desc = get_sorted_gexweek_values(expedition_participation_table)

    if len(expedition_weeks_sorted_desc) < 1:
        logging.warning("No guild expedition participation found in file")
        return

    # Look back up to 2 expedition weeks (current, previous) for stats
    current_expedition_week = expedition_weeks_sorted_desc[1]
    previous_expedition_week = 0
    if len(expedition_weeks_sorted_desc) > 1:
        previous_expedition_week = expedition_weeks_sorted_desc[2]

    current_guild_expedition_week_stats = next((r for r in expedition_participation_table.rows if r.get(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY) == current_expedition_week), None)
    previous_guild_expedition_week_stats = next((r for r in expedition_participation_table.rows if r.get(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY) == previous_expedition_week), None)

    guild_id = current_guild_expedition_week_stats.get("currentGuildID")
    get_guild_expedition_stats_for_players(players_from_file, "ExpeditionStats", current_guild_expedition_week_stats)
    get_guild_expedition_stats_for_players(players_from_file, "ExpeditionStatsPrevious", previous_guild_expedition_week_stats)

    expedition_ranking_table = database.get_table(GUILD_EXPEDITION_RANKING_TABLE)
    row = next((r for r in expedition_ranking_table.rows if r.get(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY) == current_expedition_week), None)
    if row is None:
        logging.error("Could not find Guild and Server information in Guild Expedition Ranking table")
        return

    for participant in row.get(GUILD_EXPEDITION_PARTICIPANTS_ROWS, []):
        # Find the current guild, other guilds participating in the expedition are not relevant
        if participant.get("guildId", 0) == guild_id:
            server_info["server"] = participant.get("worldId", "")
            server_info["world"] = participant.get("worldName", "")
            server_info["guild_id"] = guild_id
            server_info["guild_name"] = participant.get("name", "")
            logging.info(f"Found current guild in server: {server_info}")
            break


def get_guild_expedition_stats_for_players(players_from_file, expedition_stats_key: str, row):
    if row is None:
        return

    for participant in row.get(GUILD_EXPEDITION_PARTICIPATION_TABLE, []):
        # add guild expedition stats for player
        player_id = participant.get("player_id")
        logging.debug(f"Processing guild expedition participant: {player_id}")

        points = participant.get("expeditionPoints", DEFAULT_SCORE_ZERO)
        solved_encounters = participant.get("solvedEncounters", DEFAULT_SCORE_ZERO)
        trial = participant.get("trial", DEFAULT_SCORE_ZERO)

        player_by_id = players_from_file.get_player_by_id(player_id)
        # removed players can still be in the expedition stats, but we don't need their data anymore
        if player_by_id is not None:
            player_by_id[expedition_stats_key] = get_expedition_stats(points, solved_encounters, trial)


def parse_database(dexie_db) -> Database:
    if "data" in dexie_db and "data" in dexie_db["data"]:
        format_name = dexie_db["formatName"]
        format_version = dexie_db["formatVersion"]
        database_name = dexie_db["data"]["databaseName"]
        database_version = dexie_db["data"]["databaseVersion"]
        logging.info(f"Reading format: {format_name}, format version: {format_version}, database name: {database_name} and database version: {database_version}")
        database = Database(format_name, format_version, database_name, database_version)
        parse_tables(database, dexie_db)
        return database
    else:
        logging.error("No 'data' key found in the JSON structure!")
        return Database("", "", "", 0)


def parse_tables(database, dexie_db):
    for table in dexie_db["data"]["data"]:
        table_name = table["tableName"]
        rows = table["rows"]
        database.add_table(table_name, rows)
        logging.info(f"Added table '{table_name}' with {len(rows)} rows.")


def find_file_path_with_substring(directory, substring):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if substring in file:
                return os.path.join(root, file)
    return None


def get_great_building_by_name(buildings, building_name):
    if buildings is None:
        return None
    for building in buildings:
        if building.get("name") == building_name:
            return building
    return None


def get_guild_buildings_by_name(buildings, building_name, is_exact_name_match=True):
    if buildings is None:
        return None

    guild_buildings = buildings["buildings"]
    if guild_buildings is None:
        return None

    guild_buildings_by_name = []
    for building in guild_buildings:
        if is_exact_name_match:
            if building.get("name") == building_name:
                guild_buildings_by_name.append(building)
        else:
            if building.get("name").startswith(building_name):
                guild_buildings_by_name.append(building)
    return guild_buildings_by_name


def get_great_building_level(building):
    if building is None:
        return 0
    return building.get("level", 0)


def get_guild_buildings(buildings):
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


def get_expedition_stats(points: int = DEFAULT_SCORE_ZERO, solved_encounters: int = DEFAULT_SCORE_ZERO, trial: int = DEFAULT_SCORE_ZERO):
    return {
        "Points": points,
        "SolvedEncounters": solved_encounters,
        "Trial": trial
    }


def get_sorted_gexweek_values(expedition_participation_table):
    """
    Extracts all 'gexweek' values from the rows of the expedition_participation_table
    and sorts them in descending order.

    Args:
        expedition_participation_table: A table object containing rows with 'gexweek' keys.

    Returns:
        list: A list of sorted 'gexweek' values in descending order.
    """
    gexweek_values = [row.get(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY) for row in expedition_participation_table.rows if GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY in row]
    return sorted(gexweek_values, reverse=True)


def format_profile_link_template(foe_data, current_player):
    link_template = foe_data.get("player_profile_link_template", "")
    server_info = foe_data.get("server_info", {})
    return link_template.format(
        language=server_info.get("language", ""),
        server=server_info.get("server", ""),
        world=server_info.get("world", ""),
        player_id=current_player.get("player_id", ""))


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_foe_helper_export_zip_file>")
        sys.exit(1)

    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=LOG_LEVEL,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    zip_path_command_line_argument = sys.argv[1]
    players = read_players(zip_path_command_line_argument, {})
    player_data = players.get_all_players()
    for player in player_data:
        logging.info(f"Player: {player}: {player_data[player]}")

    logging.info(f" --- Total players found: {len(player_data)} --- ")
