# -*- coding:utf8 -*-
import sys
import os
from copy import deepcopy
import collections

import logging
logger = logging.getLogger('oozappa')


def _update(org, opt):
    for k, v in opt.iteritems():
        if isinstance(v, collections.Mapping):
            r = _update(org.get(k, OozappaSetting()), v)
            org[k] = r
        else:
            org[k] = opt[k]
    return org


class OozappaSetting(dict):
    '''dict like object. accessible with dot syntax.
  >>> settings = OozappaSetting(
  ...   spam = '123',
  ...   egg = 123
  ... )
  >>> assert(settings.spam == '123')
  >>> assert(settings.egg == 123)
  >>> settings.ham = 123.0
  >>> assert(settings.ham == 123.0)
  >>> s2 = OozappaSetting(dict(spam=456))
  >>> settings.update(s2)
  >>> assert(settings.spam == 456)
  >>> assert(settings.ham == 123.0)
    '''
    def __init__(self, *args, **kwargs):
        for d in args:
            if isinstance(d, collections.Mapping):
                self.update(d)
        for key, value in kwargs.items():
            self[key] = value

    def __setattr__(self, key, value):
        if isinstance(value, collections.Mapping):
            self[key] = OozappaSetting(value)
        else:
            self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except:
            object.__getattribute__(self, key)

    def update(self, opt):
        self = _update(self, opt)


def common_base_path():
    if os.path.exists(
        os.path.abspath(
            os.path.join(os.getcwd(), 'fabfile'))) or os.path.exists(
        os.path.abspath(
            os.path.join(os.getcwd(), 'fabfile.py'))):
        return os.path.abspath(os.path.join(os.getcwd(), '..'))
    else:
        return os.getcwd()


def get_config():
    path_added = False
    _common_base_path = common_base_path()
    logger.debug('COMMON_BASE_PATH: {0}'.format(_common_base_path))
    try:
        if not _common_base_path in sys.path:
            sys.path.insert(0, _common_base_path)
            path_added = True
        from common.vars import settings as common_settings
        _settings = deepcopy(common_settings)
        if path_added:
            sys.path.remove(_common_base_path)
    except ImportError:
        _settings = OozappaSetting()
    try:
        from vars import settings
        _settings.update(settings)
    except ImportError:
        pass
    return _settings


def procure_common_functions():
    u'''insert common/functions to sys.path'''
    _common_function_path = os.path.join(common_base_path(), 'common', 'functions')
    if not _common_function_path in sys.path:
        if not os.path.exists(_common_function_path):
            logging.warn('common_function directory not exists? {0}'.format(_common_function_path))
        sys.path.insert(0, _common_function_path)
        logger.info('common_function directory added to sys.path')
