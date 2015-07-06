# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

from clari_dynamo.migrate.common_imports import *


def run(db):
    db.create_table('test_run_migration_b',
        schema=[
            HashKey  ( 'type'                       ),
            RangeKey ( 'rangeNum', data_type=NUMBER ),
        ],
        throughput={
            'read':   1,
            'write':  1,
        }, global_indexes=[
            GlobalAllIndex('globalIndex', parts=[
                HashKey  ('rangeNum', data_type=NUMBER),
                RangeKey ('type'),
            ], throughput={
                'read':  1,
                'write': 1,
            })
        ]
    )