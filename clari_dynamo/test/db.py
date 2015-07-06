# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
from clari_dynamo.clari_dynamo import ClariDynamo


class TestDB(object):
    db = None
    users = 0

    @classmethod
    def get(cls):
        if cls.db is None:
            cls.init()
        cls.users += 1
        return cls.db

    @classmethod
    def init(cls):
        cls.db = ClariDynamo(
            aws_access_key        = 'test_db',
            aws_secret_access_key = 'test_key',
            host                  = 'localhost',
            port                  = 8001,
            is_remote             = False,
            in_memory             = True,
            is_secure             = False,)

        if cls.db.host != 'localhost':
            raise Exception('must test on localhost')

        tables = cls.db.list_tables()
        assert len(tables) == 0, \
            'tables should be cleared at start of tests'

    @classmethod
    def release(cls):
        cls.users -= 1
        if cls.users <= 0:
            cls.db._stop_local()
            cls.db = None