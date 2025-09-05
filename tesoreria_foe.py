#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys

from PyQt5 import QtWidgets
from gui import UI

import logging

# Change to DEBUG for more verbose output
LOG_LEVEL = logging.WARNING

logging.basicConfig(
    level = LOG_LEVEL,
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

app = QtWidgets.QApplication(sys.argv)
app.setApplicationName("Forge of Empires Guild Tools")
app.setApplicationDisplayName("Forge of Empires Guild Tools")
app.setApplicationVersion("1.0")
Dialog = UI()
Dialog.show()
sys.exit(app.exec_())
