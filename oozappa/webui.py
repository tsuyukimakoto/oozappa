# -*- coding:utf8 -*-
import os
import sys
import json

from oozappa import exec_fabric
from oozappa.records import Environment, Job, Jobset, JobsetJobList, ExecuteLog, get_db_session, init as init_db
from oozappa.forms import EnvironmentForm, JobForm, JobSetForm
from oozappa.fabrictools import FabricHelper

import logging
from uuid import uuid4
from datetime import datetime
import time

from flask import Flask, render_template, url_for, redirect, Response, abort, jsonify
from flask_sockets import Sockets

import filelock

logging.basicConfig(level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('oozappa')
# logger.setLevel(logging.DEBUG)

app = Flask('oozappa')
from oozappa.config import get_config
_settings = get_config()
try:
    app.config['SECRET_KEY'] = _settings.FLASK_SECRET_KEY
except AttributeError:
    should_create = raw_input('Create common environment here? [y/N]')
    if should_create == 'y':
        import shutil
        current = os.getcwd()
        shutil.copytree(os.path.join(os.path.dirname(__file__), '_structure', 'common'), 'common')
        with open('common/vars.py') as f:
            data = f.read()
        with open('common/vars.py', 'w') as f:
            f.write(data.format(uuid4().hex))
        print('create common directory. db file path and flask secret key are in common/vars.py.')
        sys.exit(0)
    print("couldn't find FLASK_SECRET_KEY in your ENVIRONMENT/vars.py")
    sys.exit(1)

init_db()
sockets = Sockets(app)


@app.template_filter('datetimefmt')
def _datetimefmt(d):
    return d and d.strftime("%Y/%m/%d %H:%M:%S") or ''

LOCK_FILE_NAME = 'oozappa_lock_file'

def _is_locked():
    return os.path.exists(LOCK_FILE_NAME)

def _locked_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(LOCK_FILE_NAME).st_ctime))

@sockets.route('/run_task')
def run_task(ws):
    message = ws.receive()
    if not message:
        return
    data = json.loads(message)
    if not data.get('fabric_path', None):
        ws.send('need fabric_path')
        return
    if not data.get('tasks', None):
        helper = FabricHelper(data.get('fabric_path'))
        ws.send('specify task(s) below.\n  ' + '\n  '.join(helper.task_list()))
        return
    lock = filelock.FileLock(LOCK_FILE_NAME)
    try:
        with lock.acquire(timeout=1):
            with exec_fabric(ws, data['fabric_path']) as executor:
                executor.doit(data['tasks'].split(' '))
    except filelock.Timeout as err:
        ws.send('''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            Lock aquired another jobset from {0}

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''.format(_locked_time()))
        return


@sockets.route('/run_jobset')
def run_jobset(ws):
    message = ws.receive()
    if not message:
        return
    lock = filelock.FileLock(LOCK_FILE_NAME)
    try:
        with lock.acquire(timeout=1):
            data = json.loads(message)
            jobset_id = data.get('jobset_id')
            session = get_db_session()
            jobset = session.query(Jobset).get(jobset_id)
            executelog = ExecuteLog()
            executelog.jobset = jobset
            session.add(executelog)
            session.commit()
            logfile = None
            if _settings.OOZAPPA_LOG:
                executelog.logfile = os.path.join(_settings.OOZAPPA_LOG_BASEDIR,
                  '{0}.log'.format(uuid4().hex))
                logfile = open(executelog.logfile, 'w')
            for job in jobset.jobs:
                with exec_fabric(ws, job.environment.execute_path) as executor:
                    executor.doit(job.tasks.split(' '), logfile)
            else:
                executelog.success = True
                executelog.finished = datetime.now()
                session.commit()
                ws.send('\n&nbsp;\n&nbsp;\n')
                ws.send('=' * 35)
                ws.send('\n')
                ws.send(u'[Oozappa:FINISHED] Jobset: {0} in {1} seconds.'.format(jobset.title,
                  executelog.execute_time()).encode('utf8'))
                ws.send('\n')
                ws.send('=' * 35)
                ws.send('\n&nbsp;\n&nbsp;\n')
            if logfile:
                logfile.close()
    except filelock.Timeout as err:
        ws.send('''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            Lock aquired another jobset from {0}

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''.format(_locked_time()))


@app.route('/')
def index():
    session = get_db_session()
    jobset_list = session.query(Jobset).all()
    executelog_list = session.query(ExecuteLog).order_by(ExecuteLog.id.desc()).all()[:20]
    return render_template('index.html', jobset_list=jobset_list, executelog_list=executelog_list)


@app.route('/environments')
def environments():
    session = get_db_session()
    environment_list = session.query(Environment).all()
    return render_template('environment_list.html', environment_list=environment_list, form=EnvironmentForm())


@app.route('/environments/add', methods=['POST'])
def add_environment():
    form = EnvironmentForm()
    if form.validate_on_submit():
        session = get_db_session()
        #TODO
        environ = Environment()
        environ.name = form.name.data
        environ.sort_order = form.sort_order.data
        environ.execute_path = form.execute_path.data
        session.add(environ)
        session.commit()
        return redirect(url_for('environments'))
    return render_template('environment_list.html', form=form)


@app.route('/emvironments/<environment_id>/', methods=['GET', 'POST'])
def environment(environment_id):
    session = get_db_session()
    environ = session.query(Environment).get(environment_id)
    helper = FabricHelper(environ.execute_path)
    error_message = None
    form = JobForm()
    if not environ:
        abort(404)
    if form.validate_on_submit():
        not_found_tasks = helper.get_tasks(form.tasks.data.split(' ')).get('not_found')
        if len(not_found_tasks) == 0:
            job = Job()
            job.name = form.name.data
            job.description = form.description.data
            job.tasks = form.tasks.data
            job.environment = environ
            session.commit()
            return redirect(url_for('environment', environment_id=environment_id))
        error_message = 'tasks [{0}] not found.'.format(','.join(not_found_tasks))
    form.environment_id.data = environ.id
    return render_template('environment.html', form=form,
      environ=environ, environ_doc=helper.doc, error_message=error_message)


@app.route('/jobsets')
def jobsets():
    session = get_db_session()
    jobset_list = session.query(Jobset).all()
    return render_template('jobset_list.html', jobset_list=jobset_list)


@app.route('/jobsets/create', methods=['GET', 'POST'])
def create_jobset():
    form = JobSetForm()
    form.job_id.choices = Job.choices()
    session = get_db_session()
    if form.validate_on_submit():
        jobset = Jobset()
        jobset.title = form.title.data
        jobset.description = form.description.data
        session.add(jobset)
        for id in form.job_id.data:
            j = session.query(Job).get(id)
            jsl = JobsetJobList()
            jsl.jobset = jobset
            jsl.job = j
            session.add(jsl)
        session.commit()
        return redirect(url_for('jobsets'))
    return render_template('create_jobset.html', form=form, job_list=session.query(Job).all())


@app.route('/jobsets/<jobset_id>/', methods=['GET', 'POST'])
def jobset(jobset_id):
    session = get_db_session()
    jobset = session.query(Jobset).get(jobset_id)
    return render_template('jobset.html', jobset=jobset, job_list=session.query(Job).all(), executelog_list=jobset.execute_logs[:10])


@app.route('/get_execute_log/<id>/', methods=['GET'])
def get_execute_log(id):
    session = get_db_session()
    executelog = session.query(ExecuteLog).get(id)
    if not executelog.logfile:
        abort(404)
    with open(executelog.logfile, 'r') as f:
        logs = f.read()
    return Response(logs, mimetype='text/plain')

@app.route('/is_running_something.json', methods=['GET'])
def is_running_something():
    if _is_locked():
        return jsonify(dict(running=True, locked_time=_locked_time()))
    return jsonify(dict(running=False))

#gunicorn -t 3600 -k flask_sockets.worker oozappa.webui:app
