#-----------------------------------------------------------
# Copyright (C) 2016 Peter Petrik for Lutra Consulting
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qgis.utils
from .main_widget import *
from .resources import *

old_show_exception = None
report_dialog = None
last_error = None


def close_report_dialog():
    global report_dialog
    if report_dialog:
        report_dialog.close()
        report_dialog = None


def show_report_dialog(last_error=None):
    global report_dialog
    close_report_dialog()
    report_dialog = MainWidget(last_error)
    report_dialog.show()


def show_report_exception(etype, value, tb, msg, *args, **kwargs):
    global old_show_exception

    if old_show_exception:
        old_show_exception(etype, value, tb, msg, *args, **kwargs)

    reply = QMessageBox.question(None,
                                 "Confirmation",
                                 "Do you want to report the bug?",
                                 QMessageBox.Yes | QMessageBox.No)

    if reply == QMessageBox.Yes:
        last_error = {'etype': etype, 'value': value, 'tb': tb, 'msg': msg}
        show_report_dialog(last_error)


class ReportPlugin:
    def __init__(self, iface):
        self.action = None
        self.iface = iface

    def initGui(self):
        icon = QIcon(':/plugins/report/images/icon.png')
        self.action = QAction(icon, "Report!", self.iface.mainWindow())
        self.action.triggered.connect(show_report_dialog)
        self.iface.addToolBarIcon(self.action)

        # hook to exception handling
        global old_show_exception
        old_show_exception = qgis.utils.showException
        qgis.utils.showException = show_report_exception

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

        close_report_dialog()

        # unhook from exception handling
        global old_show_exception
        qgis.utils.showException = old_show_exception

