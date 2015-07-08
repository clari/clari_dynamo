# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

from clari_dynamo.migrate.common_imports import *


def run(db):
    db.drop_table('test_run_migration_a')
    pass