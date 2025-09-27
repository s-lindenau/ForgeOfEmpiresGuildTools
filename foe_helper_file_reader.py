#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
import os.path
import random
import tempfile
import zipfile

from model.database import Database, Table
from model.players import Players
from model.foe_guild_tools_data import GuildInfo, FoeGuildToolsData
from util.application import application_data

# Change to DEBUG for more verbose output
LOG_LEVEL = logging.INFO

GUILD_MEMBER_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_GuildMemberStat"
GUILD_MEMBER_STATS_PLAYER_TABLE = "player"
GUILD_MEMBER_STATS_FORUM_TABLE = "forum"

GUILD_BUILDINGS_KEY = "guildbuildings"
GUILD_BUILDINGS_BUILDINGS_KEY = "buildings"

GREAT_BUILDINGS_KEY = "greatbuildings"
GREAT_BUILDING_THE_ARC = "The Arc"

GUILD_EXPEDITION_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_GexStat"
GUILD_EXPEDITION_PARTICIPATION_TABLE = "participation"
GUILD_EXPEDITION_PARTICIPATION_ROWS = "participation"
GUILD_EXPEDITION_PARTICIPANTS_ROWS = "participants"
GUILD_EXPEDITION_RANKING_TABLE = "ranking"
GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY = "gexweek"        # This is the END date-time of the GE week

GUILD_BATTLEGROUNDS_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_GuildFights"
GUILD_BATTLEGROUNDS_PARTICIPATION_HISTORY_TABLE = "history"
GUILD_BATTLEGROUNDS_ROUND_DATE_TIME_EPOCH_KEY = "gbground"   # This is the END date-time of the GbG round
GUILD_BATTLEGROUNDS_PARTICIPATION_ROWS = "participation"

QUANTUM_INCURSION_STATS_FILE_NAME_SUBSTRING = "FoeHelperDB_Qi"
QUANTUM_INCURSION_PARTICIPATION_HISTORY_TABLE = "history"
QUANTUM_INCURSION_ROUND_DATE_TIME_EPOCH_KEY = "qiround"      # This is the END date-time of the Qi round
QUANTUM_INCURSION_PARTICIPATION_ROWS = "participation"

# todo make configurable or detect from data
FOE_LANGUAGE_DEFAULT = "en"
PLAYER_PROFILE_LINK_TEMPLATE = "https://foestats.com/{language}/{server}/players/profile/?server={server}&world={world}&id={player_id}"

DEFAULT_SCORE_ZERO = 0
DEFAULT_VALUE_ZERO = 0
UNKNOWN_VALUE = -1


def read_foe_data_from_zip(zip_path: str) -> FoeGuildToolsData:
    """
    Reads FoE data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).
        Args:
        zip_path (str): Path to the ZIP file.

    Returns:
        dict: A FoeGuildToolsData object with FoE data including guild information and players.
    """

    foe_guild_info = GuildInfo.from_dict({"language": FOE_LANGUAGE_DEFAULT})

    foe_player_data = read_players(zip_path, foe_guild_info)

    foe_tools_data = FoeGuildToolsData(
         PLAYER_PROFILE_LINK_TEMPLATE,
         foe_guild_info,
         foe_player_data
    )
    return foe_tools_data


def read_players(zip_path: str, guild_info: GuildInfo) -> Players:
    """
    Reads player data from a ZIP file exported from FoE-Helper (containing IndexedDB data as json files).

    Args:
        zip_path (str): Path to the ZIP file.
        guild_info (GuildInfo): A GuildInfo object to store guild information (name, language, server, world).

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
            process_guild_expedition_file(guild_expedition_stats_path, players_from_file, guild_info)
        except Exception as e:
            logging.error(f"Failed to process file {guild_expedition_stats_path}: {e}", exc_info=e)

        # Guild Battlegrounds stats
        guild_battlegrounds_stats_path = find_file_path_with_substring(temp_dir, GUILD_BATTLEGROUNDS_STATS_FILE_NAME_SUBSTRING)
        if guild_battlegrounds_stats_path is None:
            logging.error(f"Could not find the {GUILD_BATTLEGROUNDS_STATS_FILE_NAME_SUBSTRING} JSON file in the ZIP.")
            return players_from_file

        try:
            logging.info(f"Processing extracted file: {guild_battlegrounds_stats_path}")
            process_guild_battlegrounds_file(guild_battlegrounds_stats_path, players_from_file)
        except Exception as e:
            logging.error(f"Failed to process file {guild_battlegrounds_stats_path}: {e}", exc_info=e)

        # Quantum Incursion stats
        quantum_incursion_stats_path = find_file_path_with_substring(temp_dir, QUANTUM_INCURSION_STATS_FILE_NAME_SUBSTRING)
        if quantum_incursion_stats_path is None:
            logging.error(f"Could not find the {QUANTUM_INCURSION_STATS_FILE_NAME_SUBSTRING} JSON file in the ZIP.")
            return players_from_file

        try:
            logging.info(f"Processing extracted file: {quantum_incursion_stats_path}")
            process_quantum_incursion_file(quantum_incursion_stats_path, players_from_file)
        except Exception as e:
            logging.error(f"Failed to process file {quantum_incursion_stats_path}: {e}", exc_info=e)

    return players_from_file


def process_guild_members_file(guild_member_stats_path, players_from_file: Players):
    # Load the JSON data from the file
    with open(guild_member_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    players_table = database.get_table(GUILD_MEMBER_STATS_PLAYER_TABLE)

    for row in players_table.rows:
        player_rank_in_guild = row.get("rank", [UNKNOWN_VALUE, UNKNOWN_VALUE])[1]   # array of size 2: [previous rank, current rank]
        player_id = row.get("player_id", UNKNOWN_VALUE)
        if application_data.get("anonymized") is True:
            player_name = "Player-"+str(random.randrange(80))+str(random.randrange(80))
        else:
            player_name = row.get("name", "")
        player_age = row.get("era", "")
        player_deleted_date = row.get("deleted", UNKNOWN_VALUE)    # timestamp of when deleted, 0 when still active in guild
        logging.debug(f"Processing player: {player_id}")

        if player_deleted_date != 0:
            # deleted players are no longer relevant for the guild
            continue

        great_buildings = row.get(GREAT_BUILDINGS_KEY, None)
        arc = get_great_building_by_name(great_buildings, GREAT_BUILDING_THE_ARC)

        parsed_player_data = {
            "Age": player_age,
            "id": player_rank_in_guild,
            "player_id": player_id,
            "player_name": player_name,
            "Arc": get_great_building_level(arc),
            "ForumParticipation": DEFAULT_SCORE_ZERO,
            "ExpeditionHighestTrial": DEFAULT_SCORE_ZERO,
            "ExpeditionStats": {},
            "ExpeditionStatsPrevious": {},
            "BattleGroundsStats": {},
            "BattleGroundsStatsPrevious": {},
            "QuantumIncursionStats": {},
            "QuantumIncursionStatsPrevious": {},
            "GreatBuildings": {},
            "GuildBuildings": {},
        }
        players_from_file.add_player(player_id, player_name, parsed_player_data)

        process_all_great_buildings(player_id, players_from_file, great_buildings)
        guild_buildings = row.get(GUILD_BUILDINGS_KEY, None)
        process_all_guild_buildings(player_id, players_from_file, guild_buildings)

    forum_table = database.get_table(GUILD_MEMBER_STATS_FORUM_TABLE)
    for row in forum_table.rows:
        # add forum stats for player
        player_id = row.get("player_id", UNKNOWN_VALUE)
        player_by_id = players_from_file.get_player_by_id(player_id)
        # removed players can still be in the stats, but we don't need their data anymore
        if player_by_id is not None:
            messages = row.get("message_id", [])
            message_count = len(messages)
            player_by_id["ForumParticipation"] = message_count


def process_all_guild_buildings(player_id, players_from_file: Players, guild_buildings):
    if guild_buildings is None:
        return

    player_from_file = players_from_file.get_player_by_id(player_id)
    for guild_building in guild_buildings.get("buildings", []):
        guild_building_id = guild_building.get("gbid", DEFAULT_VALUE_ZERO)
        player_guild_building = player_from_file.get("GuildBuildings").get(guild_building_id, {})

        guild_building_name = guild_building.get("name", "Unknown")
        guild_building_level = guild_building.get("level", DEFAULT_VALUE_ZERO)
        player_guild_building["Name"] = guild_building_name
        player_guild_building["Level"] = guild_building_level

        guild_building_power = guild_building.get("power", None)
        if guild_building_power is not None:
            player_guild_building["PowerValue"] = guild_building_power.get("value", DEFAULT_VALUE_ZERO)

        guild_building_resources = guild_building.get("resources", None)
        if guild_building_resources is not None:
            player_guild_building["TotalGoods"] = guild_building_resources.get("totalgoods", DEFAULT_VALUE_ZERO)

        player_from_file.get("GuildBuildings")[guild_building_id] = player_guild_building


def process_all_great_buildings(player_id, players_from_file: Players, great_buildings):
    if great_buildings is None:
        return

    player_from_file = players_from_file.get_player_by_id(player_id)
    for great_building in great_buildings:
        great_building_name = great_building.get("name", "Unknown")
        player_from_file.get("GreatBuildings")[great_building_name] = great_building.get("level", DEFAULT_VALUE_ZERO)


def process_guild_expedition_file(guild_expedition_stats_path, players_from_file: Players, guild_info: GuildInfo):
    # Load the JSON data from the file
    with open(guild_expedition_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    expedition_participation_table = database.get_table(GUILD_EXPEDITION_PARTICIPATION_TABLE)
    expedition_weeks_sorted_desc = expedition_participation_table.get_sorted_values_from_rows_by_key(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY)

    if len(expedition_weeks_sorted_desc) < 1:
        logging.warning("No guild expedition participation found in file")
        return

    # Look back up to 2 expedition weeks (current, previous) for stats
    current_expedition_week = expedition_weeks_sorted_desc[0]
    previous_expedition_week = 0
    if len(expedition_weeks_sorted_desc) > 1:
        previous_expedition_week = expedition_weeks_sorted_desc[1]

    current_guild_expedition_week_stats = expedition_participation_table.get_row_where_key_matches_value(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY, current_expedition_week)
    previous_guild_expedition_week_stats = expedition_participation_table.get_row_where_key_matches_value(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY, previous_expedition_week)

    guild_id = current_guild_expedition_week_stats.get("currentGuildID", UNKNOWN_VALUE)
    get_guild_expedition_stats_for_players(players_from_file, "ExpeditionStats", current_guild_expedition_week_stats, current_expedition_week)
    get_guild_expedition_stats_for_players(players_from_file, "ExpeditionStatsPrevious", previous_guild_expedition_week_stats, previous_expedition_week)
    process_guild_expedition_highest_trial(players_from_file, expedition_participation_table)

    expedition_ranking_table = database.get_table(GUILD_EXPEDITION_RANKING_TABLE)
    row = next((r for r in expedition_ranking_table.rows if r.get(GUILD_EXPEDITION_WEEK_DATE_TIME_EPOCH_KEY) == current_expedition_week), None)
    if row is None:
        logging.error("Could not find Guild and Server information in Guild Expedition Ranking table")
        return

    for participant in row.get(GUILD_EXPEDITION_PARTICIPANTS_ROWS, []):
        # Find the current guild, other guilds participating in the expedition are not relevant
        if participant.get("guildId", DEFAULT_VALUE_ZERO) == guild_id:
            guild_info.server = participant.get("worldId", "")
            guild_info.world = participant.get("worldName", "")
            guild_info.guild_id = guild_id
            if application_data.get("anonymized") is True:
                guild_info.guild_name = '*' * len(participant.get("name", ""))
            else:
                guild_info.guild_name = participant.get("name", "")
            logging.info(f"Found current guild in server: {guild_info}")
            break


def get_guild_expedition_stats_for_players(players_from_file: Players, expedition_stats_key: str, row, expedition_week_timestamp: int):
    if row is None:
        return

    for participant in row.get(GUILD_EXPEDITION_PARTICIPATION_ROWS, []):
        # add guild expedition stats for player
        player_id = participant.get("player_id", UNKNOWN_VALUE)
        logging.debug(f"Processing guild expedition participant: {player_id}")

        player_by_id = players_from_file.get_player_by_id(player_id)
        # removed players can still be in the expedition stats, but we don't need their data anymore
        if player_by_id is not None:
            player_by_id[expedition_stats_key] = get_expedition_stats(expedition_week_timestamp, participant)


def process_guild_expedition_highest_trial(players_from_file: Players, expedition_participation_table: Table):
    for row in expedition_participation_table.rows:
        for participant in row.get(GUILD_EXPEDITION_PARTICIPATION_ROWS, []):
            # find the highest trial level per player
            player_id = participant.get("player_id", UNKNOWN_VALUE)
            player_by_id = players_from_file.get_player_by_id(player_id)
            # removed players can still be in the expedition stats, but we don't need their data anymore
            if player_by_id is not None:
                current_trial = participant.get("trial", DEFAULT_SCORE_ZERO)
                highest_trial = player_by_id.get("ExpeditionHighestTrial")
                if current_trial > highest_trial:
                    player_by_id["ExpeditionHighestTrial"] = current_trial


def process_guild_battlegrounds_file(guild_battlegrounds_stats_path, players_from_file: Players):
    # Load the JSON data from the file
    with open(guild_battlegrounds_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    battlegrounds_participation_table = database.get_table(GUILD_BATTLEGROUNDS_PARTICIPATION_HISTORY_TABLE)
    battlegrounds_rounds_sorted_desc = battlegrounds_participation_table.get_sorted_values_from_rows_by_key(GUILD_BATTLEGROUNDS_ROUND_DATE_TIME_EPOCH_KEY)

    # Look back up to 2 battlegrounds rounds (current, previous) for stats
    current_battlegrounds_round = battlegrounds_rounds_sorted_desc[0]
    previous_battlegrounds_round = 0
    if len(battlegrounds_rounds_sorted_desc) > 1:
        previous_battlegrounds_round = battlegrounds_rounds_sorted_desc[1]

    current_battlegrounds_round_stats = battlegrounds_participation_table.get_row_where_key_matches_value(GUILD_BATTLEGROUNDS_ROUND_DATE_TIME_EPOCH_KEY, current_battlegrounds_round)
    previous_battlegrounds_round_stats = battlegrounds_participation_table.get_row_where_key_matches_value(GUILD_BATTLEGROUNDS_ROUND_DATE_TIME_EPOCH_KEY, previous_battlegrounds_round)

    get_guild_battlegrounds_stats_for_players(players_from_file, "BattleGroundsStats", current_battlegrounds_round_stats, current_battlegrounds_round)
    get_guild_battlegrounds_stats_for_players(players_from_file, "BattleGroundsStatsPrevious", previous_battlegrounds_round_stats, previous_battlegrounds_round)


def get_guild_battlegrounds_stats_for_players(players_from_file: Players, battlegrounds_stats_key: str, row, battlegrounds_round_timestamp: int):
    if row is None:
        return

    for participant in row.get(GUILD_BATTLEGROUNDS_PARTICIPATION_ROWS, []):
        # add guild battlegrounds stats for player
        player_id = participant.get("player_id", UNKNOWN_VALUE)
        logging.debug(f"Processing guild battlegrounds participant: {player_id}")

        player_by_id = players_from_file.get_player_by_id(player_id)
        # removed players can still be in the battlegrounds stats, but we don't need their data anymore
        if player_by_id is not None:
            player_by_id[battlegrounds_stats_key] = get_battlegrounds_stats(battlegrounds_round_timestamp, participant)


def process_quantum_incursion_file(quantum_incursion_stats_path, players_from_file: Players):
    # Load the JSON data from the file
    with open(quantum_incursion_stats_path, mode="r", encoding="utf-8") as file:
        dexie_db = json.load(file)

    database = parse_database(dexie_db)
    quantum_incursion_participation_table = database.get_table(QUANTUM_INCURSION_PARTICIPATION_HISTORY_TABLE)
    quantum_incursion_rounds_sorted_desc = quantum_incursion_participation_table.get_sorted_values_from_rows_by_key(QUANTUM_INCURSION_ROUND_DATE_TIME_EPOCH_KEY)

    # Look back up to 2 quantum incursion rounds (current, previous) for stats
    current_quantum_incursion_round = quantum_incursion_rounds_sorted_desc[0]
    previous_quantum_incursion_round = 0
    if len(quantum_incursion_rounds_sorted_desc) > 1:
        previous_quantum_incursion_round = quantum_incursion_rounds_sorted_desc[1]

    current_quantum_incursion_round_stats = quantum_incursion_participation_table.get_row_where_key_matches_value(QUANTUM_INCURSION_ROUND_DATE_TIME_EPOCH_KEY, current_quantum_incursion_round)
    previous_quantum_incursion_round_stats = quantum_incursion_participation_table.get_row_where_key_matches_value(QUANTUM_INCURSION_ROUND_DATE_TIME_EPOCH_KEY, previous_quantum_incursion_round)

    get_quantum_incursion_stats_for_players(players_from_file, "QuantumIncursionStats", current_quantum_incursion_round_stats, current_quantum_incursion_round)
    get_quantum_incursion_stats_for_players(players_from_file, "QuantumIncursionStatsPrevious", previous_quantum_incursion_round_stats, previous_quantum_incursion_round)


def get_quantum_incursion_stats_for_players(players_from_file: Players, quantum_incursion_stats_key: str, row, quantum_incursion_round_timestamp: int):
    if row is None:
        return

    for participant in row.get(QUANTUM_INCURSION_PARTICIPATION_ROWS, []):
        # add quantum incursion stats for player
        player_id = participant.get("player_id", UNKNOWN_VALUE)
        logging.debug(f"Processing quantum incursion participant: {player_id}")

        player_by_id = players_from_file.get_player_by_id(player_id)
        # removed players can still be in the quantum incursion stats, but we don't need their data anymore
        if player_by_id is not None:
            player_by_id[quantum_incursion_stats_key] = get_quantum_incursion_stats(quantum_incursion_round_timestamp, participant)


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
        if building.get("name", "") == building_name:
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
            if building.get("name", "") == building_name:
                guild_buildings_by_name.append(building)
        else:
            if building.get("name", "").startswith(building_name):
                guild_buildings_by_name.append(building)
    return guild_buildings_by_name


def get_great_building_level(building):
    if building is None:
        return DEFAULT_VALUE_ZERO
    return building.get("level", DEFAULT_VALUE_ZERO)


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


def get_expedition_stats(expedition_week_timestamp: int, participant: dict):
    return {
        "ExpeditionWeekTimestamp": expedition_week_timestamp,
        "Rank": participant.get("rank", DEFAULT_SCORE_ZERO),
        "Points": participant.get("expeditionPoints", DEFAULT_SCORE_ZERO),
        "SolvedEncounters": participant.get("solvedEncounters", DEFAULT_SCORE_ZERO),
        "Trial": participant.get("trial", DEFAULT_SCORE_ZERO)
    }


def get_battlegrounds_stats(battlegrounds_round_timestamp: int, participant: dict):
    return {
        "BattleGroundsRoundTimestamp": battlegrounds_round_timestamp,
        "Rank": participant.get("rank", DEFAULT_SCORE_ZERO),
        "BattlesWon": participant.get("battlesWon", DEFAULT_SCORE_ZERO),
        "NegotiationsWon": participant.get("negotiationsWon", DEFAULT_SCORE_ZERO),
        "Attrition": participant.get("attrition", DEFAULT_SCORE_ZERO)
    }


def get_quantum_incursion_stats(quantum_incursion_round_timestamp: int, participant: dict):
    return {
        "QuantumIncursionRoundTimestamp": quantum_incursion_round_timestamp,
        "Rank": participant.get("rank", DEFAULT_SCORE_ZERO),
        "Actions": participant.get("actions", DEFAULT_SCORE_ZERO),
        "Progress": participant.get("progress", DEFAULT_SCORE_ZERO)
    }


def format_profile_link_template(foe_data: FoeGuildToolsData, current_player):
    link_template = foe_data.player_profile_link_template
    guild_info = foe_data.guild_info
    return link_template.format(
        language=guild_info.language,
        server=guild_info.server,
        world=guild_info.world,
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
    players = read_players(zip_path_command_line_argument, GuildInfo.from_dict({"language": FOE_LANGUAGE_DEFAULT}))
    player_data = players.get_all_players()
    for player in player_data:
        logging.info(f"Player: {player}: {player_data[player]}")

    logging.info(f" --- Total players found: {len(player_data)} --- ")
