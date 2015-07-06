# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import random
import string
from functools import wraps
from time import time

from builtins import (str, range, zip)

from clari_dynamo.conf.cd_logger import logging


def env(key, default=None):
    ret = os.environ.get('CLARI_DYNAMO_' + key, default)
    if default is not None and ret != default:
        if type(default) == bool:
            ret = ret == 'True' or ret == 'true'
        else:
            ret = type(default)(ret)
    return ret


def quick_random_str(n):
    """Quick random string of n characters - not cryptographically random"""
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


def secure_random_str(n):
    """Cryptographically random string of n characters
        10x slower than quick_random_str
    """
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(n))


