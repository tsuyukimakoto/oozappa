# -*- coding:utf8 -*-
import os
import sys
import logging
import shutil
from collections import OrderedDict
from uuid import uuid4
import argparse

logger = logging.getLogger(__name__)

from oozappa.config import get_config
_settings = get_config()


from oozappa import __version__, LogfileCommunicator, run_jobset

DEFAULT_OOZAPPA_PATH = '/tmp/oozappa'
DEFAULT_OOZAPPA_DATAPATH = '{DEFAULT_OOZAPPA_PATH}/data.sqlite'.format(
    DEFAULT_OOZAPPA_PATH=DEFAULT_OOZAPPA_PATH)


def _ensure_directory(pth):
    if not os.path.exists(pth):
        if raw_input('Create directory or exit? "{0}" [y/N] : '.format(pth)).lower() == 'y':
            os.makedirs(pth)
        else:
            print('aborted')
            sys.exit(-1)
    if not os.path.isdir(pth):
        print('{0} is not directory.'.format(pth))
        print('aborted')
        sys.exit(-1)
    if not os.access(pth, os.W_OK | os.X_OK):
        print('directory "{0}" is not writable. check permission.'.format(pth))
        sys.exit(1)


def _create_database_path(sqlite_stored_path):
    if sqlite_stored_path == '':
        sqlite_stored_path = DEFAULT_OOZAPPA_DATAPATH
    else:
        if os.path.dirname(sqlite_stored_path) == '':
            sqlite_stored_path = os.path.join(os.path.abspath(os.path.curdir), sqlite_stored_path)
        sqlite_stored_path = os.path.abspath(sqlite_stored_path)
        _ensure_directory(sqlite_stored_path)
        sqlite_stored_path = 'sqlite:///{0}'.format(sqlite_stored_path)
    return sqlite_stored_path


def _create_logfile_stored_path(log_file_path):
    if log_file_path == '':
        log_file_path = DEFAULT_OOZAPPA_PATH
    _ensure_directory(log_file_path)
    return log_file_path


def init(args):
    try:
        _settings.FLASK_SECRET_KEY
    except AttributeError:
        should_create = raw_input('Create common environment here? [y/N] : ').lower()
        if should_create == 'y':
            sqlite_stored_path = _create_database_path(raw_input(
                'Sqlite database stored path. [{DEFAULT_OOZAPPA_DATAPATH}] : '.format(
                    DEFAULT_OOZAPPA_DATAPATH=DEFAULT_OOZAPPA_DATAPATH))
            )
            log_file_path = _create_logfile_stored_path(
                raw_input('Log files stored path. [{DEFAULT_OOZAPPA_PATH}] : '.format(
                    DEFAULT_OOZAPPA_PATH=DEFAULT_OOZAPPA_PATH))
            )
            shutil.copytree(os.path.join(os.path.dirname(__file__), '_structure', 'common'), 'common')
            with open('common/vars.py') as f:
                data = f.read()
            with open('common/vars.py', 'w') as f:
                f.write(data.format(FLASK_SECRET_KEY=uuid4().hex,
                  OOZAPPA_DB=sqlite_stored_path,
                  OOZAPPA_LOG_BASEDIR=log_file_path))
            print('created common directory. db/log file path and flask secret key are in common/vars.py.')
            sys.exit(0)
        print("couldn't find FLASK_SECRET_KEY in your ENVIRONMENT/vars.py")
        sys.exit(1)
    else:
        print('Oozappa structure exits already.')


def create_environment(args):
    environ_names = args.names
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


def print_version(args):
    print('Oozappa/{0}'.format(__version__))


def list_jobsets(*args):
    from oozappa.records import Jobset, get_db_session
    session = get_db_session()
    jobset_list = session.query(Jobset).all()
    print('-' * 40)
    for jobset in jobset_list:
        print(u'|id:{0:03d}|CLI_ONLY:{1}|title:{2}|'.format(jobset.id, jobset.cli_only, jobset.title))
    print('-' * 40)

def change_cli_flag():
    from oozappa.records import Jobset, get_db_session
    session = get_db_session()
    list_jobsets()
    x = raw_input(u'Which Jobset id?')
    jobset = session.query(Jobset).get(x)
    if jobset:
        jobset.cli_only = not jobset.cli_only
        session.commit()
    list_jobsets()


class CommandDict(OrderedDict):
    pass


class Return(object):
    pass


class Command(object):

    def __init__(self, func, description):
        self.func = func
        self.description = description

_command = CommandDict(
    l=Command(list_jobsets, 'List Jobsets'),
    c=Command(change_cli_flag, "Modify Jobset's CLI Flag."),
    n=Command(CommandDict(
            x=Command(list_jobsets, 'list Jobsets'),
        ), 'next',
    ),
    q=Command(Return, 'quit'),
)


def _switch_command(chr, __command):
    if chr in __command:
        return __command.get(chr)
    return None


def _show_command(__command):
    print(' commands')
    for k, v in __command.items():
        print(' ' * 3 + ' -> {0}: {1}'.format(k, v.description))


def manage_oozappa(args):
    _current = _command
    print('<{0}:{1}>'.format('manage',
          os.path.dirname(os.path.abspath(__file__))))
    _show_command(_current)
    while 1:
        x = _switch_command(raw_input(), _current)
        if not x:
            continue
        if x.func == Return:
            break
        if type(x.func) == CommandDict:
            _show_command(x.func)
            _current = x.func
            continue
        x.func()
        _show_command(_current)


def run_jobset_from_cli(args):
    jobset_id = args.jobset
    with LogfileCommunicator(_settings.OOZAPPA_LOG_BASEDIR) as communicator:
        communicator.write('[[zappa]]\n')
        run_jobset(jobset_id, communicator, cli=True)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')
    init_parser = subparsers.add_parser('init', help='Initialize. Create oozappa base structure.')
    init_parser.set_defaults(func=init)
    create_environemnt_parser = subparsers.add_parser('create_environment', help='Create oozappa environment structure.')
    create_environemnt_parser.add_argument('--names', nargs='+', default=[])
    create_environemnt_parser.set_defaults(func=create_environment)
    version_parser = subparsers.add_parser('version', help='show Oozappa version')
    version_parser.set_defaults(func=print_version)
    list_jobsets_parser = subparsers.add_parser('list', help='list jobsets')
    list_jobsets_parser.set_defaults(func=list_jobsets)
    manage_parser = subparsers.add_parser('manage', help='manage oozappa environment')
    manage_parser.set_defaults(func=manage_oozappa)
    run_jobset_parser = subparsers.add_parser('run_jobset', help='Run specified jobset')
    run_jobset_parser.add_argument('--jobset')
    run_jobset_parser.set_defaults(func=run_jobset_from_cli)
    args = parser.parse_args()
    args.func(args)
