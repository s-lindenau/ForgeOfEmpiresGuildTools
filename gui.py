#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from PyQt5 import QtWidgets, QtGui
from pyperclip import copy as clipboard_copy
from lib import foe_data, players, ages, report
from foe_helper_file_reader import read_foe_data, format_profile_link_template


class Player(QtWidgets.QWidget):
    """Widget with the player's guild buildings"""

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

        self.Statues = []
        self.Airships = []

        layout = QtWidgets.QGridLayout(self)

        layout.addWidget(QtWidgets.QLabel("Age"), 0, 1)
        self.age = QtWidgets.QComboBox()
        for age in ages:
            self.age.addItem(age)
        layout.addWidget(self.age, 0, 2)
        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 1, 3)
        layout.addWidget(QtWidgets.QLabel("Arc"), 2, 1)
        self.arc = QtWidgets.QSpinBox()
        self.arc.setRange(0, 999)
        layout.addWidget(self.arc, 2, 2)
        layout.addWidget(QtWidgets.QLabel("Observatory"), 3, 1)
        self.observatory = QtWidgets.QSpinBox()
        self.observatory.setRange(0, 999)
        layout.addWidget(self.observatory, 3, 2)
        layout.addWidget(QtWidgets.QLabel("Atomium"), 4, 1)
        self.atomium = QtWidgets.QSpinBox()
        self.atomium.setRange(0, 999)
        layout.addWidget(self.atomium, 4, 2)

        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 5, 1)

        group_statues = QtWidgets.QGroupBox("Statue of Honor")
        layout.addWidget(group_statues, 6, 1, 1, 3)
        self.layoutStatues = QtWidgets.QVBoxLayout(group_statues)
        layout_button = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QToolButton()
        add_button.setIcon(QtGui.QIcon("images/add.png"))
        layout_button.addWidget(add_button)
        delete_button = QtWidgets.QToolButton()
        delete_button.setIcon(QtGui.QIcon("images/remove.png"))
        layout_button.addWidget(delete_button)
        layout_button.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        self.layoutStatues.addLayout(layout_button)
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(self.add_statue)
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.delete_statue)

        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 7, 1)

        group_profiles = QtWidgets.QGroupBox("Player Profile (copy to clipboard with button)")
        layout.addWidget(group_profiles, 8, 1, 1, 3)
        layout_profiles = QtWidgets.QGridLayout(group_profiles)
        self.profile_text_field = QtWidgets.QLineEdit()
        self.profile_text_field.setReadOnly(True)
        layout_profiles.addWidget(self.profile_text_field, 0, 1, 1, 1)
        copy_link_button = QtWidgets.QToolButton()
        copy_link_button.setIcon(QtGui.QIcon("images/right.png"))
        copy_link_button.clicked.connect(self.copy_profile_link_to_clipboard)
        layout_profiles.addWidget(copy_link_button, 0, 2, 1, 1)

        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), 9, 1)

        group_airship = QtWidgets.QGroupBox("Airship level 11")
        layout.addWidget(group_airship, 10, 1, 1, 3)
        self.layoutAirship = QtWidgets.QVBoxLayout(group_airship)
        layout_button = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QToolButton()
        add_button.setIcon(QtGui.QIcon("images/add.png"))
        layout_button.addWidget(add_button)
        delete_button = QtWidgets.QToolButton()
        delete_button.setIcon(QtGui.QIcon("images/remove.png"))
        layout_button.addWidget(delete_button)
        layout_button.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        self.layoutAirship.addLayout(layout_button)
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(self.add_airship)
        # noinspection PyUnresolvedReferences
        delete_button.clicked.connect(self.delete_airship)

        layout.addItem(QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding), 12, 1, 1, 3)


    # noinspection PyMethodOverriding
    def update(self, item, last_item):

        # Saved data of last item
        if last_item:
            lastname = last_item.text()
            player_data = {
                "Age": self.age.currentText(), 
                "id": self.parent().list.row(last_item) + 1,
                "Arc": self.arc.value(), 
                "Observatory": self.observatory.value(), 
                "Atomium": self.atomium.value()}

            est = []
            for statue in self.Statues:
                ed = {
                    "Age": statue.itemAt(1).widget().currentText(), 
                    "Level": statue.itemAt(3).widget().value()}
                est.append(ed)
            player_data["Statue"] = est

            player_data["Airship"] = []
            for airship in self.Airships:
                widget = airship.itemAt(1).widget()
                player_data["Airship"].append(widget.currentText())

            players[lastname] = player_data

        # Update properties with new player
        name = item.text()
        player_data = players[name]

        self.age.setCurrentText(player_data["Age"])
        if "Arc" in player_data:
            self.arc.setValue(player_data["Arc"])
        else:
            self.arc.setValue(0)

        if "Observatory" in player_data:
            self.observatory.setValue(player_data["Observatory"])
        else:
            self.observatory.setValue(0)

        if "Atomium" in player_data:
            self.atomium.setValue(player_data["Atomium"])
        else:
            self.atomium.setValue(0)

        profile_link = format_profile_link_template(foe_data, player_data)
        self.profile_text_field.setText(profile_link)
        self.profile_text_field.setCursorPosition(0)

        current_age_id = ages.index(player_data["Age"])

        # Deletes widgets from the previous player's statues
        for layout in self.Statues:
            while True:
                widget = layout.takeAt(0)
                if widget is None:
                    break
                widget.widget().deleteLater()
                self.layoutStatues.removeItem(widget)

        self.Statues = []
        if "Statue" in player_data:
            for statue in player_data["Statue"]:
                layout = QtWidgets.QHBoxLayout()
                layout.addWidget(QtWidgets.QLabel("Age"))
                age = QtWidgets.QComboBox()
                for ed in ages[:current_age_id + 1]:
                    age.addItem(ed)
                age.setCurrentText(statue["Age"])
                layout.addWidget(age)
                layout.addWidget(QtWidgets.QLabel("Level"))
                level = QtWidgets.QSpinBox()
                level.setRange(0, 99)
                level.setValue(statue["Level"])
                layout.addWidget(level)
                self.layoutStatues.addLayout(layout)
                self.Statues.append(layout)

        # Delete widgets from the previous player's Airships
        for layout in self.Airships:
            while True:
                widget = layout.takeAt(0)
                if widget is None:
                    break
                widget.widget().deleteLater()
                self.layoutAirship.removeItem(widget)

        self.Airships = []
        if "Airship" in player_data:
            for airship in player_data["Airship"]:
                layout = QtWidgets.QHBoxLayout()
                layout.addWidget(QtWidgets.QLabel("Age"))
                age = QtWidgets.QComboBox()
                for ed in ages[:current_age_id + 1]:
                    age.addItem(ed)
                age.setCurrentText(airship)
                layout.addWidget(age)
                self.layoutAirship.addLayout(layout)
                self.Airships.append(layout)

    def add_statue(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Age"))
        age = QtWidgets.QComboBox()
        for ed in ages[:self.age.currentIndex() + 1]:
            age.addItem(ed)
        age.setCurrentIndex(self.age.currentIndex())
        layout.addWidget(age)
        layout.addWidget(QtWidgets.QLabel("Level"))
        level = QtWidgets.QSpinBox()
        level.setRange(0, 99)
        level.setValue(1)
        layout.addWidget(level)
        self.layoutStatues.addLayout(layout)
        self.Statues.append(layout)

    def delete_statue(self):
        if not self.Statues:
            return
        statues = self.Statues.pop(-1)
        while True:
            widget = statues.takeAt(0)
            if widget is None:
                break
            widget.widget().deleteLater()
            self.layoutStatues.removeItem(widget)

    def add_airship(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Age"))
        age = QtWidgets.QComboBox()
        for ed in ages[:self.age.currentIndex() + 1]:
            age.addItem(ed)
        age.setCurrentIndex(self.age.currentIndex())
        layout.addWidget(age)
        self.layoutAirship.addLayout(layout)
        self.Airships.append(layout)

    def delete_airship(self):
        if not self.Airships:
            return
        airship = self.Airships.pop(-1)
        while True:
            widget = airship.takeAt(0)
            if widget is None:
                break
            widget.widget().deleteLater()
            self.layoutAirship.removeItem(widget)

    def copy_profile_link_to_clipboard(self):
        link_value = self.profile_text_field.text()
        clipboard_copy(link_value)


class UI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(UI, self).__init__(parent)

        layout = QtWidgets.QGridLayout(self)
        layout_button = QtWidgets.QHBoxLayout()
        add_button = QtWidgets.QToolButton()
        add_button.setIcon(QtGui.QIcon("images/add.png"))
        layout_button.addWidget(add_button)
        self.deleteButton = QtWidgets.QToolButton()
        self.deleteButton.setEnabled(False)
        self.deleteButton.setIcon(QtGui.QIcon("images/remove.png"))
        layout_button.addWidget(self.deleteButton)
        self.upButton = QtWidgets.QToolButton()
        self.upButton.setIcon(QtGui.QIcon("images/up.png"))
        layout_button.addWidget(self.upButton)
        self.downButton = QtWidgets.QToolButton()
        self.downButton.setIcon(QtGui.QIcon("images/down.png"))
        layout_button.addWidget(self.downButton)
        layout_button.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))
        report_button = QtWidgets.QToolButton()
        report_button.setIcon(QtGui.QIcon("images/report.png"))
        layout_button.addWidget(report_button)
        layout.addLayout(layout_button, 0, 1, 1, 3)
        # noinspection PyUnresolvedReferences
        add_button.clicked.connect(self.add_player)
        # noinspection PyUnresolvedReferences
        self.deleteButton.clicked.connect(self.delete_player)
        # noinspection PyUnresolvedReferences
        self.upButton.clicked.connect(self.up)
        # noinspection PyUnresolvedReferences
        self.downButton.clicked.connect(self.down)
        # noinspection PyUnresolvedReferences
        report_button.clicked.connect(self.report)

        self.load_zip_button = QtWidgets.QPushButton("Load from ZIP")
        self.load_zip_button.clicked.connect(self.load_zip_file)
        layout_button.addWidget(self.load_zip_button)

        self.list = QtWidgets.QListWidget()
        self.list.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(self.list, 1, 1, 1, 1)
        self.player = Player()
        layout.addWidget(self.player, 1, 2, 1, 1)
        # noinspection PyUnresolvedReferences
        self.list.currentItemChanged.connect(self.player.update)
        # noinspection PyUnresolvedReferences
        self.list.currentRowChanged.connect(self.enable_button)

        for player in players:
            item = QtWidgets.QListWidgetItem(player)
            self.list.addItem(item)
        self.list.setCurrentRow(0)

    def enable_button(self, row):
        if row != -1:
            self.deleteButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)

        if row == 0:
            self.upButton.setEnabled(False)
        else:
            self.upButton.setEnabled(True)

        if row == self.list.count()-1:
            self.downButton.setEnabled(False)
        else:
            self.downButton.setEnabled(True)

    def up(self):
        row = self.list.currentRow()
        item = self.list.takeItem(row)
        self.list.insertItem(row - 1, item)
        self.list.setCurrentRow(row - 1)

    def down(self):
        row = self.list.currentRow()
        item = self.list.takeItem(row)
        self.list.insertItem(row + 1, item)
        self.list.setCurrentRow(row + 1)

    def add_player(self):
        name, input_completed = QtWidgets.QInputDialog.getText(
            self, "Name", "Enter new player name", )
        if input_completed and len(name) > 0:
            players[name] = {"Age": "IronAge", "id": self.list.count()}
            self.list.addItem(name)
            self.list.setCurrentRow(self.list.count() - 1)

    def delete_player(self):
        player = self.list.takeItem(self.list.currentRow()).text()
        del players[player]

    @staticmethod
    def report():
        txt = report()
        dialog = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Information, "Asset Report", txt)
        dialog.exec_()

    def closeEvent(self, event=None):
        # TODO: rewrite GUI data loading/saving
        #json.dump(players, open("data.json", "w"), indent=4)
        self.close()

    def load_zip_file(self):
        selected_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', "Zip Files (*.zip)")
        filename = selected_file[0]
        if filename.__len__() <= 0:
            # no file selected / dialog cancelled
            return

        foe_data = read_foe_data(filename)
        players_from_file = foe_data.get("players", {})
        if players_from_file.__len__() == 0:
            self.show_alert("Data not loaded", "Data could not be loaded from the selected file", QtWidgets.QMessageBox.Warning, QtWidgets.QMessageBox.Ok)
            return

        json.dump(foe_data, open("data.json", "w"), indent=4)
        # for now user needs to restart GUI to load changes
        self.show_alert("Data loaded", "Data loaded, please restart GUI to apply changes", QtWidgets.QMessageBox.Information, QtWidgets.QMessageBox.Ok)
        self.close()

    @staticmethod
    def show_alert(title, message, icon, buttons):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(buttons)
        msg_box.exec_()