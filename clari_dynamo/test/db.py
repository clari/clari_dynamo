# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)
from clari_dynamo.conf.constants import *

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
        if TEST_REMOTE:
            cls.db = cls.get_remote_db()
        else:
            cls.db = cls.get_local_db()

    @classmethod
    def get_remote_db(cls):
        assert ENV_NAME == 'test'
        ret = ClariDynamo(
            aws_access_key        = AWS_ACCESS_KEY_ID,
            aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
            is_remote             = True,
            in_memory             = False,
            is_secure             = True,)
        return ret

    @classmethod
    def get_local_db(cls):
        ret = ClariDynamo(
            aws_access_key        = 'test_db',
            aws_secret_access_key = 'test_key',
            host                  = 'localhost',
            port                  = 8001,
            is_remote             = False,
            in_memory             = True,
            is_secure             = False,)

        if ret.host != 'localhost':
            raise Exception('must test on localhost')

        tables = ret.list_tables()
        assert len(tables) == 0, \
            'tables should be cleared at start of tests'

        return ret

    @classmethod
    def release(cls):
        cls.users -= 1
        if cls.users <= 0:
            if not TEST_REMOTE:
                cls.db._stop_local()
            cls.db = None