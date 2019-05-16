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

from PyQt5 import uic
from .utils import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


ui_file = get_ui_file('conf_widget.ui')
uiWidget, qtBaseClass = uic.loadUiType(ui_file)


class ConfigurationWidget(qtBaseClass, uiWidget):

    def __init__(self, provider, parent=None):
        qtBaseClass.__init__(self, parent)
        self.setupUi(self)
        self.provider = provider
        self._connect_signals()
        self._load_settings()

    def _load_settings(self):
        github = self.provider['github']
        self.GitTokenLineEdit.setText(github.get_credentials())

    def _connect_signals(self):
        self.GitTokenLineEdit.editingFinished.connect(self._token_selected)
        self.GitOkButton.clicked.connect(self._ok_clicked)
        self.GitHelpButton.clicked.connect(self._git_help_wanted)

    def _git_help_wanted(self):
        html = get_file_path('doc', 'github_token.html')
        url = QUrl.fromLocalFile(html)
        QDesktopServices.openUrl(url)

    def _ok_clicked(self):
        self._token_selected()
        self.close()

    def _token_selected(self):
        git_token = self.GitTokenLineEdit.text()
        self.provider['github'].set_credentials(git_token)

    def closeEvent(self, e):
        self._token_selected()
        qtBaseClass.closeEvent(self, e)
