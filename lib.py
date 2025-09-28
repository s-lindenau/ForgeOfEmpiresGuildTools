#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import os
import logging
import sys

from model.players import Players
from model.foe_guild_tools_data import FoeGuildToolsData
from util.sort_direction import SortDirection

# Change to DEBUG for more verbose output
LOG_LEVEL = logging.WARNING

total_by_age = {
    "BronzeAge": 0,
    "IronAge": 0,
    "EarlyMiddleAge": 0,
    "HighMiddleAge": 0,
    "LateMiddleAge": 0,
    "ColonialAge": 0,
    "IndustrialAge": 0,
    "ProgressiveEra": 0,
    "ModernEra": 0,
    "PostModernEra": 0,
    "ContemporaryEra": 0,
    "TomorrowEra": 0,
    "FutureEra": 0,
    "ArcticFuture": 0,
    "OceanicFuture": 0,
    "VirtualFuture": 0,
    "SpaceAgeMars": 0,
    "SpaceAgeAsteroidBelt": 0,
    "SpaceAgeVenus": 0,
    "SpaceAgeJupiterMoon": 0,
    "SpaceAgeTitan": 0,
    "SpaceAgeSpaceHub": 0,
}

ages = [
    "BronzeAge",
    "IronAge",
    "EarlyMiddleAge",
    "HighMiddleAge",
    "LateMiddleAge",
    "ColonialAge",
    "IndustrialAge",
    "ProgressiveEra",
    "ModernEra",
    "PostModernEra",
    "ContemporaryEra",
    "TomorrowEra",
    "FutureEra",
    "ArcticFuture",
    "OceanicFuture",
    "VirtualFuture",
    "SpaceAgeMars",
    "SpaceAgeAsteroidBelt",
    "SpaceAgeVenus",
    "SpaceAgeJupiterMoon",
    "SpaceAgeTitan",
    "SpaceAgeSpaceHub",
]

# Age order since unlocking the 2nd level costs age goods
# previous
expeditionOrder = {
    "BronzeAge": "BronzeAge",
    "IronAge": "IronAge",
    "EarlyMiddleAge": "IronAge",
    "HighMiddleAge": "EarlyMiddleAge",
    "LateMiddleAge": "HighMiddleAge",
    "ColonialAge": "LateMiddleAge",
    "IndustrialAge": "ColonialAge",
    "ProgressiveEra": "IndustrialAge",
    "ModernEra": "ProgressiveEra",
    "PostModernEra": "ModernEra",
    "ContemporaryEra": "PostModernEra",
    "TomorrowEra": "ContemporaryEra",
    "FutureEra": "TomorrowEra",
    "ArcticFuture": "FutureEra",
    "OceanicFuture": "ArcticFuture",
    "VirtualFuture": "OceanicFuture",
    "SpaceAgeMars": "VirtualFuture",
    "SpaceAgeAsteroidBelt": "SpaceAgeMars",
    "SpaceAgeVenus": "SpaceAgeAsteroidBelt",
    "SpaceAgeJupiterMoon": "SpaceAgeVenus",
    "SpaceAgeTitan": "SpaceAgeJupiterMoon",
    "SpaceAgeSpaceHub": "SpaceAgeTitan",
}

expeditionCost = {
    "BronzeAge": 0,
    "IronAge": 0,
    "EarlyMiddleAge": 0,
    "HighMiddleAge": 0,
    "LateMiddleAge": 0,
    "ColonialAge": 0,
    "IndustrialAge": 0,
    "ProgressiveEra": 0,
    "ModernEra": 0,
    "PostModernEra": 0,
    "ContemporaryEra": 0,
    "TomorrowEra": 0,
    "FutureEra": 0,
    "ArcticFuture": 0,
    "OceanicFuture": 0,
    "VirtualFuture": 0,
    "SpaceAgeMars": 0,
    "SpaceAgeAsteroidBelt": 0,
    "SpaceAgeVenus": 0,
    "SpaceAgeJupiterMoon": 0,
    "SpaceAgeTitan": 0,
    "SpaceAgeSpaceHub": 0,
}

# https://en.wiki.forgeofempires.com/index.php?title=Costs_of_Unlocking_Difficulties
expeditionLevel2 = {
    "BronzeAge": 0,
    "IronAge": 2,
    "EarlyMiddleAge": 2,
    "HighMiddleAge": 3,
    "LateMiddleAge": 4,
    "ColonialAge": 4,
    "IndustrialAge": 5,
    "ProgressiveEra": 5,
    "ModernEra": 5,
    "PostModernEra": 5,
    "ContemporaryEra": 5,
    "TomorrowEra": 6,
    "FutureEra": 6,
    "ArcticFuture": 6,
    "OceanicFuture": 6,
    "VirtualFuture": 7,
    "SpaceAgeMars": 9,
    "SpaceAgeAsteroidBelt": 10,
    "SpaceAgeVenus": 11,
    "SpaceAgeJupiterMoon": 12,
    "SpaceAgeTitan": 13,
    "SpaceAgeSpaceHub": 14,
}


def read_data_from_stored_json() -> FoeGuildToolsData:
    try:
        foe_data_from_file = FoeGuildToolsData.from_dict(json.load(open("data.json", "r")))
    except FileNotFoundError:
        logging.debug("data.json file not found, starting with empty data.")
        foe_data_from_file = FoeGuildToolsData.empty()
    except json.JSONDecodeError as e:
        logging.error("data.json file is corrupt, please delete and try again!", exc_info=e)
        sys.exit(-1)
    except Exception as e:
        logging.error(f"Error loading data.json; {e}", exc_info=e)
        sys.exit(-100)

    return foe_data_from_file


def arc_goods_for_level(level):
    """Goods delivered by the ark based on the level"""
    if level == 0:
        return 0
    elif level == 1:
        return 9
    elif level == 2:
        return 10
    elif level == 3:
        return 12
    elif level == 4:
        return 13
    elif level == 5:
        return 15
    elif level == 6:
        return 16
    elif level == 7:
        return 18
    elif level == 8:
        return 19
    elif level == 9:
        return 21
    else:
        return level * 2 + 2


def report(players: Players):
    try:
        return do_report(players)
    except Exception as e:
        logging.error(f"Failed to generate expedition report: {e}", exc_info=e)


def do_report(players: Players):
    expedition_report_data = get_expedition_report_data(players)
    txt = "%-20s\t%6s \t %5s" % ("Age", "Income", "Cost") + os.linesep + "-----------------------------------------" + os.linesep

    for age in expedition_report_data:
        expedition_data = expedition_report_data.get(age)
        txt += "%-20s\t%6i \t %5i" % (expedition_data.get("age"), expedition_data.get("income"), expedition_data.get("cost"))
        txt += os.linesep
    return txt


def get_expedition_report_data(players: Players) -> dict:
    """Collection income amount by age"""
    for player, player_data in players.get_all_players().items():
        if "Arc" in player_data:
            total_by_age[player_data["Age"]] += arc_goods_for_level(player_data["Arc"])

        # Calculate expedition costs
        previous_age = expeditionOrder[player_data["Age"]]
        expeditionCost[previous_age] += expeditionLevel2[player_data["Age"]]
        expeditionCost[player_data["Age"]] += 2 * expeditionLevel2[player_data["Age"]] + 4 * expeditionLevel2[player_data["Age"]]

    expedition_report_data = {}
    for ed in ages:
        expedition_report_data[ed] = {
            "age": ed,
            "income": total_by_age[ed],
            "cost": -expeditionCost[ed]
        }
    return expedition_report_data


def members_report(players: Players):
    try:
        return do_members_report(players)
    except Exception as e:
        logging.error(f"Failed to generate members report: {e}", exc_info=e)


def do_members_report(players: Players) -> str:
    members = get_members_report_data(players)

    members_sorted = members.get_sorted_by_key("overall_participation", SortDirection.DESCENDING)
    txt = "%-3s\t%12s \t %30s" % ("#", "Contribution", "Player") + os.linesep + "----------------------------------------------------" + os.linesep
    for member, member_data in members_sorted.items():
        txt += "#%-3s\t%12s \t %30s" % (member_data.get("rank"), member_data.get("overall_participation"), member_data.get("player_name"))
        txt += os.linesep
    return txt


def get_members_report_data(players: Players) -> Players:
    guild_members_size = len(players.get_all_players())
    members = Players()
    for player in players.get_all_players():
        player_data = players.get_player_by_name(player)
        player_id = player_data.get("player_id")
        player_rank_in_guild = player_data.get("id")
        age = player_data.get("Age")

        ge_data = player_data.get("ExpeditionStats", {})
        gbg_data = player_data.get("BattleGroundsStats", {})
        qi_data = player_data.get("QuantumIncursionStats", {})

        member_data = {
            "player_id": player_id,
            "player_name": player,
            "rank": player_rank_in_guild,
            "age": age,
            "ge_data": ge_data,
            "qi_data": qi_data,
            "gbg_data": gbg_data,
            "overall_participation": 0,
        }
        member_data["overall_participation"] = calculate_participation_points(member_data, guild_members_size)
        members.add_player(player_id, player, member_data)
    return members


def calculate_participation_points(member_data: dict, guild_size: int) -> int:
    """Calculate the participation points for a member based on their ranks in different guild activities."""

    # Current activities included are:
    #  - Guild Expedition (GE)
    #  - Quantum Incursion (QI)
    #  - Guild BattleGrounds (GbG)
    #
    # Assume a guild size of for example 80 members
    # - ranked 1 in the event gives 80 points
    # - ranked 2 in the event gives 79 points
    # - ranked n in the event gives (guild size - n + 1) points
    # - not ranked (<1) gives 0 points
    # - breaching guild rules gives negative(guild size) points (TODO)

    total_participation_points = 0
    guild_size_adjusted = guild_size + 1

    ge_data = member_data.get("ge_data", {})
    qi_data = member_data.get("qi_data", {})
    gbg_data = member_data.get("gbg_data", {})

    ge_rank = ge_data.get("Rank", -1)
    ge_contribution = ge_data.get("Trial", 0)  # GE: Number of trials completed determines contribution
    qi_rank = qi_data.get("Rank", -1)
    qi_contribution = qi_data.get("Progress", 0)  # Qi: Progress points on completed encounters determines contribution
    gbg_rank = gbg_data.get("Rank", -1)
    gbg_contribution = gbg_data.get("BattlesWon", 0) + gbg_data.get("NegotiationsWon", 0)  # GbG: Battles + Negotiations determines contribution

    if ge_contribution > 0 and ge_rank > 0:
        total_participation_points += guild_size_adjusted - ge_rank
    if qi_contribution > 0 and qi_rank > 0:
        total_participation_points += guild_size_adjusted - qi_rank
    if gbg_contribution > 0 and gbg_rank > 0:
        total_participation_points += guild_size_adjusted - gbg_rank

    return total_participation_points


if __name__ == "__main__":
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=LOG_LEVEL,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
    foe_data = read_data_from_stored_json()
    print("++ Expedition Level 2 Unlock Costs ++ ")
    print("")
    print(report(foe_data.players))
    print("++ Overall member participation ++")
    print("")
    print(members_report(foe_data.players))
