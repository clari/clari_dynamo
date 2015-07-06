# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import (bytes, str, open, super, range, zip, round, input, int, pow, object)
from clari_dynamo.conf.constants import *
from clari_dynamo.utils import quick_random_str

from functools import wraps
import logging
from time import time


def timing_setup(func, args):
    start = time()
    op_id = quick_random_str(6)
    main_args = dict(zip(func.func_code.co_varnames, args))
    if 'self' in main_args:
        del main_args['self']
    return main_args, op_id, start


def timing_finish(func, args, kwargs, start):
    result = func(*args, **kwargs)
    end = time()
    elapsed = end - start
    return elapsed, result


def table_op(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        main_args, op_id, start = timing_setup(func, args)
        table_name = main_args.get('table_name', kwargs.get('table_name', None))
        table_str = ':%s' % table_name if table_name else ''
        logging.info('%s(%s)%s started opid:%s' %
            (func.func_name, ', '.join(kwargs.keys()), table_str, op_id))
        elapsed, result = timing_finish(func, args, kwargs, start)
        logging.info('%s(%s)%s finished in %0.3fms opid:%s' %
            (func.func_name, ', '.join(kwargs.keys()), table_str,
             elapsed * 1000.0, op_id))
        return result
    return wrapper


def item_op(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        main_args, op_id, start = timing_setup(func, args)
        purpose = main_args.get('purpose', kwargs.get('purpose', None))
        table_name = main_args.get('table_name', kwargs.get('table_name', None))
        tenant_id = main_args.get('tenant_id', kwargs.get('tenant_id', None))
        assert purpose
        assert tenant_id
        logging.info('%s(%s):%s started purpose:"%s" opid:%s' %
            (func.func_name, ', '.join(kwargs.keys()), table_name, purpose, op_id))
        elapsed, result = timing_finish(func, args, kwargs, start)
        logging.info('%s(%s):%s finished in %0.3fms purpose:"%s" opid:%s' %
            (func.func_name, ', '.join(kwargs.keys()), table_name, elapsed * 1000.0, purpose, op_id))
        return result
    return wrapper