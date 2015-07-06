# -*- coding: utf-8 -*-
import boto
import boto.ec2
import boto.dynamodb2
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER, BOOLEAN
from clari_dynamo.conf.constants import *
