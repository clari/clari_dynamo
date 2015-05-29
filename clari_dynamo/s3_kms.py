import utils
from conf.constants import *

from boto.s3.connection import S3Connection
from boto.s3.key import Key

CONNECTION = S3Connection(host='s3.amazonaws.com', debug=2, is_secure=True)
BUCKET = CONNECTION.get_bucket(AWS_KMS_S3_BUCKET_NAME)


def put(table_name, item_name, data):
    file_name = '{0:s}.{1:s}.{2:s}'.format(table_name, item_name,
                                           utils.get_a_uuid())
    key = Key(BUCKET)
    key.key = file_name
    key.set_contents_from_string(data, headers=get_kms_headers())

    return key


def delete(key_string):
    key = Key(BUCKET)
    key.key = key_string
    BUCKET.delete_key(key)


def get(key_string):
    key = Key(BUCKET)
    key.key = key_string
    ret = key.get_contents_as_string()
    return ret


def get_kms_headers():
    return {
        'x-amz-server-side-encryption': 'aws:kms',
        'x-amz-server-side-encryption-aws-kms-key-id':
            os.environ['CLARI_DYNAMO_AWS_KMS_KEY_ARN_ID']}