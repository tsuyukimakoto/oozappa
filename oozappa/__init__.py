import os
import sys
import subprocess
import time
import json

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

from flask import Flask, render_template
from flask_sockets import Sockets

app = Flask('oozappa')
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

#gunicorn -k flask_sockets.worker oozappa:app

# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///:memory:', echo=True) #

# from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
# metadata = Base.metadata #this knows table mapping class.

# metadata.create_all(engine) #create table if not exists.

# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine)
# session = Session()

# stg_environment = Environment()
# stg_environment.name = 'Staging'
# stg_environment.sort_order = 2
# stg_environment.execute_path = 'sample/ops/staging'
# prd_environment = Environment()
# prd_environment.name = 'Production'
# prd_environment.sort_order = 1
# prd_environment.execute_path = 'sample/ops/production'
# session.add(stg_environment)
# session.add(prd_environment)
# session.commit()


