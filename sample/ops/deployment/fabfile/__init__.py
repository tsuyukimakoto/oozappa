# -*- coding:utf8 -*-
from fabric.api import task, local, run, sudo, env

from oozappa.config import get_config, procure_common_functions
_settings = get_config()
procure_common_functions()

# your own task below

@task
def set_env_app_type_a():
    u'''eg. search app server type a instance via api or hard-coding and set fabric env.'''
    print('set_env_app_type_a')

@task
def set_env_app_type_b():
    u'''eg. search app server type b instance via api or hard-coding and set fabric env.'''
    print('set_env_app_type_b')

@task
def deploy_application_type_a():
    u'''grab application from somewhere and deploy app_type_a'''
    print('deploy_application_type_a')

@task
def deploy_application_type_b():
    u'''grab application from somewhere and deploy app_type_b'''
    print('deploy_application_type_b')

@task
def create_image_from_app_type_a():
    u'''eg. search app_type_a instance and create image.'''
    print('create_image_from_app_type_a')
