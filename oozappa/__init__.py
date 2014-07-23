# -*- coding:utf8 -*-
import os
import sys
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('oozappa')

version_info = (0, 8, 4)
__version__ = ".".join([str(v) for v in version_info])


class exec_fabric:
    def __init__(self, wsckt, path):
        self.wsckt = wsckt
        self.initial_path = os.getcwd()  # TODO
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

    def doit(self, fabric_commands=[], logfile=None):
        start_time = time.time()
        logger.debug('doit from running websocket: fab {0}'.format(' '.join(fabric_commands)))
        p = subprocess.Popen(["fab"] + fabric_commands,
          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
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
