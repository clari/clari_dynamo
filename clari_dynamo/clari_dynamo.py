# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)
from clari_dynamo.conf.constants import *

import random
import time
from datetime import datetime
import sys

# Hack for KMS patch - TODO: Remove after https://github.com/boto/boto/issues/2921
sys.path.insert(0, BOTO_PATH)

from boto.dynamodb2.exceptions import ProvisionedThroughputExceededException
from boto.dynamodb2.exceptions import ConditionalCheckFailedException
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table as BotoTable
from boto.dynamodb.types import Binary

from . import s3_kms
from .local_dynamo.localdb import LocalDb


class ClariDynamo(object):
    def __init__(self, aws_access_key, aws_secret_access_key, is_secure,
                 is_remote=False, host=None, port=None, in_memory=False,
                 auth_func=None):
        if auth_func and not auth_func():
            raise self.AuthException()

        self.host = host
        self.port = port
        self.is_secure = is_secure
        self.is_remote = is_remote
        self.in_memory = in_memory
        kwargs = {
            'aws_access_key_id':     aws_access_key,
            'aws_secret_access_key': aws_secret_access_key,
            'is_secure':             is_secure
        }
        if not is_remote:
            kwargs['host'] = host
            kwargs['port'] = port
            self.local_db = LocalDb(port, in_memory)

        self.conn = DynamoDBConnection(
            aws_access_key_id     = aws_access_key,
            aws_secret_access_key = aws_secret_access_key,
            host                  = host,
            port                  = port,
            is_secure             = is_secure)

    def get_item(self, table, tenant_id, **id_query):
        item = table.get_item(**id_query)
        assert item['tenant_id'] == CRYPTO.decrypt(bytes(
            item['encrypted_tenant_id'], 'UTF-8'))
        self._check_for_meta(item._data, table, operation='get')
        return item

    def put_item(self, table, item, tenant_id):
        assert type(item) == dict
        isinstance(tenant_id, str)
        item['tenant_id'] = tenant_id
        item['encrypted_tenant_id'] = CRYPTO.encrypt(bytes(tenant_id, 'UTF-8'))
        item['created_at'] = str(datetime.now())
        self._check_for_meta(item, table, operation='put')
        return self._put_with_retries(table, item, retry=0)

    def delete_item(self, table, item):
        data = item._data
        assert type(data) == dict
        self._check_for_meta(data, table, operation='delete')
        item.delete()

    def create_table(self, name, **kwargs):
        return BotoTable.create(name, connection=self.conn, **kwargs)

    def drop_table(self, name):
        return self.conn.delete_table(name)

    def get_table(self, name, **kwargs):
        return BotoTable(name, connection=self.conn, **kwargs)

    def stop_local(self):
        if not self.is_remote:
            self.local_db.stop()

    def _handle_s3_backed_item(self, table, operation, parent, key, value):
        if operation == 'get':
            value['$data'] = s3_kms.get(value["$s3_key"])
        elif operation == 'put':
            s3_key = s3_kms.put(table.table_name, key, value['$data'])
            value['$s3_key'] = s3_key.key
            del value['$data']
        elif operation == 'delete':
            s3_kms.delete(value["$s3_key"])

    def _handle_base64_item(self, table, operation, parent, key, value):
        if operation == 'get':
            pass
        elif operation == 'put':
            binary_data = Binary('')

            #  base64 comes in from API, so set directly (minor hack)
            binary_data.value = value['$data']

            assert(len(value) == 2,
                   'only $data and $base64 should be set on binary item')

            parent[key] = binary_data

        elif operation == 'delete':
            pass

    def _check_for_meta(self, item, table, operation):
        for key, value in item.iteritems():
            if type(value) == dict:
                # Read meta info
                if value.get("$s3"):
                    self._handle_s3_backed_item(table, operation, item, key,
                                                value)
                if value.get('$base64'):
                    self._handle_base64_item(table, operation, item, key, value)
            if type(value) in (dict, list):
                self._check_for_meta(value, table, operation)

    def _put_with_retries(self, table, data, retry):
        try:
            table.put_item(data)
        except ProvisionedThroughputExceededException as e:
            if RETRY_ON_THROUGHPUT_EXCEEDED and retry < 4:
                logging.warn(
                    'ProvisionedThroughputExceededException retrying: ' +
                    str(retry))
                time.sleep(2 ** retry * random.random())  # random => ! herd
                self._put_with_retries(data, table, retry + 1)
            else:
                raise e
        except ConditionalCheckFailedException as e:
            raise self.ClariDynamoConditionCheckFailedException(str(e) + ' - ' +
                'This could be due to a duplicate insertion.')
        # TODO: Handle too large exception by compressing or s3 if non-indexed
        except Exception as e:
            print(e)
            raise e

    class AuthException(Exception):
        pass

    class ClariDynamoConditionCheckFailedException(Exception):
        pass