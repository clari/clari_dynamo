# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import imp
import os
import sys
from os import listdir
from clari_dynamo.migrate.common_imports import *
from clari_dynamo.clari_dynamo import ClariDynamo
from clari_dynamo.conf.cd_logger import logging

TABLE_NAME = '_schema_migrations'

# TODO: Move meta table stuff to its own class
META_TABLE_NAME = '_meta'
META_KEY_NAME   = 'meta_name'
META_VALUE_NAME = 'meta_value'

HASH_KEY                  = 'migration'
MIGRATION_META_STATUS_KEY = 'migrations_running'

NO_STATUS  = 'no'
YES_STATUS = 'yes'


def get_finished_migrations(db):
    result = db.query(TABLE_NAME,
                    purpose='get finished migrations',
                    tenant_id=SUPER_TENANT_ID,
                    migration_key__eq=HASH_KEY,
                    consistent=True)
    ret = list(migration['migration_name'] for migration in result)
    return ret


def is_migration_file(file_name):
    return file_name.startswith('migration_') and \
           file_name.find('.pyc') == -1


def get_migrations_to_run(db, migrations_dir):
    finished = get_finished_migrations(db)
    for file_name in sorted(listdir(migrations_dir)):
        migration_name = os.path.splitext(file_name)[0]
        if is_migration_file(file_name) and migration_name not in finished:
            migration = load_from_file(os.path.join(migrations_dir, file_name))
            yield migration_name, migration


def mark_migration_done(db, migration_name):
    # We want to do one bulk query for all migrations, so giving them
    # the same hash key. Should be only hundreds to thousands of these.
    db.put_item(TABLE_NAME, item={
        'migration_key' : HASH_KEY,
        'migration_name': migration_name
    }, tenant_id=SUPER_TENANT_ID, purpose='ran migration')


def handle_failed_migration(db, exc_info):
    logging.error('Aborting migrations - '
                  ' %s failed with: %s %s %s',
                  exc_info[0], exc_info[1], exc_info[2])
    if ALLOW_RETRYING_MIGRATIONS:
        release_migration_lock(db)
        logging.warn('Migrations will retry next server start '
                     '"%s" to "%s" in the "%s" table' % (
                         MIGRATION_META_STATUS_KEY, NO_STATUS, META_TABLE_NAME))
    else:
        logging.warn('You will need to set '
                     '"%s" to "%s" in the "%s" table' % (
                         MIGRATION_META_STATUS_KEY, NO_STATUS, META_TABLE_NAME))


def migrate(db, migrations_dir):
    """
    Returns: accumulated_migrations, all_migrations_ran_successfully

    accumulated_migrations is a list of migration names that ran successfully.
    all_migrations_ran_successfully is a bool indicating overall success
    """
    ensure_schema_migrations_tables(db)
    accumulated_migrations = []
    if obtain_migration_lock(db):
        # So two servers don't run migration at same time
        migrations = get_migrations_to_run(db, migrations_dir)
        for i, (migration_name, migration) in enumerate(migrations):
            logging.info('Running ' + migration_name )
            try:
                migration.run(db)
            except Exception as e:
                exc_info = sys.exc_info()
                handle_failed_migration(db, exc_info)
                return accumulated_migrations, False
            logging.info('Finished migration ' + migration_name )
            mark_migration_done(db, migration_name)
            accumulated_migrations += migration_name
        release_migration_lock(db)
        return accumulated_migrations, True


def obtain_migration_lock(db):
    # lock = db.get_item(table_name=META_TABLE_NAME, tenant_id=SUPER_TENANT_ID,
    #                    purpose='check status', name=MIGRATION_META_STATUS_KEY)
    try:
        db.put_item(table_name=META_TABLE_NAME,
                    item={
                        META_KEY_NAME:   MIGRATION_META_STATUS_KEY,
                        META_VALUE_NAME: YES_STATUS
                    },
                    tenant_id=SUPER_TENANT_ID,
                    purpose='obtain migration lock',
                    overwrite=True,
                    condition=META_VALUE_NAME + " = :status",
                    vars={':status': NO_STATUS})
    except ClariDynamo.ClariDynamoConditionCheckFailedException as e:
        logging.info('Could not get migration lock, other process running.')
        return False

    return True


def release_migration_lock(db):
    result = db.put_item(table_name=META_TABLE_NAME, item={
        META_KEY_NAME:   MIGRATION_META_STATUS_KEY,
        META_VALUE_NAME: NO_STATUS
    }, tenant_id=SUPER_TENANT_ID, purpose='release migration lock',
                         overwrite=True)
    return result


def ensure_schema_migrations_tables(db):
    if not db.has_table(TABLE_NAME):
        db.create_table(TABLE_NAME,
                        schema=[HashKey ('migration_key'),
                                RangeKey('migration_name')],
                        throughput={'read':  10, 'write':  5},)
    if not db.has_table(META_TABLE_NAME):
        db.create_table(META_TABLE_NAME,
                        schema=[HashKey (META_KEY_NAME)],
                        throughput={'read':  10, 'write':  5})

        db.put_item(table_name=META_TABLE_NAME, item={
            META_KEY_NAME:   MIGRATION_META_STATUS_KEY,
            META_VALUE_NAME: NO_STATUS
        }, tenant_id=SUPER_TENANT_ID, purpose='init')


def load_from_file(file_path):
    mod_name, file_ext = os.path.splitext(os.path.split(file_path)[-1])
    assert file_ext.lower() == '.py'
    py_mod = imp.load_source(mod_name, file_path)
    return py_mod
