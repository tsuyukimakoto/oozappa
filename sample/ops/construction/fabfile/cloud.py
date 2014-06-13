# -*- coding:utf8 -*-

from fabric.api import task, local, run, sudo, env, hosts

@task
def launch_instance():
    u'''eg. launch instance and make initial setting.'''
    print('initial_instance')
