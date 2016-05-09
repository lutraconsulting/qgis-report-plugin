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

from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources

import main_widget

class ReportPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.main_widget = None

    def initGui(self):
        icon = QIcon(':/plugins/qgis-report-plugin/images/icon.png')
        self.action = QAction(icon, "Report!", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

        self.main_dlg = None

    def run(self):
        self.main_widget = main_widget.MainWidget(self.iface)
        self.main_widget.show()
        self.main_widget.exec_()
