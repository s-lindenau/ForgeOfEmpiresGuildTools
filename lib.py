#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import os
import logging
import sys

from model.foe_guild_tools_data import FoeGuildToolsData

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
        return level*2+2


def observatory_goods_for_level(level):
    """Goods delivered by the observatory based on the level"""
    if level == 0:
        return 0
    elif level == 1:
        return 3
    elif level == 2:
        return 4
    elif level == 3:
        return 4
    elif level == 4:
        return 5
    elif level == 5:
        return 6
    elif level == 6:
        return 6
    elif level == 7:
        return 7
    elif level == 8:
        return 7
    elif level == 9:
        return 8
    elif level == 10:
        return 8
    else:
        return level*2-12


def atomium_goods_for_level(level):
    """Goods that the atomium delivers depending on the level"""
    if level == 0:
        return 0
    elif level == 1:
        return 6
    elif level == 2:
        return 7
    elif level == 3:
        return 8
    elif level == 4:
        return 9
    elif level == 5:
        return 11
    elif level == 6:
        return 12
    elif level == 7:
        return 13
    elif level == 8:
        return 14
    elif level == 9:
        return 15
    else:
        return level*2-3


def report(players: dict):
    try:
        return do_report(players)
    except Exception as e:
        logging.error(f"Failed to generate report: {e}", exc_info=e)


def do_report(players: dict):
    """Collection income amount by age"""
    for player, player_data in players.items():
        if "Arc" in player_data:
            total_by_age[player_data["Age"]] += arc_goods_for_level(player_data["Arc"])
        if "Observatory" in player_data:
            total_by_age[player_data["Age"]] += observatory_goods_for_level(player_data["Observatory"])
        if "Atomium" in player_data:
            total_by_age[player_data["Age"]] += atomium_goods_for_level(player_data["Atomium"])

        # Calculate expedition costs
        anterior = expeditionOrder[player_data["Age"]]
        expeditionCost[anterior] += expeditionLevel2[player_data["Age"]]
        expeditionCost[player_data["Age"]] += 2 * expeditionLevel2[player_data["Age"]] + 4 * expeditionLevel2[player_data["Age"]]

    txt = "%-20s\t%6s \t %5s" % ("Age", "Total", "Cost") + os.linesep + "-----------------------------------------" + os.linesep
    for ed in ages:
        txt += "%-20s\t%6i \t %5i" % (ed, total_by_age[ed], -expeditionCost[ed])
        txt += os.linesep
    return txt


if __name__ == "__main__":
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=LOG_LEVEL,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
    foe_data = read_data_from_stored_json()
    print(report(foe_data.players.get_all_players()))
