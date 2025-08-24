#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys

from PyQt5 import QtWidgets
from gui import UI


app = QtWidgets.QApplication(sys.argv)
app.setApplicationName("Forge of Empires Guild Tools")
app.setApplicationDisplayName("Forge of Empires Guild Tools")
app.setApplicationVersion("1.0")
Dialog = UI()
Dialog.show()
sys.exit(app.exec_())
