#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import os


try:
    players = json.load(open("data.json", "r"))
except FileNotFoundError:
    players = {}

players = {k: v for k, v in sorted(players.items(), key=lambda d: d[1]["id"])}


edad = {
    "Hierro": 0,
    "AEM": 0,
    "PEM": 0,
    "BEM": 0,
    "Colonial": 0,
    "Industrial": 0,
    "Progreso": 0,
    "Moderna": 0,
    "Postmoderna": 0,
    "Contemporánea": 0,
    "Mañana": 0,
    "Futuro": 0,
    "Ártico": 0,
    "Oceánico": 0,
    "Virtual": 0,
    "Marte": 0,
    "Ceres": 0
    }


edades = ["Hierro", "AEM", "PEM", "BEM", "Colonial", "Industrial", "Progreso",
          "Moderna", "Postmoderna", "Contemporánea", "Mañana", "Futuro",
          "Ártico", "Oceánico", "Virtual", "Marte", "Ceres"]


# Orden de edades ya que desbloquear el 2 nivel cuesta bienes de la edad
# anterior
expeOrden = {
    "Hierro": "Hierro",
    "AEM": "Hierro",
    "PEM": "AEM",
    "BEM": "PEM",
    "Colonial": "BEM",
    "Industrial": "Colonial",
    "Progreso": "Industrial",
    "Moderna": "Progreso",
    "Postmoderna": "Moderna",
    "Contemporánea": "Postmoderna",
    "Mañana": "Contemporánea",
    "Futuro": "Mañana",
    "Ártico": "Futuro",
    "Oceánico": "Ártico",
    "Virtual": "Oceánico",
    "Marte": "Virtual",
    "Ceres": "Marte"}

expeCoste = {
    "Hierro": 0,
    "AEM": 0,
    "PEM": 0,
    "BEM": 0,
    "Colonial": 0,
    "Industrial": 0,
    "Progreso": 0,
    "Moderna": 0,
    "Postmoderna": 0,
    "Contemporánea": 0,
    "Mañana": 0,
    "Futuro": 0,
    "Ártico": 0,
    "Oceánico": 0,
    "Virtual": 0,
    "Marte": 0,
    "Ceres": 0}

expeLevel2 = {
    "Hierro": 2,
    "AEM": 2,
    "PEM": 3,
    "BEM": 4,
    "Colonial": 4,
    "Industrial": 5,
    "Progreso": 5,
    "Moderna": 5,
    "Postmoderna": 5,
    "Contemporánea": 5,
    "Mañana": 6,
    "Futuro": 6,
    "Ártico": 6,
    "Oceánico": 6,
    "Virtual": 7,
    "Marte": 14,
    "Ceres": 28}


def arca(level):
    """Bienes que entrega el arca en función del nivel"""
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


def observatorio(level):
    """Bienes que entrega el observatorio en función del nivel"""
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


def atomium(level):
    """Bienes que entrega el atomium en función del nivel"""
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


def bano(level):
    """Bienes que entrega el baño real del asentamiento egipcio en función del
    nivel, hay que tener en cuenta que la información sobre los bienes que
    devuelve a diferencia de para los GE es la suma de todos los bienes de la
    edad"""
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
    """Importe de ingresos por recogida por edad"""
    for player, dat in players.items():
        if "Arca" in dat:
            edad[dat["Edad"]] += arca(dat["Arca"])
        if "Observatorio" in dat:
            edad[dat["Edad"]] += observatorio(dat["Observatorio"])
        if "Atomium" in dat:
            edad[dat["Edad"]] += atomium(dat["Atomium"])

        # En el caso de los edificios gremiales los materiales que se indican
        # en la descripción son siempre la suma de los 5 bienes de la edad
        if "Dirigible" in dat:
            for ed in dat["Dirigible"]:
                edad[ed] += 4   # 20/5

        if "Estatua" in dat:
            for ed in dat["Estatua"]:
                edad[ed["Edad"]] += 2*ed["Nivel"]   # 10/5

        if "Baño" in dat:
            edad[dat["Baño"]["Edad"]] += bano(dat["Baño"]["Nivel"])

        # Calculo coste de expedición
        anterior = expeOrden[dat["Edad"]]
        expeCoste[anterior] += expeLevel2[dat["Edad"]]
        expeCoste[dat["Edad"]] += 2*expeLevel2[dat["Edad"]] + \
            4*expeLevel2[dat["Edad"]]

    txt = ""
    for ed in edades:
        txt += "%-25s\t%5i \t %4i" % (ed, edad[ed], -expeCoste[ed])
        txt += os.linesep
    return txt


def userReport():
    """Informe de edificios por jugador"""
    for player, dat in players.items():
        if "Arca" not in dat and "Observatorio" not in dat \
                and "Atomium" not in dat and "Dirigible" not in dat \
                and "Estatua" not in dat and "Baño" not in dat:
            continue

        print("-------------------------------------------------------------")
        print(player, " - ", dat["Edad"])
        if "Arca" in dat:
            print("    Arca %i" % dat["Arca"])
        if "Observatorio" in dat:
            print("    Observatorio %i" % dat["Observatorio"])
        if "Atomium" in dat:
            print("    Atomium %i" % dat["Atomium"])

        if "Estatua" in dat:
            for ed in dat["Estatua"]:
                print("    Estatua %i - %s" % (ed["Nivel"], ed["Edad"]))

        if "Dirigible" in dat:
            for ed in dat["Dirigible"]:
                print("    Dirigible 11 - %s" % ed)
        if "Baño" in dat:
            print("    Baño Real %i - %s" % (
                dat["Baño"]["Nivel"],  dat["Baño"]["Edad"]))

        print()

if __name__ == "__main__":
    print(report())
