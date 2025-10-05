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

CROSS = "❌"
CHECK = "✅"

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
    ge_contribution_count = get_contribution_count(players, "ExpeditionStats", "Rank")
    qi_contribution_count = get_contribution_count(players, "QuantumIncursionStats", "Rank")
    gbg_contribution_count = get_contribution_count(players, "BattleGroundsStats", "Rank")

    members_goods_data = get_members_goods_data(players)
    goods_contribution_count = len(members_goods_data)

    members = Players()
    for player in players.get_all_players():
        player_data = players.get_player_by_name(player)
        player_id = player_data.get("player_id")
        player_rank_in_guild = player_data.get("id")
        age = player_data.get("Age")

        ge_data = player_data.get("ExpeditionStats", {})
        qi_data = player_data.get("QuantumIncursionStats", {})
        gbg_data = player_data.get("BattleGroundsStats", {})
        goods_data = members_goods_data.get(player, {})

        member_data = {
            "player_id": player_id,
            "player_name": player,
            "rank": player_rank_in_guild,
            "age": age,
            "overall_participation": 0,
            "ge_contribution_count": ge_contribution_count,
            "qi_contribution_count": qi_contribution_count,
            "gbg_contribution_count": gbg_contribution_count,
            "goods_contribution_count": goods_contribution_count,
            "ge_data": ge_data,
            "qi_data": qi_data,
            "gbg_data": gbg_data,
            "goods_data": goods_data,
        }
        process_participation_data(member_data)
        members.add_player(player_id, player, member_data)
    return members


def get_members_goods_data(players) -> dict:
    members_goods = Players()
    for player in players.get_all_players():
        player_data = players.get_player_by_name(player)
        player_total_goods = get_total_goods(player_data)
        player_id = player_data.get("player_id")
        member_goods_data = {
            "total_goods": player_total_goods,
        }
        members_goods.add_player(player_id, player, member_goods_data)
    # add the rank by sorting high->low
    members_goods_ranks = members_goods.get_sorted_by_key("total_goods", sort_direction=SortDirection.DESCENDING)
    rank = 1
    for member_goods in members_goods_ranks:
        members_goods_ranks.get(member_goods)["rank"] = rank
        rank += 1
    return members_goods_ranks


def get_total_goods(player_data):
    total_goods = 0
    guild_buildings = player_data.get("GuildBuildings", {}).values()
    for guild_building in guild_buildings:
        total_goods += guild_building.get("TotalGoods", 0)
    return total_goods


def get_contribution_count(players: Players, contribution_category_key, position_key) -> int:
    contribution_count = 0
    for player in players.get_all_players():
        player_data = players.get_player_by_name(player)
        contribution_category = player_data.get(contribution_category_key, {})
        position = contribution_category.get(position_key, -1)
        if position > contribution_count:
            contribution_count = position
    return contribution_count


def process_participation_data(member_data: dict):
    """Calculate and store the participation data for a member based on their ranks in different guild activities."""

    # Current activities included are:
    #  - Guild Expedition (GE)
    #  - Quantum Incursion (QI)
    #  - Guild BattleGrounds (GbG)
    #
    # Assume a guild size of for example 80 members participating in each activity
    # - ranked 1 in the event gives 79 points
    # - ranked 2 in the event gives 78 points
    # - ranked n in the event gives (event participation count - n) points
    # - not ranked (<1) or last gives 0 points
    # - breaching guild rules gives negative(participation count) points (TODO)
    #
    # Guild Treasury (T) goods buildings (totals) are also counted, but currently not included in the activity score

    participation_summary = ""
    total_participation_points = 0
    total_goods_contribution = member_data.get("goods_data", {}).get("total_goods", 0)
    ge_contribution_count = member_data.get("ge_contribution_count", -1)
    qi_contribution_count = member_data.get("qi_contribution_count", -1)
    gbg_contribution_count = member_data.get("gbg_contribution_count", -1)

    ge_data = member_data.get("ge_data", {})
    qi_data = member_data.get("qi_data", {})
    gbg_data = member_data.get("gbg_data", {})

    ge_rank = ge_data.get("Rank", -1)
    ge_contribution = ge_data.get("SolvedEncounters", 0)  # GE: Number of solved encounters completed determines contribution
    qi_rank = qi_data.get("Rank", -1)
    qi_contribution = qi_data.get("Progress", 0)  # Qi: Progress points on completed encounters determines contribution
    gbg_rank = gbg_data.get("Rank", -1)
    gbg_contribution = gbg_data.get("BattlesWon", 0) + gbg_data.get("NegotiationsWon", 0)  # GbG: Battles + Negotiations determines contribution

    if ge_contribution > 0 and ge_rank > 0:
        total_participation_points += ge_contribution_count - ge_rank
        participation_summary += "Ge: " + CHECK
    else:
        participation_summary += "Ge: " + CROSS

    if qi_contribution > 0 and qi_rank > 0:
        total_participation_points += qi_contribution_count - qi_rank
        participation_summary += " Qi: " + CHECK
    else:
        participation_summary += " Qi: " + CROSS

    if gbg_contribution > 0 and gbg_rank > 0:
        total_participation_points += gbg_contribution_count - gbg_rank
        participation_summary += " GbG: " + CHECK
    else:
        participation_summary += " GbG: " + CROSS

    if total_goods_contribution > 0:
        participation_summary += " T: " + CHECK
    else:
        participation_summary += " T: " + CROSS

    member_data["overall_participation"] = total_participation_points
    member_data["participation_summary"] = participation_summary


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
