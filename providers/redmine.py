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


import json

from report import utils

from report.providers.provider_base import ProviderApiBase, ProviderApiError

try:
    import redmine
except ImportError:
    utils.add_deps('python_redmine-1.5.1-py2.py3-none-any.whl')
    import redmine

class RedmineApiError(ProviderApiError):
    pass

class RedmineProvider(ProviderApiBase):
    def _set_tracker(self, tracker):
        return tracker

    def is_my_tracker(self, tracker):
        return "hub.qgis.org" in str(tracker)

    def _save_credentials(self):
        token = utils.save_settings("redmine-token", self.credentials)

    def load_credentials(self):
        token = utils.load_settings("redmine-token")
        self._set_credentials(token)

    def create_issue(self, title, labels=None, description=None):
        return 'www.google.com', 1

    def _get_labels(self):
        return []

