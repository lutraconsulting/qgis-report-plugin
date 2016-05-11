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

from PyQt4 import uic
import platform
import traceback

import utils
from github_utils import GitHubApiError, GitHubApi
from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QListWidgetItem, QMessageBox
from qgis.core import QGis

from qgis.utils import available_plugins, pluginMetadata
from qgis.utils import iface

ui_file = utils.get_file_path('conf_widget.ui')
uiWidget, qtBaseClass = uic.loadUiType(ui_file)

class ConfigurationWidget(qtBaseClass, uiWidget):
    def __init__(self, parent=None):
        qtBaseClass.__init__(self, parent)
        self.setupUi(self)
        self._load_settings()


    def _load_settings(self):
        token = utils.load_settings("token")
        if token:
            self.TokenLineEdit.setText(token)
        else:
            self.TokenLineEdit.setText("")

    def _connect_signals(self):
        self.TokenLineEdit.editingFinished.connect(self._token_selected)

    def _token_selected(self):
        self._save_settings("token", token)
