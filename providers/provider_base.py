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

from report import utils


class ProviderApiError(Exception):
    pass

class ProviderApiBase():
    def __init__(self):
        self.tracker = None
        self.credentials = None
        self.labels = []

    def is_valid(self):
        is_initialized = (self.tracker != None) and (self.credentials != None)
        if is_initialized:
            try:
                # try to fetch labels to test token
                self._get_labels()
                return True
            except ProviderApiError:
                return False
        else:
            return False

    def set_tracker(self, tracker):
        if tracker:
            tracker = self._set_tracker(tracker)
        self.tracker = tracker

    def _set_credentials(self, credentials):
        if credentials:
            credentials = credentials.strip()
        self.credentials = credentials

    def set_credentials(self, credentials):
        self._set_credentials(credentials)
        self._save_credentials()

    def get_credentials(self):
        return self.credentials

    def get_labels(self):
        return self.labels

    def _save_credentials(self):
        utils.save_settings(self._credential_settings_key(), self.credentials)

    def load_credentials(self):
        token = utils.load_settings(self._credential_settings_key())
        self._set_credentials(token)

    ######################

    def _credential_settings_key(self):
        raise NotImplementedError()

    def _set_tracker(self, tracker):
        # returns tracker
        raise NotImplementedError()

    def create_issue(self, title, labels=None, description=None):
        # returns (html_url, number)
        raise NotImplementedError()

    def _get_labels(self):
        # returns [{name: name, color: color}]
        raise NotImplementedError()

    def is_my_tracker(self, tracker):
        # returns bool
        raise NotImplementedError()
