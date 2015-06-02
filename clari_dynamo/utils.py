# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function,unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import base64
import uuid


def env(key, default=None):
    ret = os.environ.get(key, default)
    if default is not None and ret != default:
        if type(default) == bool:
            ret = ret == 'True' or ret == 'true'
        else:
            ret = type(default)(ret)
    return ret


def get_a_uuid():
    """ Get a UUID - URL safe, Base64 """
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.replace('=', '')