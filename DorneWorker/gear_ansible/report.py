# -*- coding: utf-8 -*-

import requests
import json
from requests.exceptions import Timeout, HTTPError, ConnectionError
from ansible.parsing.ajson import AnsibleJSONEncoder


class Report(object):
    """report result"""

    def __init__(self, callback_url, callback_method='POST'):
        self._callback_url = callback_url
        self._callback_method = callback_method

    def report(self, msg, status=0):
        """"""
        try:
            if self._callback_method == "POST":
                msg_struct = dict(
                    status=status,
                    msg=msg
                )
                payload = json.dumps(msg_struct, cls=AnsibleJSONEncoder,
                                     sort_keys=True)
                r = requests.post(self._callback_url, data=payload,
                                  timeout=(4, 15))
                r.raise_for_status()
            else:
                pass

        # TODO: log error
        except Timeout:
            pass
        except HTTPError:
            pass
        except ConnectionError:
            pass
