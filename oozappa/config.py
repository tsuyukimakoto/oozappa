# -*- coding:utf8 -*-
import sys
import os
from copy import deepcopy

import logging
logger = logging.getLogger('oozappa')

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

def get_config(call_path):
  path_added = False
  common_path = os.path.abspath(os.path.join(call_path, '..', '..', '..'))
  logger.debug(common_path)
  if not common_path in sys.path:
    sys.path.insert(0, common_path)
    path_added = True
  from common.vars import settings as common_settings
  _settings = deepcopy(common_settings)
  if path_added:
    sys.path.remove(common_path)
  from vars import settings
  _settings.update(settings)
  return _settings
