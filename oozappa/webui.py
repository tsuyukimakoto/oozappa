# -*- coding:utf8 -*-
import os
import sys
import json
import urlparse

from oozappa import exec_fabric, run_jobset as _run_jobset, LogWebsocketCommunicator
from oozappa.records import (Environment, Job, Jobset, JobsetJobList,
                             ExecuteLog, get_db_session, init as init_db)
from oozappa.forms import EnvironmentForm, JobForm, JobSetForm
from oozappa.fabrictools import FabricHelper

import logging
from uuid import uuid4
import time

from flask import (Flask, render_template, url_for, redirect, Response,
                   abort, jsonify, request)
from flask_sockets import Sockets

import filelock

logger = logging.getLogger(__name__)

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
            with LogWebsocketCommunicator(ws, _settings.OOZAPPA_LOG_BASEDIR) as communicator:
                # communicator.write('[[webui]]\n')
                _run_jobset(jobset_id, communicator)
    except filelock.Timeout as err:
        ws.send(json.dumps({'output': '''
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            Lock aquired another jobset from {0}

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
'''.format(_locked_time())}))


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

@app.route('/emvironments/<environment_id>/job/<job_id>/', methods=['GET', 'POST'])
def job(environment_id, job_id):
    session = get_db_session()
    environ = session.query(Environment).get(environment_id)
    job = session.query(Job).get(job_id)
    helper = FabricHelper(environ.execute_path)
    error_message = None
    form = JobForm(
        name=job.name, description=job.description,
        environment_id=job.environment_id,
        tasks=job.tasks
    )
    if not environ:
        abort(404)
    if form.validate_on_submit():
        not_found_tasks = helper.get_tasks(form.tasks.data.split(' ')).get('not_found')
        if len(not_found_tasks) == 0:
            job.name = form.name.data
            job.description = form.description.data
            job.tasks = form.tasks.data
            job.environment = environ
            session.commit()
            return redirect(url_for('environment', environment_id=environment_id))
        error_message = 'tasks [{0}] not found.'.format(','.join(not_found_tasks))
    form.environment_id.data = environ.id
    return render_template('job.html', form=form,
      environ=environ, job=job, error_message=error_message)

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

@app.route('/jobsets/reorder/', methods=['POST'])
def reorder_jobset():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        return jsonify(res='error'), 400
    jobset_id_ordered = [int(x) for x in urlparse.parse_qs(request.json).get('jobset[]', [])]
    session = get_db_session()
    for i, jobset_id in enumerate(jobset_id_ordered):
        _sort_order = i + 1
        _jobset = session.query(Jobset).get(jobset_id)
        if _jobset.sort_order != _sort_order:
            _jobset.sort_order = _sort_order
    session.commit()
    return jsonify(res='ok')

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
