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
from PyQt4.QtCore import QSettings
from qgis.core import QGis

from qgis.utils import plugins, pluginMetadata, pluginDirectory
from qgis.utils import iface

ui_file = utils.get_file_path('main_widget.ui')
uiWidget, qtBaseClass = uic.loadUiType(ui_file)

class MainWidget(qtBaseClass, uiWidget):
    def __init__(self, last_exception=None, parent=None):
        qtBaseClass.__init__(self, parent)
        self.setupUi(self)
        self.github = GitHubApi()
        self.last_exception = last_exception

        self._connect_signals()

        self._load_available_trackers()
        self._load_settings()

        self._load_last_error()
        self._load_additional_info()

        self._enable_submit()

    def _save_settings(self, key, val):
        settings = QSettings()
        settings.beginGroup("/qgis-report-plugin")
        settings.setValue(key, val)

    def _find_plugin_from_exception(self, exc_fileline):
         items = [self.PluginChooser.itemText(i) for i in range(self.PluginChooser.count())]
         for item in items:
            if item and item in exc_fileline: #skip empty item
                self._set_chosen_plugin(item)
                return
         self._set_err("unable to determine plugin from exception text")


    def _load_last_error(self):
        if self.last_exception:
            desc = self.DescriptionTextEdit.toPlainText()

            msg = self.last_exception['msg']
            if msg is None:
                msg = ""

            error = ''

            lst = traceback.format_exception(self.last_exception['etype'], self.last_exception['value'], self.last_exception['tb'])
            for s in lst:
                error += s.decode('utf-8', 'replace') if hasattr(s, 'decode') else s

            main_error = lst[-1].decode('utf-8', 'replace') if hasattr(lst[-1], 'decode') else lst[-1]

            fileline = lst[-2].decode('utf-8', 'replace') if hasattr(lst[-2], 'decode') else lst[-2]
            self._find_plugin_from_exception(fileline)

            desc += "\n{} {}".format(msg, error)

            self.DescriptionTextEdit.setText(desc)
            self.TitleEditLine.setText("Uncaught " + main_error)
            self.LabelsLineEdit.setText("bug")

    def _load_additional_info(self):
        desc = self.DescriptionTextEdit.toPlainText()
        desc += "\nQGIS {} on {} {}\n".format(QGis.QGIS_VERSION, platform.system(), platform.release())
        self.DescriptionTextEdit.setText(desc)

    def _set_chosen_plugin(self, plugin):
        idx = self.PluginChooser.findText(plugin)
        if idx != -1:
            self.PluginChooser.setCurrentIndex(idx)
        self._plugin_selected()

    def _load_settings(self):
        settings = QSettings()
        settings.beginGroup("/qgis-report-plugin")

        token = settings.value("token", "", type=str)
        self.TokenLineEdit.setText(token)
        self._token_selected()

        plugin = settings.value("plugin", "", type=str)
        self._set_chosen_plugin(plugin)

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

