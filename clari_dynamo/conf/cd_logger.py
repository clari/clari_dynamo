# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import logging

FORMAT = \
"%(asctime)s %(pathname)s:%(lineno)s:%(funcName)s - %(levelname)s - %(message)s"

logging.basicConfig(
    level=logging.DEBUG,
    format=FORMAT)