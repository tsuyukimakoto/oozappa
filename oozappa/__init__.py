# -*- coding:utf8 -*-
import os
import sys
import subprocess
import time
import json


from oozappa.records import Environment, Job, Jobset, ExecuteLog, get_db_session
from oozappa.forms import EnvironmentForm

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

from flask import Flask, render_template, url_for, redirect
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

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/environments')
def environments():
  session = get_db_session()
  environment_list = session.query(Environment).all()
  return render_template('environment_list.html', environment_list=environment_list, form=EnvironmentForm())

@app.route('/add_environment', methods=['POST'])
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

#gunicorn -k flask_sockets.worker oozappa:app

# how can i pass env through different environment ?
# Set value to env that results execute task. how?

# JobSet organize Job, job is multiple fabric task. JobSet contains Job consists an environment and tasks.
