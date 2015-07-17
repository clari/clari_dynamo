# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import sys
os.environ['CLARI_DYNAMO_IS_TEST'] = 'True'

from clari_dynamo.conf.constants import *

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)

from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
import unittest

from clari_dynamo.clari_dynamo import get_double_reads, get_double_writes
from clari_dynamo.clari_dynamo import ClariDynamo
from clari_dynamo.test.db import TestDB
from clari_dynamo.conf.cd_logger import logging

"""Tests for Clari Dynamo."""


class ClariDynamoTest(unittest.TestCase):
    def setup_stuff(self):
        db = self.db
        table_name = self._testMethodName
        self.create_test_table(table_name)
        return db, table_name

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
        self.put_get_delete(db, expected, item, table_name)

    def test_s3_kms_data(self):
        expected = 'awesome data'
        db, table_name = self.setup_stuff()
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,
                '$s3': True,
            }
        }
        self.put_get_delete(db, expected, item, table_name)

    def test_get_partial_item(self):
        expected = 'awesome data'
        db, table_name = self.setup_stuff()
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,
                '$s3': True,
            }
        }
        tenant_id, test_name = self.put(db, item, table_name)
        attributes = ['id']
        retrieved = db.get_item(table_name, tenant_id, purpose=test_name,
                        attributes=attributes, id=test_name)
        self.assertTrue('expected' not in retrieved)
        self.assertEquals(1, len(retrieved._data))

    def test_tenant_id_protection(self):
        db, table_name = self.setup_stuff()
        expected = 'tenant data'
        item = {
            'id': self._testMethodName,
            'expected': {
                '$data': expected,

            }
        }
        self.put_get_delete(db, expected, item, table_name)

    def test_duplicate_error(self):
        db, table_name = self.setup_stuff()
        test_name = purpose = self._testMethodName
        expected = 'unique data'
        item = {
            'id': test_name,
            'expected': {
                '$data': expected,
            }
        }
        tenant_id = '123'
        db.put_item(table_name, item, tenant_id, purpose)
        did_raise_exception = False
        before = db.get_item(table_name, tenant_id, purpose, id=test_name)
        try:
            db.put_item(table_name, item, tenant_id, purpose)
        except ClariDynamo.ClariDynamoConditionCheckFailedException as e:
            did_raise_exception = True
            assert e.message.lower().find('duplicate') != -1
        after = db.get_item(table_name, tenant_id, purpose, id=test_name)
        self.assertEquals(before['updated_at'], after['updated_at'])
        self.assertTrue(did_raise_exception)
        retrieved = db.get_item(table_name, tenant_id, purpose, id=test_name)
        db.delete_item(table_name, retrieved, tenant_id, purpose)

    def test_overwrite(self):
        db, table_name = self.setup_stuff()
        test_name = purpose = self._testMethodName
        expected = 'unique data'
        item = {
            'id': test_name,
            'expected': {
                '$data': expected,
            }
        }
        tenant_id = '123'
        db.put_item(table_name, item, tenant_id, purpose)
        before = db.get_item(table_name, tenant_id, purpose, id=test_name)
        db.put_item(table_name, item, tenant_id, purpose, overwrite=True)
        after = db.get_item(table_name, tenant_id, purpose, id=test_name)
        self.assertNotEquals(before['updated_at'], after['updated_at'])
        db.delete_item(table_name, after, tenant_id, purpose)

    def test_successful_throttled_operation(self):
        try_msg = 'trying'
        try_function = lambda: print(try_msg)
        self.try_throttled_operation(try_function)

    def test_exceeded_throttled_operation(self):
        from boto.dynamodb2.exceptions import ProvisionedThroughputExceededException
        self._test_exceeded_throttled_operation_attempts = 0

        def throughput_exceeded():
            self._test_exceeded_throttled_operation_attempts += 1
            raise ProvisionedThroughputExceededException('test', 'test')

        try:
            self.try_throttled_operation(throughput_exceeded)
        except ProvisionedThroughputExceededException:
            pass
        else:
            self.fail('Should have thrown ProvisionedThroughputExceededException')

        self.assertGreater(self._test_exceeded_throttled_operation_attempts, 0,
                           'Should have retried at least once')

        self.db.wait_for_table_to_become_active(
            self.db.get_table(self._testMethodName), self._testMethodName)
        pass

    def test_change_throughput_error(self):
        db, table_name = self.setup_stuff()
        boto_table = db.get_table(table_name)
        db._handle_throughput_exceeded(
            get_double_reads(boto_table), 0,
            boto_table)
        db._handle_throughput_exceeded(
            get_double_reads(boto_table), 0,
            boto_table)
        db.wait_for_table_to_become_active(boto_table, table_name)

    def test_list_tables(self):
        db, table_name = self.setup_stuff()
        tables = db.list_tables()
        self.assertGreater(len(tables), 0)

    def try_throttled_operation(self, try_function):
        db, table_name = self.setup_stuff()
        boto_table = db.get_table(table_name)
        db._attempt_throttled_operation(
            try_function=try_function,
            retry_number=0,
            boto_table=boto_table,
            increased_throughput=get_double_reads(
                db.get_table(table_name)))
        db._attempt_throttled_operation(
            try_function=try_function,
            retry_number=0,
            boto_table=boto_table,
            increased_throughput=get_double_writes(
                db.get_table(table_name)))

    def put(self, db, item, table_name):
        tenant_id = '123'
        test_name = self._testMethodName
        db.put_item(table_name, item, tenant_id, purpose=test_name)
        return tenant_id, test_name

    def put_get(self, db, expected, item, table_name):
        tenant_id, test_name = self.put(db, item, table_name)
        retrieved = db.get_item(table_name, tenant_id, purpose=test_name,
                                id=test_name)
        self.assertEquals(retrieved['expected'], expected)
        return retrieved, tenant_id, test_name

    def put_get_delete(self, db, expected, item, table_name):
        retrieved, tenant_id, test_name = self.put_get(db, expected, item,
                                                       table_name)
        db.delete_item(table_name, retrieved, tenant_id, purpose=test_name)

    def create_test_table(self, name):
        return self.db.create_table(name,
            schema=[HashKey('id')],
            throughput={'read':  10, 'write':  5})

    def tearDown(self):
        if self.db.has_table(self._testMethodName):
            self.db.drop_table(self._testMethodName)

    @classmethod
    def setUpClass(cls):
        # sets self.db in methods
        cls.db = TestDB.get()

    @classmethod
    def tearDownClass(cls):
        TestDB.release()