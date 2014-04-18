# -*- coding:utf8 -*-
import os
import sys
import subprocess
import time
import json


from oozappa.records import Environment, Job, Jobset, ExecuteLog, get_db_session, init as init_db
from oozappa.forms import EnvironmentForm, JobForm, JobSetForm
from oozappa.fabrictools import get_tasks

import logging
from uuid import uuid4
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, request
from flask_sockets import Sockets

logging.basicConfig(level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('oozappa')
logger.setLevel(logging.DEBUG)

class exec_fabric:
    def __init__(self, wsckt, path):
        self.wsckt = wsckt
        self.initial_path = os.getcwd() #TODO
        if not os.path.isabs(path):
            self.exec_path = os.path.join(self.initial_path, path)
        else:
            self.exec_path = path
        self.path_appended = False

    def __enter__(self):
        os.chdir(self.exec_path)
        if not self.exec_path in sys.path:
            sys.path.insert(0, self.exec_path)
            self.path_appended = True
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.initial_path)
        if self.path_appended:
            sys.path.remove(self.exec_path)

    def doit(self, fabric_commands = [], logfile=None):
      start_time = time.time()
      logger.debug('doit from running websocket: fab {0}'.format(' '.join(fabric_commands)))
      p = subprocess.Popen(["fab"] + fabric_commands,
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      stderr = p.stdout
      while True:
        line = stderr.readline()
        if not line:
          break
        self.wsckt.send(line)
        if logfile:
          logfile.write(line)
        # print(line.strip())
      self.wsckt.send('takes {0:.2f} sec'.format(time.time() - start_time))
      return p.wait()

app = Flask('oozappa')
from oozappa.config import get_config, procure_common_functions
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

@sockets.route('/run_task')
def run_task(ws):
  message = ws.receive()
  data = json.loads(message)
  if not data.get('fabric_path', None):
    ws.send('need fabric_path')
    return
  if not data.get('tasks', None):
    from oozappa.fabrictools import FabricHelper
    helper = FabricHelper(data.get('fabric_path'))
    ws.send('specify task(s) below.\n  ' + '\n  '.join(helper.task_list()))
    return
  with exec_fabric(ws, data['fabric_path']) as executor:
      executor.doit(data['tasks'].split(' '))

@sockets.route('/run_jobset')
def run_jobset(ws):
  message = ws.receive()
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
  if logfile:
    logfile.close()

@app.route('/')
def index():
  session = get_db_session()
  jobset_list = session.query(Jobset).all()
  return render_template('index.html', jobset_list=jobset_list)

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
    environ.name=form.name.data
    environ.sort_order=form.sort_order.data
    environ.execute_path=form.execute_path.data
    session.add(environ)
    session.commit()
    return redirect(url_for('environments'))
  return render_template('environment_list.html', form=form)

@app.route('/emvironments/<environment_id>/', methods=['GET', 'POST'])
def environment(environment_id):
  session = get_db_session()
  environ = session.query(Environment).get(environment_id)
  error_message = None
  form = JobForm()
  if not environ:
    abort(404)
  if form.validate_on_submit():
    not_found_tasks = get_tasks(environ.execute_path, form.tasks.data.split(' ')).get('not_found')
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
  return render_template('environment.html', form=form, environ=environ, error_message=error_message)

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
      jobset.jobs.append(j)
    session.commit()
    return redirect(url_for('jobsets'))
  return render_template('create_jobset.html', form=form, job_list=session.query(Job).all())

@app.route('/jobsets/<jobset_id>/', methods=['GET', 'POST'])
def jobset(jobset_id):
  session = get_db_session()
  jobset = session.query(Jobset).get(jobset_id)
  return render_template('jobset.html', jobset=jobset, job_list=session.query(Job).all())

if __name__ == '__main__':
  pass

#gunicorn -k flask_sockets.worker oozappa:app
