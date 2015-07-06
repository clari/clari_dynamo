# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)

import os
import unittest

from clari_dynamo.test.db import TestDB
from clari_dynamo.migrate.run_migrations import *

DIR = os.path.dirname(os.path.abspath(__file__))


class MigrationsTest(unittest.TestCase):
    def migrate_test(self, folder):
        names_ran, was_success = \
            migrate(self.db, migrations_dir=os.path.join(DIR, folder))
        return names_ran, was_success

    def test_migrations(self):
        names_ran, was_success = self.migrate_test('migrations')
        self.assertGreater(len(names_ran), 0)
        self.assertTrue(was_success)
        names_ran, was_success = self.migrate_test('migrations')

        # Test idempotency
        self.assertEqual(len(names_ran), 0)
        self.assertTrue(was_success)

    def test_migration_lock(self):
        db = self.db
        ensure_schema_migrations_tables(db)
        self.assertTrue(obtain_migration_lock(db))
        self.assertFalse(obtain_migration_lock(db), "Parallel migrations not allowed")
        release_migration_lock(db)
        self.assertTrue(obtain_migration_lock(db), "Lock should have been released")
        release_migration_lock(db)

    def test_failed_migration(self):
        names_ran, was_success = self.migrate_test('failed_migrations')
        self.assertEqual(len(names_ran), 0)
        self.assertFalse(was_success)

    @classmethod
    def setUpClass(cls):
        cls.db = TestDB.get()

    @classmethod
    def tearDownClass(cls):
        TestDB.release()