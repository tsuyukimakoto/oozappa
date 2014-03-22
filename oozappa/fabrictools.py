# -*- coding:utf8 -*-
import os
from fabric.main import load_fabfile

class FabricTask(object):
    def __init__(self, task_dict):
        self._task_dict = task_dict
    def name(self):
        return self._task_dict.name
    @property
    def description(self):
        return self._task_dict.__doc__ or u''
    def __str__(self):
        return self.name()
    def __repr__(self):
        return self.__str__()

class FabricHelper(object):
    def __init__(self, path):
        _path = path
        if not path.endswith('fabric'):
            _path = os.path.join(path, 'fabfile')
        _dict = load_fabfile(_path)[1]
        self.task_dict = dict((x.name, FabricTask(x)) for x in _dict.values())
        self.directory = os.path.split(path)[0]

    def task_list(self):
        return self.task_dict
    def task(self, name):
        return self.task_dict[name]

def print_task_list(path):
    tasks = load_fabfile(path)
    task_dict = tasks[1]
    for task in task_dict.values():
        print(u'{0:10}: {1}'.format(task.name, task.__doc__))

