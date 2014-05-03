# -*- coding:utf8 -*-
import sys
import os
import shutil
import logging

logger = logging.getLogger('oozappa')

def main():
  environ_names = sys.argv[1:]
  if len(environ_names) == 0:
    while 1:
      x = raw_input('environ_name : ').strip()
      if len(x) > 1 and 'common' != x.lower():
        environ_names.append(x)
        break
  for environ_name in environ_names:
    if os.path.exists(environ_name):
      logger.warn('{0} is exists and do nothing.'.format(environ_name))
      continue
    shutil.copytree(os.path.join(os.path.dirname(__file__), '_structure', '_environment'), environ_name)
    logger.info('create environment : {0}'.format(environ_name))

if __name__ == '__main__':
  main()