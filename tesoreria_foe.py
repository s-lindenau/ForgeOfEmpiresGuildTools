#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import sys
import logging

from PyQt5 import QtWidgets, QtGui
from foe_helper_file_reader import read_foe_data_from_zip
from util.application import application_data
from lib import read_data_from_stored_json
from view.gui import UI

# Change to DEBUG for more verbose output
LOG_LEVEL = logging.WARNING

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        zip_path_command_line_argument = sys.argv[1]
        foe_data_read = read_foe_data_from_zip(zip_path_command_line_argument)
        players_from_file = foe_data_read.players.get_all_players()
        if len(players_from_file) > 0:
            json.dump(foe_data_read, open("data.json", "w"), indent=4, default=vars)

app = QtWidgets.QApplication(sys.argv)
app.setApplicationName(application_data.get("name"))
app.setApplicationDisplayName(application_data.get("name"))
app.setApplicationVersion(application_data.get("version"))
app.setWindowIcon(QtGui.QIcon("images/application/foe_guild_tools_icon.ico"))
Dialog = UI(read_data_from_stored_json())
Dialog.show()
sys.exit(app.exec_())
