# -*- coding:utf8 -*-
from fabric.api import task, run, local, cd, hosts, env

import time

from oozappa.config import get_config, procure_common_functions
_settings = get_config()

procure_common_functions()
import sys

from common_multiple_fabric_environment import _deploy_template_sample_a

test_host = ('192.168.0.110',) #FIXME

@task
def ls():
    u'''run ls command on local machine.'''
    local('ls -la')

@task
def ps():
    u'''run ls command on local machine.'''
    local('ps ax')

@task
def sys_path():
    import sys
    print(sys.path)

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

@task
@hosts(test_host)
def deploy_template_sample_a():
    _deploy_template_sample_a(_settings.sample_template_vars.sample_a)

@task
def launch_instance_from_app_a_image():
    u'''eg. launch instance from app a image.'''
    print('launch_instance_from_app_a_image')

@task
def set_env_latest_app_a():
    u'''eg. search latest app type a instance and set fabric env.'''
    print('set_env_latest_app_a')

@task
def set_env_latest_app_b():
    u'''eg. search latest app type b instance and set fabric env.'''
    print('set_env_latest_app_b')

@task
def launch_instance_from_app_b_image():
    u'''eg. launch instance from app b image.'''
    print('launch_instance_from_app_b_image')

@task
def production_specific_setting():
    u'''eg. production specific setting'''
    print('production_specific_setting')
