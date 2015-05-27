# -*- coding: utf-8 -*-

import os

from clari_dynamo.utils import env

if os.path.isfile(os.path.dirname(os.path.abspath(__file__)) + '/secrets.py'):
    import conf.secrets
else:
    print('No secrets.py found, request access or fill out secrets.example.py')

#######################################################################
# Please don't put sensitive information here. Use secrets.py instead #
#######################################################################

# For direct access by mobile / web clients
# AUTH_WEB_HOOK = os.environ('AUTH_WEB_HOOK')

# Used by boto to set signing method for AWS
os.environ['S3_USE_SIGV4'] = 'True'

HOME_TEXT = """
clari_dynamo - send PUT to table/tableName with {"name": value, "name2": value2}
"""

AWS_KMS_S3_BUCKET_NAME = env('CLARI_DYNAMO_AWS_KMS_S3_BUCKET_NAME')
AWS_KMS_KEY_ARN_ID     = env('CLARI_DYNAMO_AWS_KMS_KEY_ARN_ID')
AWS_ACCESS_KEY_ID      = env('CLARI_DYNAMO_AWS_ACCESS_KEY_ID'     , default='local_dynamo')
AWS_SECRET_ACCESS_KEY  = env('CLARI_DYNAMO_AWS_SECRET_ACCESS_KEY' , default='local_secret')
IS_REMOTE              = env('CLARI_DYNAMO_IS_REMOTE'             , default=False)
ENV_NAME               = env('CLARI_DYNAMO_ENVIRONMENT'           , default='dev')

RETRY_ON_THROUGHPUT_EXCEEDED = False
DYNAMO_IS_SECURE = True