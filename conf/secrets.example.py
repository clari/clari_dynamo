# -*- coding: utf-8 -*-
import os

# Template file for secrets.py, copy to secrets.py in the same directory
# and fill in the values for local dev. Should be in OS environment for
# deployment.

os.environ['CLARI_DYNAMO_AWS_KMS_S3_BUCKET_NAME'] = 'x'
os.environ['CLARI_DYNAMO_AWS_KMS_KEY_ARN_ID']     = 'x'