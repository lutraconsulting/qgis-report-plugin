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
    import certifi
    cacert_file = certifi.where()
except ImportError:
    cacert_file = utils.get_file_path("deps", "cacert.pem")

try:
    import requests
except ImportError:
    utils.add_deps('requests-2.10.0-py2.py3-none-any.whl')
    import requests

class GitHubApiError(ProviderApiError):
    pass

class GitHubProvider(ProviderApiBase):
    def _set_tracker(self, tracker):
        API = "https://api.github.com/repos/"
        if tracker:
            tracker = tracker.replace("https://github.com/", API)
            tracker = tracker.replace("https://www.github.com/", API)
            tracker = tracker.replace("/issues/", "")
            tracker = tracker.replace("/issues", "")
            if not tracker.endswith("/"):
                tracker += "/"
        return tracker

    def is_my_tracker(self, tracker):
        return "github.com" in str(tracker)

    def _credential_settings_key(self):
        return "github-token"

    def _parse_response(self, resp):
        ok_codes = ['200', '201', '202']
        if resp.status_code in ok_codes:
            raise GitHubApiError("Invalid API GitHub Call ({})".format(resp.status_code))

        resp_json = resp.json()
        if isinstance(resp_json, dict):
            msg = resp_json.get("message", None)
            if msg and "Bad credentials" in msg:
                raise GitHubApiError("Invalid GitHub access token")

        return resp_json

    def _post(self, key, payload):
        headers = {'Authorization': 'token ' + self.credentials}
        url = self.tracker + key
        r = requests.post(url, data=json.dumps(payload), headers=headers, verify=cacert_file)
        return self._parse_response(r)

    def _get(self, key):
        headers = {'Authorization': 'token ' + self.credentials}
        url = self.tracker + key
        r = requests.get(url, headers=headers, verify=cacert_file)
        return self._parse_response(r)

    def create_issue(self, title, labels=None, description=None):
        payload = {}
        payload['title'] = title
        if description:
            payload['body'] = description
        if labels:
            payload['labels'] = labels

        resp = self._post("issues", payload)
        return resp['html_url'], resp['number']

    def _get_labels(self):
        labels = self._get("labels")
        ret = []
        for l in labels:
            ret += [{'name': l['name'], 'color': l['color']}]
        self.labels = ret
