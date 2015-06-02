# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import json

from cryptography.fernet import Fernet
from clari_dynamo.conf.cd_logger import logging
from clari_dynamo.utils import env

if os.path.isfile(os.path.dirname(os.path.abspath(__file__)) + '/secrets.py'):
    import clari_dynamo.conf.secrets
else:
    print('No secrets.py found, request access, set the variables documented in '
          'secrets.example.py')

#######################################################################
# Please don't put sensitive information here. Use secrets.py instead #
#######################################################################

# Used by boto to set signing method for AWS
os.environ['S3_USE_SIGV4'] = 'True'

HOME_TEXT = {
    'clari_dynamo': {
        'routes': [
            {
                'url': 'table/%{tableName}',
                'operations': [
                    {'PUT': {'bodyFormat': {"column_name": 'columnValue'}}}
                ],
            }
        ]
    }
}

AWS_KMS_S3_BUCKET_NAME = env('CLARI_DYNAMO_AWS_KMS_S3_BUCKET_NAME')
AWS_KMS_KEY_ARN_ID     = env('CLARI_DYNAMO_AWS_KMS_KEY_ARN_ID')
AWS_ACCESS_KEY_ID      = env('CLARI_DYNAMO_AWS_ACCESS_KEY_ID'     , default='local_dynamo')
AWS_SECRET_ACCESS_KEY  = env('CLARI_DYNAMO_AWS_SECRET_ACCESS_KEY' , default='local_secret')
IS_REMOTE              = env('CLARI_DYNAMO_IS_REMOTE'             , default=False)
ENV_NAME               = env('CLARI_DYNAMO_ENVIRONMENT'           , default='dev')
CRYPTO_KEY             = env('CLARI_DYNAMO_CRYPTO_KEY'            , default=None)
AUTH_WEB_HOOK          = env('CLARI_DYNAMO_AUTH_WEB_HOOK'         , default=None)
BASIC_AUTH_USERNAME    = env('CLARI_DYNAMO_BASIC_AUTH_USERNAME'   , default=None)
BASIC_AUTH_PASSWORD    = env('CLARI_DYNAMO_BASIC_AUTH_PASSWORD'   , default=None)

if BASIC_AUTH_USERNAME:
    BASIC_AUTH_DICT = {BASIC_AUTH_USERNAME: BASIC_AUTH_PASSWORD}
else:
    BASIC_AUTH_DICT = None

CRYPTO = Fernet(CRYPTO_KEY)
RETRY_ON_THROUGHPUT_EXCEEDED = False
DYNAMO_IS_SECURE = True

# TODO: Remove after https://github.com/boto/boto/issues/2921
BOTO_PATH = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)))) + '/boto'