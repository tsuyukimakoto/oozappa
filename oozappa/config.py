# -*- coding:utf8 -*-
import sys
import os
from copy import deepcopy
import collections

import logging
logger = logging.getLogger('oozappa')

def _update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = _update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

class OozappaSetting(dict):
  '''dict like object. accessible with dot syntax.
>>> settings = OozappaSetting(
...   spam = '123',
...   egg = 123
... )
...
>>> assert(settings.spam == '123)
>>> assert(settings.egg == 123)
>>> settings.ham = 123.0
>>> assert(settings.ham == 123.0)
>>> s2 = OozappaSetting(dict())
  '''
  def __init__(self, *args, **kwargs) :
    for d in args:
      print(d)
      if type(d) is OozappaSetting or type(d) is dict:
        self.update(d)
    for key, value in kwargs.items():
      self[key] = value

  def __setattr__(self, key, value):
    if value and type(value) is OozappaSetting or type(value) is dict:
      self[key] = OozappaSetting(value)
    else:
      self[key] = value

  def __getattr__(self, key):
    try: return self[key]
    except: object.__getattribute__(self, key)

  def update(self, opt):
    self = _update(self, opt)

def common_base_path():
  return os.path.abspath(os.path.join(os.getcwd(), '..'))

def get_config():
  path_added = False
  _common_base_path = common_base_path()
  logger.debug(_common_base_path)
  if not _common_base_path in sys.path:
    sys.path.insert(0, _common_base_path)
    path_added = True
  from common.vars import settings as common_settings
  _settings = deepcopy(common_settings)
  if path_added:
    sys.path.remove(_common_base_path)
  from vars import settings
  _settings.update(settings)
  return _settings
