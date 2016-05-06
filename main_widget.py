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
import utils
from github_utils import GitHubApiError, GitHubApi
from PyQt4.QtCore import QSettings

from qgis.utils import plugins, pluginMetadata

ui_file = utils.get_file_path('main_widget.ui')
uiWidget, qtBaseClass = uic.loadUiType(ui_file)

class MainWidget(qtBaseClass, uiWidget):
    def __init__(self,iface, parent=None):
        qtBaseClass.__init__(self, parent)
        self.setupUi(self)
        self.iface = iface

        self.github = GitHubApi()


        self._connect_signals()

        self._load_available_trackers()
        self._load_settings()

        self._enable_submit()

    def _save_settings(self, key, val):
        settings = QSettings()
        settings.beginGroup("/qgis-report-plugin")
        settings.setValue(key, val)

    def _load_settings(self):
        settings = QSettings()
        settings.beginGroup("/qgis-report-plugin")

        token = settings.value("token", "", type=str)
        self.TokenLineEdit.setText(token)
        self._token_selected()

        plugin = settings.value("plugin", "", type=str)
        idx = self.PluginChooser.findText(plugin)
        if idx != -1:
            self.PluginChooser.setCurrentIndex(idx)
        self._plugin_selected()

    def _connect_signals(self):
        self.PluginChooser.activated.connect(self._plugin_selected)
        self.TokenLineEdit.editingFinished.connect(self._token_selected)
        self.SubmitButton.clicked.connect(self._submit_issue)
        self.TitleEditLine.editingFinished.connect(self._enable_submit)

    def _set_no_err(self):
        self.ErrorLabel.setText("")
        self.ErrorLabel.hide()

    def _set_err(self, msg):
        self.ErrorLabel.setText("<font color=red>" + msg + "</font>")
        self.ErrorLabel.show()

    def _enable_submit(self, dummy=None):
        if not self.TokenLineEdit.text():
            self._set_err("Missing GitHub Access Token")
            ok = False
        elif not self.TrackerLabel.text():
            self._set_err("Missing Tracker")
            ok = False
        elif not self.github:
            self._set_err("Invalid GitHub access token")
            ok = False
        elif not self.TitleEditLine.text():
            self._set_err("Missing Title")
            ok = False
        else:
            self._set_no_err()
            ok = True

        self.SubmitButton.setEnabled(ok)

    def _token_selected(self):
        token = self.TokenLineEdit.text()
        self.github.set_access_token(token)
        self._save_settings("token", token)

        self._enable_submit()

    def _plugin_selected(self):
        plugin = self.PluginChooser.itemText(self.PluginChooser.currentIndex())
        tracker = self.PluginChooser.itemData(self.PluginChooser.currentIndex())
        self.github.set_tracker(tracker)
        self.TrackerLabel.setText(str(tracker))
        self._save_settings("plugin", plugin)

        self._enable_submit()

    def _load_available_trackers(self):
        self.PluginChooser.addItem("", None)
        for pl in plugins.keys():
            if pl:
                tracker = pluginMetadata(pl, 'tracker')
                if "github.com" in tracker:
                    self.PluginChooser.addItem(pl, tracker)

    def _submit_issue(self):
        if self.github.is_valid() == True:
            title = self.TitleEditLine.text()
            labels = self.LabelsLineEdit.text()
            desc = self.DescriptionTextEdit.toPlainText()

            try:
                self.github.create_issue(title, labels, desc)
            except GitHubApiError as err:
                self._set_err(str(err))
                return

            self.accept()
        else:
           self._set_err("Invalid GitHub connection")

