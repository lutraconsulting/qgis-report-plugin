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
    raise ImportError
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

    def is_valid(self):
        return (self.tracker != None) and (self.access_token != None)

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

    def _post(self, key, payload):
        headers = {'Authorization': 'token ' + self.access_token}
        url = self.tracker + key
        r = requests.post(url, data=json.dumps(payload), headers=headers)

        ok_codes = ['200', '201', '202']

        if r.status_code in ok_codes:
            raise GitHubApiError("Invalid API GitHub Call ({})".format(r.status_code))

        return r.json()

    def _get(self, key):
        headers = {'Authorization': 'token ' + self.access_token}
        url = self.tracker + key
        r = requests.get(url, headers=headers)

        ok_codes = ['200', '201', '202']

        if r.status_code in ok_codes:
            raise GitHubApiError("Invalid API GitHub Call ({})".format(r.status_code))

        return r.json()

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

    def get_labels(self):
        labels = self._get("labels")
        ret = []
        for l in labels:
            ret += [l['name']]
        return ret
