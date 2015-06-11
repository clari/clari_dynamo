# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import sys

os.environ['CLARI_DYNAMO_IS_TEST'] = 'True'
from clari_dynamo.conf.constants import *

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)

from clari_dynamo.clari_dynamo import ClariDynamo
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
import unittest

"""Tests for Clari Dynamo."""


class ClariDynamoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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

        tables = cls.db.conn.list_tables()
        assert len(tables['TableNames']) == 0, \
            'tables should be cleared at start of tests'

    def test_auth(self):
        try:
            ClariDynamo(
                aws_access_key        = 'test_db',
                aws_secret_access_key = 'test_key',
                host                  = 'localhost',
                port                  = 8001,
                is_remote             = False,
                in_memory             = True,
                is_secure             = False,
                auth_func=lambda: False)
        except ClariDynamo.AuthException:
            did_raise_exception = True
        else:
            did_raise_exception = False

        self.assertTrue(did_raise_exception, 'Should fail authorization')

    def test_binary_input(self):
        db, table_name = self.setup_stuff()
        expected = 'AA'
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,
                '$base64': True
            }
        }
        self.put_and_assert(db, expected, item, table_name)

    def setup_stuff(self):
        db = self.db
        table_name = self._testMethodName
        self.create_test_table(table_name)
        return db, table_name

    def test4_s3_kms_data(self):
        expected = 'awesome data'
        db, table_name = self.setup_stuff()
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,
                '$s3': True,
            }
        }
        self.put_and_assert(db, expected, item, table_name)

    def test_tenant_id_protection(self):
        db, table_name = self.setup_stuff()
        expected = 'tenant data'
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,

            }
        }
        self.put_and_assert(db, expected, item, table_name)

    def test_duplicate_error(self):
        db, table_name = self.setup_stuff()
        expected = 'unique data'
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,
            }
        }
        tenant_id = '123'
        db.put_item(table_name, item, tenant_id)
        did_raise_exception = False
        try:
            db.put_item(table_name, item, tenant_id)
        except ClariDynamo.ClariDynamoConditionCheckFailedException as e:
            did_raise_exception = True
            assert e.message.lower().find('duplicate') != -1
        assert did_raise_exception
        retrieved = db.get_item(table_name, tenant_id, id=self._testMethodName)
        db.delete_item(table_name, retrieved)
        db.drop_table(table_name)

    def put_and_assert(self, db, expected, item, table_name):
        tenant_id = '123'
        db.put_item(table_name, item, tenant_id)
        retrieved = db.get_item(table_name, tenant_id, id=self._testMethodName)
        self.assertEquals(retrieved['expected'], expected)
        db.delete_item(table_name, retrieved)
        db.drop_table(table_name)

    def create_test_table(self, name):
        return self.db.create_table(name,
            schema=[HashKey('id')],
            throughput={'read':  1, 'write':  1})


    @classmethod
    def tearDownClass(cls):
        cls.db.stop_local()