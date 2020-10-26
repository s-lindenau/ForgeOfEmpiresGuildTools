#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from PyQt5 import QtWidgets, QtGui

from lib import players, edades, report


class Player(QtWidgets.QWidget):
    """Widget con los edificios gremiales del jugador"""

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        self.Estatuas = []
        self.Dirigibles = []

        lyt = QtWidgets.QGridLayout(self)

        lyt.addWidget(QtWidgets.QLabel("Edad"), 0, 1)
        self.edad = QtWidgets.QComboBox()
        for edad in edades:
            self.edad.addItem(edad)
        lyt.addWidget(self.edad, 0, 2)
        lyt.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 1, 3)
        lyt.addWidget(QtWidgets.QLabel("Arca"), 2, 1)
        self.arca = QtWidgets.QSpinBox()
        lyt.addWidget(self.arca, 2, 2)
        lyt.addWidget(QtWidgets.QLabel("Observatorio"), 3, 1)
        self.observatorio = QtWidgets.QSpinBox()
        lyt.addWidget(self.observatorio, 3, 2)
        lyt.addWidget(QtWidgets.QLabel("Atomium"), 4, 1)
        self.atomium = QtWidgets.QSpinBox()
        lyt.addWidget(self.atomium, 4, 2)

        lyt.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 5, 1)

        groupEstatua = QtWidgets.QGroupBox("Estatua de honor")
        lyt.addWidget(groupEstatua, 6, 1, 1, 3)
        self.lytEstatua = QtWidgets.QVBoxLayout(groupEstatua)
        lytButton = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QToolButton()
        addButton.setIcon(QtGui.QIcon("images/add.png"))
        lytButton.addWidget(addButton)
        deleteButton = QtWidgets.QToolButton()
        deleteButton.setIcon(QtGui.QIcon("images/remove.png"))
        lytButton.addWidget(deleteButton)
        lytButton.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        self.lytEstatua.addLayout(lytButton)
        addButton.clicked.connect(self.addEstatua)
        deleteButton.clicked.connect(self.deleteEstatua)

        lyt.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 7, 1)

        groupBano = QtWidgets.QGroupBox("Baño real")
        lyt.addWidget(groupBano, 8, 1, 1, 3)
        lytbano = QtWidgets.QGridLayout(groupBano)
        self.bano = QtWidgets.QCheckBox("Baño Real")
        lytbano.addWidget(self.bano, 0, 1, 1, 2)
        lytbano.addWidget(QtWidgets.QLabel("Edad"), 1, 1)
        self.edadBano = QtWidgets.QComboBox()
        lytbano.addWidget(self.edadBano, 1, 2)
        lytbano.addWidget(QtWidgets.QLabel("Nivel"), 2, 1)
        self.nivelBano = QtWidgets.QSpinBox()
        self.nivelBano.setRange(0, 6)
        lytbano.addWidget(self.nivelBano, 2, 2)
        self.bano.toggled.connect(self.edadBano.setEnabled)
        self.bano.toggled.connect(self.nivelBano.setEnabled)

        lyt.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 9, 1)

        groupDirigible = QtWidgets.QGroupBox("Dirigible nivel 11")
        lyt.addWidget(groupDirigible, 10, 1, 1, 3)
        self.lytDirigible = QtWidgets.QVBoxLayout(groupDirigible)
        lytButton = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QToolButton()
        addButton.setIcon(QtGui.QIcon("images/add.png"))
        lytButton.addWidget(addButton)
        deleteButton = QtWidgets.QToolButton()
        deleteButton.setIcon(QtGui.QIcon("images/remove.png"))
        lytButton.addWidget(deleteButton)
        lytButton.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        self.lytDirigible.addLayout(lytButton)
        addButton.clicked.connect(self.addDirigible)
        deleteButton.clicked.connect(self.deleteDirigible)

        lyt.addItem(QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding), 12, 1, 1, 3)

        for edad in edades:
            self.edadBano.addItem(edad)

    def update(self, item, lastitem):

        # Saved data of last item
        if lastitem:
            lastname = lastitem.text()
            dat = {}
            dat["Edad"] = self.edad.currentText()
            dat["id"] = self.parent().lst.row(lastitem)+1
            dat["Arca"] = self.arca.value()
            dat["Observatorio"] = self.observatorio.value()
            dat["Atomium"] = self.atomium.value()

            est = []
            for estatua in self.Estatuas:
                ed = {}
                ed["Edad"] = estatua.itemAt(1).widget().currentText()
                ed["Nivel"] = estatua.itemAt(3).widget().value()
                est.append(ed)
            dat["Estatua"] = est

            if self.bano.isChecked():
                bano = {}
                bano["Edad"] = self.edadBano.currentText()
                bano["Nivel"] = self.nivelBano.value()
                dat["Baño"] = bano

            dat["Dirigible"] = []
            for dirigible in self.Dirigibles:
                wdg = dirigible.itemAt(1).widget()
                dat["Dirigible"].append(wdg.currentText())

            players[lastname] = dat

        # Update properties with new player
        name = item.text()
        dat = players[name]

        self.edad.setCurrentText(dat["Edad"])
        if "Arca" in dat:
            self.arca.setValue(dat["Arca"])
        else:
            self.arca.setValue(0)

        if "Observatorio" in dat:
            self.observatorio.setValue(dat["Observatorio"])
        else:
            self.observatorio.setValue(0)

        if "Atomium" in dat:
            self.atomium.setValue(dat["Atomium"])
        else:
            self.atomium.setValue(0)

        self.edadBano.clear()
        currentEdadId = edades.index(dat["Edad"])
        for edad in edades[:currentEdadId+1]:
            self.edadBano.addItem(edad)

        if "Baño" in dat:
            self.bano.setChecked(True)
            self.edadBano.setCurrentText(dat["Baño"]["Edad"])
            self.nivelBano.setValue(dat["Baño"]["Nivel"])
        else:
            self.bano.setChecked(False)

        # Borra widgets de las estatuas del anterior jugador
        for lyt in self.Estatuas:
            while True:
                wdg = lyt.takeAt(0)
                if wdg is None:
                    break
                wdg.widget().deleteLater()
                self.lytEstatua.removeItem(wdg)

        self.Estatuas = []
        if "Estatua" in dat:
            for estatua in dat["Estatua"]:
                lyt = QtWidgets.QHBoxLayout()
                lyt.addWidget(QtWidgets.QLabel("Edad"))
                edad = QtWidgets.QComboBox()
                for ed in edades[:currentEdadId+1]:
                    edad.addItem(ed)
                edad.setCurrentText(estatua["Edad"])
                lyt.addWidget(edad)
                lyt.addWidget(QtWidgets.QLabel("Nivel"))
                nivel = QtWidgets.QSpinBox()
                nivel.setRange(0, 8)
                nivel.setValue(estatua["Nivel"])
                lyt.addWidget(nivel)
                self.lytEstatua.addLayout(lyt)
                self.Estatuas.append(lyt)

        # Borra widgets de los dirigibles del anterior jugador
        for lyt in self.Dirigibles:
            while True:
                wdg = lyt.takeAt(0)
                if wdg is None:
                    break
                wdg.widget().deleteLater()
                self.lytDirigible.removeItem(wdg)

        self.Dirigibles = []
        if "Dirigible" in dat:
            for dirigible in dat["Dirigible"]:
                lyt = QtWidgets.QHBoxLayout()
                lyt.addWidget(QtWidgets.QLabel("Edad"))
                edad = QtWidgets.QComboBox()
                for ed in edades[:currentEdadId+1]:
                    edad.addItem(ed)
                edad.setCurrentText(dirigible)
                lyt.addWidget(edad)
                self.lytDirigible.addLayout(lyt)
                self.Dirigibles.append(lyt)

    def addEstatua(self):
        lyt = QtWidgets.QHBoxLayout()
        lyt.addWidget(QtWidgets.QLabel("Edad"))
        edad = QtWidgets.QComboBox()
        for ed in edades[:self.edad.currentIndex()+1]:
            edad.addItem(ed)
        edad.setCurrentIndex(self.edad.currentIndex())
        lyt.addWidget(edad)
        lyt.addWidget(QtWidgets.QLabel("Nivel"))
        nivel = QtWidgets.QSpinBox()
        nivel.setRange(0, 8)
        nivel.setValue(1)
        lyt.addWidget(nivel)
        self.lytEstatua.addLayout(lyt)
        self.Estatuas.append(lyt)

    def deleteEstatua(self):
        if not self.Estatuas:
            return
        estatua = self.Estatuas.pop(-1)
        while True:
            wdg = estatua.takeAt(0)
            if wdg is None:
                break
            wdg.widget().deleteLater()
            self.lytEstatua.removeItem(wdg)

    def addDirigible(self):
        lyt = QtWidgets.QHBoxLayout()
        lyt.addWidget(QtWidgets.QLabel("Edad"))
        edad = QtWidgets.QComboBox()
        for ed in edades[:self.edad.currentIndex()+1]:
            edad.addItem(ed)
        edad.setCurrentIndex(self.edad.currentIndex())
        lyt.addWidget(edad)
        self.lytDirigible.addLayout(lyt)
        self.Dirigibles.append(lyt)

    def deleteDirigible(self):
        if not self.Dirigibles:
            return
        dirigible = self.Dirigibles.pop(-1)
        while True:
            wdg = dirigible.takeAt(0)
            if wdg is None:
                break
            wdg.widget().deleteLater()
            self.lytDirigible.removeItem(wdg)


class UI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(UI, self).__init__(parent)

        lyt = QtWidgets.QGridLayout(self)
        lytButton = QtWidgets.QHBoxLayout()
        addButton = QtWidgets.QToolButton()
        addButton.setIcon(QtGui.QIcon("images/add.png"))
        lytButton.addWidget(addButton)
        self.deleteButton = QtWidgets.QToolButton()
        self.deleteButton.setEnabled(False)
        self.deleteButton.setIcon(QtGui.QIcon("images/remove.png"))
        lytButton.addWidget(self.deleteButton)
        self.upButton = QtWidgets.QToolButton()
        self.upButton.setIcon(QtGui.QIcon("images/up.png"))
        lytButton.addWidget(self.upButton)
        self.downButton = QtWidgets.QToolButton()
        self.downButton.setIcon(QtGui.QIcon("images/down.png"))
        lytButton.addWidget(self.downButton)
        lytButton.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        reportButton = QtWidgets.QToolButton()
        reportButton.setIcon(QtGui.QIcon("images/report.png"))
        lytButton.addWidget(reportButton)
        lyt.addLayout(lytButton, 0, 1, 1, 3)
        addButton.clicked.connect(self.addPlayer)
        self.deleteButton.clicked.connect(self.deletePlayer)
        self.upButton.clicked.connect(self.up)
        self.downButton.clicked.connect(self.down)
        reportButton.clicked.connect(self.report)

        self.lst = QtWidgets.QListWidget()
        self.lst.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                               QtWidgets.QSizePolicy.Minimum)
        lyt.addWidget(self.lst, 1, 1, 1, 1)
        self.player = Player()
        lyt.addWidget(self.player, 1, 2, 1, 1)
        self.lst.currentItemChanged.connect(self.player.update)
        self.lst.currentRowChanged.connect(self.enableButton)

        for player in players:
            item = QtWidgets.QListWidgetItem(player)
            self.lst.addItem(item)
        self.lst.setCurrentRow(0)

    def enableButton(self, row):
        if row != -1:
            self.deleteButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)

        if row == 0:
            self.upButton.setEnabled(False)
        else:
            self.upButton.setEnabled(True)

        if row == self.lst.count()-1:
            self.downButton.setEnabled(False)
        else:
            self.downButton.setEnabled(True)

    def up(self):
        row = self.lst.currentRow()
        item = self.lst.takeItem(row)
        self.lst.insertItem(row-1, item)
        self.lst.setCurrentRow(row-1)

    def down(self):
        row = self.lst.currentRow()
        item = self.lst.takeItem(row)
        self.lst.insertItem(row+1, item)
        self.lst.setCurrentRow(row+1)

    def addPlayer(self):
        name, bool = QtWidgets.QInputDialog.getText(
            self, "Nombre", "Introduce nombre nuevo jugador", )
        if bool:
            players[name] = {"Edad": "Hierro", "id": self.lst.count()}
            self.lst.addItem(name)
            self.lst.setCurrentRow(self.lst.count()-1)

    def deletePlayer(self):
        player = self.lst.takeItem(self.lst.currentRow()).text()
        del players[player]

    def report(self):
        txt = report()
        dialog = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Information, "Informe de bienes", txt)
        dialog.exec_()

    def closeEvent(self, event=None):
        json.dump(players, open("data.json", "w"), indent=4)
        self.close()
