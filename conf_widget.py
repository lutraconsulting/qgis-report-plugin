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
from provider import *
from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QListWidgetItem, QMessageBox
from qgis.core import QGis

from qgis.utils import available_plugins, pluginMetadata
from qgis.utils import iface

ui_file = utils.get_ui_file('conf_widget.ui')
uiWidget, qtBaseClass = uic.loadUiType(ui_file)

class ConfigurationWidget(qtBaseClass, uiWidget):
    def __init__(self, provider, parent=None):
        qtBaseClass.__init__(self, parent)
        self.setupUi(self)
        self.provider = provider
        self._load_settings()

    def _load_settings(self):
        github = self.provider['github']
        self.TokenLineEdit.setText(github.get_credentials())

    def _connect_signals(self):
        self.TokenLineEdit.editingFinished.connect(self._token_selected)

    def _token_selected(self):
        access_token = self.TokenLineEdit.text()
        self.provider['github'].set_credentials(access_token)

    def closeEvent(self, e):
        self._token_selected()
        qtBaseClass.closeEvent(self, e)
