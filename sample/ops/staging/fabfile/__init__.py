# -*- coding:utf8 -*-
from fabric.api import task, run, local, cd

import time

from oozappa.config import get_config
_settings = get_config(__file__)

@task
def ls():
    u'''run ls command on local machine.'''
    local('ls -la')

@task
def ps():
    u'''run ls command on local machine.'''
    local('ps ax')

@task
def sleep():
    u'''sleep 5 second.'''
    print('stop 5 sec...')
    time.sleep(5)
    print('5 sec... passed')

@task
def printsetting():
    u'''print setting from staging.vars and common.vars'''
    print(_settings)
