#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import os


try:
    foe_data = json.load(open("data.json", "r"))
    players = foe_data.get("players", {})
except FileNotFoundError:
    foe_data = {}
    players = {}

players = {k: v for k, v in sorted(players.items(), key=lambda d: d[1]["id"])}


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
    "SpaceAgeAsteroid": 0,
    "SpaceAgeVenus": 0,
    "SpaceAgeJupiter": 0,
    "SpaceAgeTitan": 0,
    "SpaceAgeHub": 0,
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
     "SpaceAgeAsteroid",
     "SpaceAgeVenus",
     "SpaceAgeJupiter",
     "SpaceAgeTitan",
     "SpaceAgeHub",
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
    "SpaceAgeAsteroid": "SpaceAgeMars",
    "SpaceAgeVenus": "SpaceAgeAsteroid",
    "SpaceAgeJupiter": "SpaceAgeVenus",
    "SpaceAgeTitan": "SpaceAgeJupiter",
    "SpaceAgeHub": "SpaceAgeTitan",
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
    "SpaceAgeAsteroid": 0,
    "SpaceAgeVenus": 0,
    "SpaceAgeJupiter": 0,
    "SpaceAgeTitan": 0,
    "SpaceAgeHub": 0,
}

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
    "SpaceAgeMars": 14,
    "SpaceAgeAsteroid": 28,
    "SpaceAgeVenus": 56,        # todo: guess, find actual value
    "SpaceAgeJupiter": 112,     # todo: guess, find actual value
    "SpaceAgeTitan": 224,       # todo: guess, find actual value
    "SpaceAgeHub": 448,         # todo: guess, find actual value
}


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


def egyptian_settlement_goods_for_level(level):
    """Goods delivered by the royal bath of the Egyptian settlement based on the
    level. It should be noted that the information on the goods it returns, unlike for the GE, is the sum of all goods of the
    age."""
    if level <= 1:
        return 0
    elif level == 2:
        return 1
    elif level == 3:
        return 2
    elif level == 4:
        return 3
    elif level == 5:
        return 4
    elif level == 6:
        return 6


def report():
    """Collection income amount by age"""
    for player, player_data in players.items():
        if "Arc" in player_data:
            total_by_age[player_data["Age"]] += arc_goods_for_level(player_data["Arc"])
        if "Observatory" in player_data:
            total_by_age[player_data["Age"]] += observatory_goods_for_level(player_data["Observatory"])
        if "Atomium" in player_data:
            total_by_age[player_data["Age"]] += atomium_goods_for_level(player_data["Atomium"])

        # In the case of guild buildings, the materials indicated
        # in the description are always the sum of the 5 assets of the age
        if "Airship" in player_data:
            for ed in player_data["Airship"]:
                total_by_age[ed] += 4   # 20/5

        if "Statue" in player_data:
            for ed in player_data["Statue"]:
                total_by_age[ed["Age"]] += 2 * ed["Level"]   # 10/5

        if "Egyptian Royal Bath" in player_data:
            total_by_age[player_data["Egyptian Royal Bath"]["Age"]] += egyptian_settlement_goods_for_level(player_data["Egyptian Royal Bath"]["Level"])

        # Calculate expedition costs
        anterior = expeditionOrder[player_data["Age"]]
        expeditionCost[anterior] += expeditionLevel2[player_data["Age"]]
        expeditionCost[player_data["Age"]] += 2 * expeditionLevel2[player_data["Age"]] + 4 * expeditionLevel2[player_data["Age"]]

    txt = "%-25s\t%5s \t %4s" % ("Age", "Total", "Cost") + os.linesep + "-----------------------------------------" + os.linesep
    for ed in ages:
        txt += "%-25s\t%5i \t %4i" % (ed, total_by_age[ed], -expeditionCost[ed])
        txt += os.linesep
    return txt


def user_report():
    """Building Report by Player"""
    for player, dat in players.items():
        if "Arc" not in dat and "Observatory" not in dat \
                and "Atomium" not in dat and "Airship" not in dat \
                and "Statue" not in dat and "Egyptian Royal Bath" not in dat:
            continue

        print("-----------------------------------------")
        print(player, " - ", dat["Age"])
        if "Arc" in dat:
            print("    Arc %i" % dat["Arc"])
        if "Observatory" in dat:
            print("    Observatory %i" % dat["Observatory"])
        if "Atomium" in dat:
            print("    Atomium %i" % dat["Atomium"])

        if "Statue" in dat:
            for ed in dat["Statue"]:
                print("    Statue %i - %s" % (ed["Level"], ed["Age"]))

        if "Airship" in dat:
            for ed in dat["Airship"]:
                print("    Airship 11 - %s" % ed)
        if "Egyptian Royal Bath" in dat:
            print("    Egyptian Royal Bath Real %i - %s" % (
                dat["Egyptian Royal Bath"]["Level"],  dat["Egyptian Royal Bath"]["Age"]))

        print()


if __name__ == "__main__":
    print(report())
