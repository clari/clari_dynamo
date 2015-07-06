# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)
import unittest

from clari_dynamo.test.test_clari_dynamo import ClariDynamoTest
from clari_dynamo.test.test_migrations import MigrationsTest

for test_module in [ClariDynamoTest, MigrationsTest]:
    unittest.TextTestRunner().run(unittest.TestSuite(
        unittest.TestLoader().loadTestsFromTestCase(test_module)))