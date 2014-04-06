# -*- coding:utf8 -*-
import os
import sys
import subprocess
import time
import json


from oozappa.records import Environment, Job, Jobset, ExecuteLog, get_db_session
from oozappa.forms import EnvironmentForm, JobForm, JobSetForm
from oozappa.fabrictools import get_tasks

import logging

logging.basicConfig(level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('oozappa')

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

    def doit(self, fabric_commands = []):
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
        # print(line.strip())
      self.wsckt.send('takes {0:.2f} sec'.format(time.time() - start_time))
      return p.wait()

logger.setLevel(logging.DEBUG)

from flask import Flask, render_template, url_for, redirect, request
from flask_sockets import Sockets

app = Flask('oozappa')
app.config['SECRET_KEY'] = 'ultra oozappa'
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
  for job in jobset.jobs:
    with exec_fabric(ws, job.environment.execute_path) as executor:
      executor.doit(job.tasks.split(' '))

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
    jobset.jobs = session.query(Job).filter(Job.id.in_(form.job_id.data)).all()
    session.add(jobset)
    session.commit()
    return redirect(url_for('jobsets'))
  return render_template('create_jobset.html', form=form, job_list=session.query(Job).all())

@app.route('/jobsets/<jobset_id>/', methods=['GET', 'POST'])
def jobset(jobset_id):
  session = get_db_session()
  jobset = session.query(Jobset).get(jobset_id)
  # form = JobSetForm(request.form, jobset)
  # form.job_id.choices = Job.choices()
  # if form.validate_on_submit():
  #   form.populate_obj(jobset)
  #   session.add(jobset)
  #   session.commit()
  #   return redirect(url_for('jobset', jobset_id=jobset_id))
  return render_template('jobset.html', form=form, jobset=jobset, job_list=session.query(Job).all())

#gunicorn -k flask_sockets.worker oozappa:app

# how can i pass env through different environment ?
# Set value to env that results execute task. how?

# JobSet organize Job, job is multiple fabric task. JobSet contains Job consists an environment and tasks.
