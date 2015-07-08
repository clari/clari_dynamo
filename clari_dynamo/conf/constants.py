# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import json

from cryptography.fernet import Fernet
from clari_dynamo.conf.cd_logger import logging
from clari_dynamo.utils import env

DIR = os.path.dirname(os.path.abspath(__file__))

if os.path.isfile(DIR + '/secrets.py'):
    import clari_dynamo.conf.secrets
else:
    print('No secrets.py found, request access, set the variables documented in '
          'secrets.example.py')

#######################################################################
# Please don't put sensitive information here. Use secrets.py instead.
#######################################################################

# Used by boto to set signing method for AWS
os.environ['S3_USE_SIGV4'] = 'True'

HOME_TEXT = {
    'clari_dynamo': {
        'routes': [
            {
                'url': 'table/%{tableName}',
                'operations': [
                    {
                        'PUT': {
                            'bodyFormat': {
                                "columnName": {
                                    '$data': 'columnValue',
                                    'optional': {
                                        '$s3': 'bool',
                                        '$base64': 'bool',
                                    }
                                }
                            }
                        }
                    }
                ],
            }
        ]
    }
}
MIGRATIONS_DIRECTORY = os.path.realpath(DIR + '/../../migrations')

AWS_KMS_S3_BUCKET_NAME    = env('AWS_KMS_S3_BUCKET_NAME')
AWS_KMS_KEY_ARN_ID        = env('AWS_KMS_KEY_ARN_ID')
AWS_ACCESS_KEY_ID         = env('AWS_ACCESS_KEY_ID'        , default='local_dynamo')
AWS_SECRET_ACCESS_KEY     = env('AWS_SECRET_ACCESS_KEY'    , default='local_secret')
IS_REMOTE                 = env('IS_REMOTE'                , default=False)
IS_TEST                   = env('IS_TEST'                  , default=False)
TEST_REMOTE               = env('TEST_REMOTE'              , default=False)
ENV_NAME                  = env('ENV_NAME'                 , default=('test' if IS_TEST else 'dev'))
CRYPTO_KEY                = env('CRYPTO_KEY'               , default=None)
AUTH_WEB_HOOK             = env('AUTH_WEB_HOOK'            , default=None)
BASIC_AUTH_USERNAME       = env('BASIC_AUTH_USERNAME'      , default=None)
BASIC_AUTH_PASSWORD       = env('BASIC_AUTH_PASSWORD'      , default=None)
HIDE_ERRORS               = env('HIDE_ERRORS'              , default=False)
SUPER_TENANT_ID           = env('SUPER_TENANT_ID'          , default='clari_dynamo')
ALLOW_RETRYING_MIGRATIONS = env('ALLOW_RETRYING_MIGRATIONS', default=True)

if BASIC_AUTH_USERNAME:
    BASIC_AUTH_DICT = {BASIC_AUTH_USERNAME: BASIC_AUTH_PASSWORD}
else:
    BASIC_AUTH_DICT = None

CRYPTO = Fernet(CRYPTO_KEY.encode('ascii'))
RETRY_ON_THROUGHPUT_EXCEEDED = True

if IS_REMOTE:
    DYNAMO_IS_SECURE = True
else:
    DYNAMO_IS_SECURE = False

# TODO: Remove after https://github.com/boto/boto/issues/2921
BOTO_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)))) + '/boto'
