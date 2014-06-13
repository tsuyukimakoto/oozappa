# -*- coding:utf8 -*-
import os
import sys
from fabric.api import env
from fabric.main import load_fabfile
from fabric.contrib.files import upload_template as fabric_upload_template

import logging
logger = logging.getLogger('oozappa')


class FabricTask(object):
    def __init__(self, task_dict, m=None):
        self._task_dict = task_dict
        self._m = m

    @property
    def name(self):
        if self._m:
            return '{0}.{1}'.format(self._m, self._task_dict.name)
        return self._task_dict.name

    @property
    def description(self):
        return self._task_dict.__doc__ or u''

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class FabricHelper(object):
    def __init__(self, path):
        _path = path
        if not path.endswith('fabric'):
            _path = os.path.join(path, 'fabfile')
        if 'fabfile' in sys.modules.keys():
            del sys.modules['fabfile']
        self.doc, _dict = load_fabfile(_path)[:2]
        self.task_dict = dict((x.name, FabricTask(x)) for x in _dict.values() if hasattr(x, 'name'))
        _modules = [k for k, m in _dict.items() if not hasattr(m, 'name')]
        for _m in _modules:
            self.task_dict.update(dict(('{0}.{1}'.format(_m, x.name), FabricTask(x, m=_m)) for x in _dict[_m].values() if hasattr(x, 'name')))
        self.directory = os.path.split(path)[0]

    def task_list(self):
        return self.task_dict

    def task(self, name):
        return self.task_dict[name]

    def get_tasks(self, task_list):
        tasks = self.task_list()
        result = dict(found={}, not_found=[])
        for t in task_list:
            if t in tasks:
                result.get('found')[tasks.get(t).name] = tasks.get(t)
            else:
                result.get('not_found').append(t)
        return result


def print_task_list(path):
    tasks = load_fabfile(path)
    task_dict = tasks[1]
    for task in task_dict.values():
        print(u'{0:10}: {1}'.format(task.name, task.__doc__))


def get_tasks(path, task_list):
    tasks = FabricHelper(path).task_list()
    result = dict(found={}, not_found=[])
    for t in task_list:
        if t in tasks:
            result.get('found')[tasks.get(t).name] = tasks.get(t)
        else:
            result.get('not_found').append(t)
    return result


TEMPLATES_DIRNAME = 'templates'


def upload_template(filename, destination, context=None,
    template_dir=None, use_sudo=False, backup=False, mirror_local_mode=False,
        mode=None):
    '''Search filename in ENVIRONMENT_DIR/templates at first and then common/templates if template_dir is not supplied.
      Call fabric.contrib.file.upload_template passing directory that is found filename, or None.
      if template_dir passed, this function just call fabric.contrib.file.upload_template as usual.

      *) backup default option is False

      *) use_jinja option is always True and you can't pass use_jinja option to this function.
    '''
    _template_dir = template_dir
    if not _template_dir:
        call_path = os.getcwd()
        common_path = os.path.abspath(os.path.join(call_path, '..', 'common'))
        if os.path.exists(os.path.join(call_path, TEMPLATES_DIRNAME, filename)):
            logger.debug('found called path')
            _template_dir = os.path.join(call_path, TEMPLATES_DIRNAME)
        elif os.path.exists(os.path.join(common_path, TEMPLATES_DIRNAME, filename)):
            logger.debug('found common path')
            _template_dir = os.path.join(common_path, TEMPLATES_DIRNAME)
        else:
            logger.warn('NOT FOUND {0}'.format(os.path.join(call_path, TEMPLATES_DIRNAME, filename)))
            logger.warn('NOT FOUND {0}'.format(os.path.join(common_path, TEMPLATES_DIRNAME, filename)))
    return fabric_upload_template(filename, destination, context=context, use_jinja=True,
        template_dir=_template_dir, use_sudo=use_sudo, backup=backup, mirror_local_mode=mirror_local_mode,
        mode=mode)


def only_once(f):
    '''Task decorator. Run task only once while executing multiple task'''
    def _f(*args, **kwargs):
        flag_format = 'only_once_function_{0}'
        try:
            if not env.get(flag_format.format(f.__name__)):
                return f(*args, **kwargs)
            logger.info('[ONLY ONCE] pass function [{0}]'.format(f.__name__))
        finally:
            env[flag_format.format(f.__name__)] = True
    return _f
