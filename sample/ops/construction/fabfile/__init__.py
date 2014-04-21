# -*- coding:utf8 -*-
u'''This environment is responsible for construction basics.

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'''
from fabric.api import task, local, run, sudo, env, hosts

from oozappa.config import get_config, procure_common_functions
_settings = get_config()
procure_common_functions()

# your own task below

@task
@hosts(['localhost'])
def create_initial_instance():
  u'''eg. launch instance and make initial setting.'''
  print('create_initial_instance')

@task
def set_env_initial_instance():
  u'''eg. search initial instance via api or hard-coding and set fabric env.'''
  env.hosts = ('192.168.0.2')
  env.user = 'your user'
  env.key_filename = 'your key here' # or password

@task
def install_base_packages():
  u'''eg. install packages using all hosts. like postfix build-essential ...'''
  print('install_base_packages')

@task
def make_some_language_or_middleware():
  u'''eg. install language or middleware using all hosts.'''
  print('make_some_language_or_middleware')

@task
def create_image_from_initial_instance():
  u'''eg. search initial instance and create image.'''
  print('create_image_from_initial_instance')
