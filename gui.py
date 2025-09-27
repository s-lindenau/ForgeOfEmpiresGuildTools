#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import json
import logging

from PyQt5 import QtWidgets, QtGui
from pyperclip import copy as clipboard_copy
from lib import ages, get_expedition_report_data, get_members_report_data
from foe_helper_file_reader import read_foe_data_from_zip, format_profile_link_template
from model.foe_guild_tools_data import FoeGuildToolsData
from util.sort_direction import SortDirection


class PlayerGui(QtWidgets.QWidget):
    """Widget with the player's guild buildings"""

    def __init__(self, foe_data: FoeGuildToolsData, parent=None):
        super(PlayerGui, self).__init__(parent)
        self.foe_data = foe_data
        self.players = foe_data.players

        layout = QtWidgets.QGridLayout(self)
        current_row = 0
        layout.addWidget(QtWidgets.QLabel("Selected player:"), current_row, 1)
        self.selected_player = QtWidgets.QLabel("")
        layout.addWidget(self.selected_player, current_row, 2)

        current_row += 1
        layout.addWidget(QtWidgets.QLabel("Age"), current_row, 1)
        self.age = QtWidgets.QComboBox()
        self.age.addItem("")
        for age in ages:
            self.age.addItem(age)
        self.age.setDisabled(True)
        layout.addWidget(self.age, current_row, 2)
        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), current_row, 3)

        current_row += 1
        layout.addWidget(QtWidgets.QLabel("Arc"), current_row, 1)
        self.arc = QtWidgets.QSpinBox()
        self.arc.setRange(0, 999)
        self.arc.setDisabled(True)
        layout.addWidget(self.arc, current_row, 2)

        current_row += 1
        layout.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed), current_row, 1)

        current_row += 1
        group_profiles = QtWidgets.QGroupBox("Player Profile (copy to clipboard with button)")
        layout.addWidget(group_profiles, current_row, 1, 1, 3)
        layout_profiles = QtWidgets.QGridLayout(group_profiles)
        self.profile_text_field = QtWidgets.QLineEdit()
        self.profile_text_field.setReadOnly(True)
        layout_profiles.addWidget(self.profile_text_field, 0, 1, 1, 1)
        copy_link_button = QtWidgets.QToolButton()
        copy_link_button.setIcon(QtGui.QIcon("images/gui/right.png"))
        # noinspection PyUnresolvedReferences
        copy_link_button.clicked.connect(self.copy_profile_link_to_clipboard)
        layout_profiles.addWidget(copy_link_button, 0, 2, 1, 1)

        current_row += 1
        layout.addItem(QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding), current_row, 1, 1, 3)

    # noinspection PyMethodOverriding
    def update(self, current_item, previous_item):
        try:
            self.do_update(current_item)
        except Exception as e:
            logging.error(f"Failed to update GUI: {e}", exc_info=e)
            self.clear_player_selection_on_error()

    def do_update(self, item):
        # Update properties with new player
        name = item.text()
        player_data = self.players.get_player_by_name(name)
        logging.debug(f"Selected player {name}: {player_data}")

        self.selected_player.setText(name)
        self.age.setCurrentText(player_data["Age"])
        if "Arc" in player_data:
            self.arc.setValue(player_data["Arc"])
        else:
            self.arc.setValue(0)

        profile_link = format_profile_link_template(self.foe_data, player_data)
        self.profile_text_field.setText(profile_link)
        self.profile_text_field.setCursorPosition(0)

    def copy_profile_link_to_clipboard(self):
        link_value = self.profile_text_field.text()
        clipboard_copy(link_value)

    def clear_player_selection_on_error(self):
        self.selected_player.setText("<Error, check logging>")
        self.age.setCurrentText("")
        self.arc.setValue(-1)


class DataTableDialog(QtWidgets.QDialog):
    """Dialog with a QTableWidget populated with data"""

    def __init__(self, window_title: str, data: dict, column_names: list, column_functions: list, parent=None):
        super(DataTableDialog, self).__init__(parent)
        column_count = len(column_names)
        self.setWindowTitle(window_title)
        self.setMinimumSize(150 + (100 * column_count), 800)
        self.data = data
        self.column_count = column_count
        self.column_names = column_names

        assert column_count == len(column_names)
        assert column_count == len(column_functions)

        layout = QtWidgets.QVBoxLayout(self)

        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setColumnCount(column_count)
        self.table_widget.setHorizontalHeaderLabels(column_names)
        self.table_widget.setRowCount(len(self.data))
        layout.addWidget(self.table_widget)

        for row, data_member in enumerate(self.data.values()):
            for column_index, column_function in enumerate(column_functions):
                column_value = column_function(data_member)
                self.table_widget.setItem(row, column_index, column_value)

        self.table_widget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table_widget.resizeColumnsToContents()

        copy_button = QtWidgets.QPushButton("Copy bottom 10 to clipboard", self)
        # noinspection PyUnresolvedReferences
        copy_button.clicked.connect(self.copy_bottom_to_clipboard)
        layout.addWidget(copy_button)
        close_button = QtWidgets.QPushButton("Copy selection to clipboard", self)
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.copy_selection_to_clipboard)
        layout.addWidget(close_button)

    def copy_bottom_to_clipboard(self):
        rows = set()
        row_count = self.table_widget.rowCount()
        # collect the last 10 rows (or fewer if less than 10 rows total)
        for row in range(max(0, row_count - 10), row_count):
            rows.add(row)

        txt = DataTableDialog.rows_to_clipboard_text(rows, self.column_count, self.column_names, self.table_widget)
        clipboard_copy(txt)

    def copy_selection_to_clipboard(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
        rows = set()
        for item in selected_items:
            rows.add(item.row())

        txt = DataTableDialog.rows_to_clipboard_text(rows, self.column_count, self.column_names, self.table_widget)
        clipboard_copy(txt)

    @staticmethod
    def rows_to_clipboard_text(rows: set, column_count: int, column_names: list, table_widget: QtWidgets.QTableWidget) -> str:
        txt = ""
        # Add column headers
        for column_name in column_names:
            txt += column_name + "\t"

        # Add separator line
        txt += os.linesep
        txt += "-" * (column_count * 10)
        txt += os.linesep

        # For each requested row
        for row in rows:
            row_data = []
            # For each column in that row
            for column in range(column_count):
                cell_item = table_widget.item(row, column)
                if cell_item is not None:
                    row_data.append(cell_item.text())
                else:
                    row_data.append("")
            txt += "\t".join(row_data) + "\n"
        return txt


class UI(QtWidgets.QWidget):

    def __init__(self, foe_data: FoeGuildToolsData, parent=None):
        super(UI, self).__init__(parent)
        self.foe_data = foe_data
        self.players = foe_data.players.get_sorted_by_key("id")

        layout = QtWidgets.QGridLayout(self)
        layout_header = QtWidgets.QHBoxLayout()

        guild_name = self.foe_data.guild_info.get_guild_name()
        self.guild_name_label = QtWidgets.QLabel(f"Guild: {guild_name}")
        layout_header.addWidget(self.guild_name_label)

        layout_header.addItem(QtWidgets.QSpacerItem(
            30, 30, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed))

        report_button = QtWidgets.QToolButton()
        report_button.setIcon(QtGui.QIcon("images/gui/report.png"))
        report_button.setToolTip("Show Guild Expedition Report")
        layout_header.addWidget(report_button)
        layout.addLayout(layout_header, 0, 1, 1, 3)
        # noinspection PyUnresolvedReferences
        report_button.clicked.connect(self.report)

        members_button = QtWidgets.QToolButton()
        members_button.setIcon(QtGui.QIcon("images/gui/report.png"))
        members_button.setToolTip("Show Guild Members Report")
        layout_header.addWidget(members_button)
        # noinspection PyUnresolvedReferences
        members_button.clicked.connect(self.members_report)

        self.load_zip_button = QtWidgets.QPushButton("Load from ZIP")
        # noinspection PyUnresolvedReferences
        self.load_zip_button.clicked.connect(self.load_zip_file)
        layout_header.addWidget(self.load_zip_button)

        self.list = QtWidgets.QListWidget()
        self.list.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(self.list, 1, 1, 1, 1)
        self.player = PlayerGui(self.foe_data)
        layout.addWidget(self.player, 1, 2, 1, 1)
        # noinspection PyUnresolvedReferences
        self.list.currentItemChanged.connect(self.player.update)

        for player in self.players:
            item = QtWidgets.QListWidgetItem(player)
            self.list.addItem(item)
        self.list.setCurrentRow(0)

    def report(self):
        expedition_report_data = get_expedition_report_data(self.foe_data.players)
        column_labels = ["Age", "Income", "Cost"]
        column_functions = [
            lambda expedition_age: QtWidgets.QTableWidgetItem(str(expedition_age["age"])),
            lambda expedition_age: QtWidgets.QTableWidgetItem(str(expedition_age["income"])),
            lambda expedition_age: QtWidgets.QTableWidgetItem(str(expedition_age["cost"])),
        ]
        window_title = "Expedition Level 2 Unlock Costs"
        dialog = DataTableDialog(window_title, expedition_report_data, column_labels, column_functions)
        dialog.exec_()

    def members_report(self):
        members_report_data = get_members_report_data(self.foe_data.players)
        sort_key = "overall_participation"
        sort_direction = SortDirection.DESCENDING
        column_labels = ["# Guild Rank", "Contribution", "Player Name", "Age"]
        column_functions = [
            lambda player: QtWidgets.QTableWidgetItem(str(player["rank"])),
            lambda player: QtWidgets.QTableWidgetItem(str(player["overall_participation"])),
            lambda player: QtWidgets.QTableWidgetItem(str(player["player_name"])),
            lambda player: QtWidgets.QTableWidgetItem(str(player["age"])),
        ]
        window_title = "Overall member participation"
        table_data = members_report_data.get_sorted_by_key(sort_key, sort_direction)
        dialog = DataTableDialog(window_title, table_data, column_labels, column_functions)
        dialog.exec_()

    def load_zip_file(self):
        selected_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', "Zip Files (*.zip)")
        filename = selected_file[0]
        if len(filename) <= 0:
            # no file selected / dialog cancelled
            return

        foe_data_read = read_foe_data_from_zip(filename)
        players_from_file = foe_data_read.players.get_all_players()
        if len(players_from_file) == 0:
            self.show_alert("Data not loaded", "Data could not be loaded from the selected file", QtWidgets.QMessageBox.Warning, QtWidgets.QMessageBox.Ok)
            return

        json.dump(foe_data_read, open("data.json", "w"), indent=4, default=vars)
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
