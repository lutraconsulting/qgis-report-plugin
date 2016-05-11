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

import utils
import json

try:
    import requests
except ImportError:
    import os
    import sys
    request_egg = utils.get_file_path('deps', 'requests-2.10.0-py2.py3-none-any.whl')
    sys.path.append(request_egg)
    import requests

class GitHubApiError(Exception):
    pass

class GitHubApi():
    def __init__(self):
        self.tracker = None
        self.access_token = None
        self.labels = []

    def is_valid(self):
        is_initialized = (self.tracker != None) and (self.access_token != None)
        if is_initialized:
            try:
                # try to fetch labels to test token
                self._get_labels()
                return True
            except GitHubApiError:
                return False
        else:
            return False

    def set_tracker(self, tracker):
        API = "https://api.github.com/repos/"
        if tracker:
            tracker = tracker.replace("https://github.com/", API)
            tracker = tracker.replace("https://www.github.com/", API)
            tracker = tracker.replace("/issues/", "")
            tracker = tracker.replace("/issues", "")
            if not tracker.endswith("/"):
                tracker += "/"

        self.tracker = tracker

    def set_access_token(self, access_token):
        if access_token:
            access_token = access_token.strip()
        self.access_token = access_token

    def _parse_response(self, resp):
        ok_codes = ['200', '201', '202']
        if resp.status_code in ok_codes:
            raise GitHubApiError("Invalid API GitHub Call ({})".format(resp.status_code))

        resp_json = resp.json()
        if isinstance(resp_json, dict):
            msg = resp_json.get("message", None)
            if "Bad credentials" in msg:
                raise GitHubApiError("Invalid GitHub access token")

        return resp_json
    
    def _post(self, key, payload):
        headers = {'Authorization': 'token ' + self.access_token}
        url = self.tracker + key
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return self._parse_response(r)

    def _get(self, key):
        headers = {'Authorization': 'token ' + self.access_token}
        url = self.tracker + key
        r = requests.get(url, headers=headers)
        return self._parse_response(r)

    def create_issue(self, title, labels=None, description=None):
        payload = {}
        payload['title'] = title
        if description:
            payload['body'] = description
        if labels:
            lab_arr = labels.split(" ;")
            payload['labels'] = lab_arr

        resp = self._post("issues", payload)
        return resp['html_url'], resp['number']

    def _get_labels(self):
        labels = self._get("labels")
        ret = []
        for l in labels:
            ret += [l['name']]
        self.labels = ret

    def get_labels(self):
        return self.labels
