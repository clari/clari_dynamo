# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)
import os

import re
import arrow
import shutil

DIR = os.path.dirname(os.path.abspath(__file__))


def get_migration():
    migration_name = input('Migration name? - i.e. '
                           '[create_my_table or add_my_column_to_my_table] ')

    if len(migration_name) == 0:
        print('Migration name must not be empty')
        return get_migration()

    if not re.match("^[\w\d_-]*$", migration_name):
        print('Migration must contain only letters, numbers, dashes, and '
              'underscores')
        return get_migration()
    else:
        file_name = '%s_%s.py' % (arrow.now().format('YYYY_MM_DD_HH_mm_ss'),
                                  migration_name)
        full_src = os.path.join(DIR, 'clari_dynamo', 'migrate',
                                'migration_template.py')
        full_dst = os.path.join(DIR, 'migrations',    file_name)
        shutil.copyfile(full_src, full_dst)
        print('Finished creating migration file:')
        print('   migrations/' + file_name)

get_migration()
