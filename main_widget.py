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

        self._enable_issues_group()

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

            self._find_plugin_from_exception(error)

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
        self.TitleEditLine.editingFinished.connect(self._enable_submit)

    def _set_no_err(self, widget):
        widget.setText("")
        widget.hide()

    def _set_err(self, widget, msg):
        if msg:
            widget.setText("<font color=red>" + msg + "</font>")
            widget.show()
        else:
            self._set_no_err(widget)

    def _enable_issues_group(self, dummy=None):
        submit_err = None
        git_err = None
        if not self.TokenLineEdit.text():
            git_err = "Missing GitHub Access Token"
        elif not self.TrackerLabel.text():
            git_err = "Missing \"tracker\" entry in plugin metadata. Please fix the plugin"
        elif not ("github.com" in self.TrackerLabel.text()):
            git_err = "Only GitHub issue trackers are currently supported."
        elif (not self.github) or (not self.github.is_valid()):
            git_err =  "Invalid GitHub tracker and token combination"
        elif not self.TitleEditLine.text():
            submit_err = "Missing Title"


        self._set_err(self.TrackerErrorLabel, git_err)

        self.IssueGroupBox.setEnabled(git_err == None)
        self.SubmitButton.setEnabled(git_err == None and submit_err == None)

        self._enable_submit()

        if not git_err:
            self._load_labels()

    def _enable_submit(self, dummy=None):
        submit_err = None
        if not self.TitleEditLine.text():
            submit_err = "Missing Title"

        self._set_err(self.TitleErrorLabel, submit_err)
        self.SubmitButton.setEnabled(submit_err == None)

    def _load_labels(self):
        labels = self.github.get_labels()
        self.LabelsListWidget.clear()
        for label in labels:
            icon = utils.colored_icon(label['color'])
            item = QListWidgetItem(icon, label['name'], self.LabelsListWidget)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.LabelsListWidget.addItem(item)
        self.LabelsListWidget.sortItems()

    def _token_selected(self):
        token = self.TokenLineEdit.text()
        self.github.set_access_token(token)
        self._save_settings("token", token)

        self._enable_issues_group()

    def _plugin_selected(self):
        plugin = self.PluginChooser.itemText(self.PluginChooser.currentIndex())
        tracker = self.PluginChooser.itemData(self.PluginChooser.currentIndex())
        self.github.set_tracker(tracker)
        if tracker:
            self.TrackerLabel.setText("<a href=\"{}\">{}</a>".format(tracker, tracker))
        else:
            self.TrackerLabel.setText("")

        self._save_settings("plugin", plugin)

        self._enable_issues_group()
        self._load_additional_info()

    def _load_available_trackers(self):
        self.PluginChooser.addItem("", None)
        plugins_to_show = sorted(available_plugins, key=lambda s: s.lower())
        for plugin_name in plugins_to_show:
            if plugin_name:
                tracker = pluginMetadata(plugin_name, 'tracker')
                if "error" in tracker:
                    tracker = ""

                self.PluginChooser.addItem(plugin_name, tracker)

    def _selected_labels(self):
        labels = []
        for row in range(self.LabelsListWidget.count()):
            item = self.LabelsListWidget.item(row)
            if item.checkState() == Qt.Checked:
                labels += [item.text()]
        print labels
        return labels

    def _submit_issue(self):
        if self.github.is_valid():
            title = self.TitleEditLine.text()
            labels = self._selected_labels()
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

