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
from PyQt4.QtGui import QStringListModel, QCompleter, QMessageBox
from qgis.core import QGis

from qgis.utils import plugins, pluginMetadata
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

        self._enable_widgets()

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

            desc += "{} {}\n".format(msg, error)

            self.DescriptionTextEdit.setText(desc)
            self.TitleEditLine.setText("Uncaught " + main_error)
            self.LabelsLineEdit.setText("bug")

    def _load_additional_info(self):
        plugin = self.PluginChooser.itemText(self.PluginChooser.currentIndex())

        qgis_info = str(QGis.QGIS_VERSION)
        platform_info = "{} {}".format(platform.system(), platform.release())
        plugin_info = "{} {}".format(plugin, pluginMetadata(plugin, "version"))

        txt = "{}, QGIS {} on {}".format(plugin_info, qgis_info, platform_info)

        self.AdditionalInfoLineEdit.setText(txt)

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
        self.TitleEditLine.editingFinished.connect(self._enable_widgets)

    def _set_no_err(self):
        self.ErrorLabel.setText("")
        self.ErrorLabel.hide()

    def _set_err(self, msg):
        self.ErrorLabel.setText("<font color=red>" + msg + "</font>")
        self.ErrorLabel.show()

    def _enable_widgets(self, dummy=None):
        if not self.TokenLineEdit.text():
            self._set_err("Missing GitHub Access Token")
            submit_ok = False
            git_ok = False
        elif not self.TrackerLabel.text():
            self._set_err("Missing Tracker")
            submit_ok = False
            git_ok = False
        elif not self.github:
            self._set_err("Invalid GitHub access token")
            submit_ok = False
            git_ok = False
        elif not self.TitleEditLine.text():
            self._set_err("Missing Title")
            submit_ok = False
            git_ok = True
        else:
            self._set_no_err()
            submit_ok = True
            git_ok = True

        self.IssueGroupBox.setEnabled(git_ok)
        if git_ok:
            self._load_labels()
        self.SubmitButton.setEnabled(submit_ok)

    def _load_labels(self):
        labels = self.github.get_labels()

        model = QStringListModel()
        completer_model = model
        compl = QCompleter()
        compl.setModel(model)
        compl.setCaseSensitivity(Qt.CaseInsensitive)
        compl.setMaxVisibleItems(50)
        compl.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        compl.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        completer_model.setStringList(labels)

        self.LabelsLineEdit.setCompleter(compl)
        self.LabelsLineEdit.setText("")

    def _token_selected(self):
        token = self.TokenLineEdit.text()
        self.github.set_access_token(token)
        self._save_settings("token", token)

        self._enable_widgets()

    def _plugin_selected(self):
        plugin = self.PluginChooser.itemText(self.PluginChooser.currentIndex())
        tracker = self.PluginChooser.itemData(self.PluginChooser.currentIndex())
        self.github.set_tracker(tracker)
        if tracker:
            self.TrackerLabel.setText(str(tracker))
        else:
            self.TrackerLabel.setText("")
        self._save_settings("plugin", plugin)

        self._enable_widgets()
        self._load_additional_info()

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
            additional_info = self.AdditionalInfoLineEdit.text()

            try:
                link, number = self.github.create_issue(title, labels, "{}\n{}".format(desc, additional_info))
                msgBox = QMessageBox()
                msgBox.setTextFormat(Qt.RichText)
                msgBox.setText("GitHub <a href='{}'>issue #{}</a> created".format(link, number));
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()

            except GitHubApiError as err:
                self._set_err(str(err))
                return

            self.accept()
        else:
           self._set_err("Invalid GitHub connection")

