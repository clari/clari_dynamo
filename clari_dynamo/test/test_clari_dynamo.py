# -*- coding: utf-8 -*-
import os
import sys

from conf.constants import *

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)

os.environ['CLARI_DYNAMO_TEST'] = 'True'

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
        db = self.db
        table_name = 'test__binary_input'
        table = self.create_test_table(table_name)

        base64_data = 'AA'
        db.put_item(table, {'id': 'asdf', 'binaryTest': {
            '$data': base64_data,
            '$base64': True
        }})

        retrieved = table.get_item(id='asdf')
        self.assertEquals(retrieved['binaryTest'], base64_data)
        db.drop_table(table_name)

    def test4_s3_kms_data(self):
        db = self.db
        table_name = 'test__s3_kms_input'
        table = self.create_test_table(table_name)
        details = 'awesome data'
        item = {
            'id': 'test-kms-s3',
            'details': {
                '$data': details,
                '$s3': True,
            }
        }

        db.put_item(table, item)
        retrieved = db.get_item(table, id='test-kms-s3')
        self.assertEquals(retrieved['details']['$data'], details)
        db.delete_item(table, retrieved)
        db.drop_table(table_name)

    def create_test_table(self, name):
        return self.db.create_table(name,
            schema=[HashKey('id')],
            throughput={'read':  1, 'write':  1})


    @classmethod
    def tearDownClass(cls):
        cls.db.stop_local()