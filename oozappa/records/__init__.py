# -*- coding:utf8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

import os

Base = declarative_base()

from functools import wraps

import logging
logger = logging.getLogger('oozappa')


def need_task(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        if not self.task_dict:
            self.task_dict = load_fabfile(self.execute_path)[1]
        return f(self, *args, **kwargs)
    return inner

class Environment(Base):
    '''Target, normally this indicates fabfile.py or fabfile directory'''
    __tablename__ = 'environment'

    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True)
    sort_order = Column(Integer)
    execute_path = Column(String)

    def __init__(self):
        self.task_dict = None

    @need_task
    def task_list(self):
        for task in self.task_dict.values():
            print('{0:10}: {1}'.format(task.name, task.__doc__ or ''))

    def __repr__(self):
       return "<Environment(name='%s', sort_order='%d', execute_path='%s')>" % (
                            self.name, self.sort_order, self.execute_path)

class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    environment_id = Column(Integer, ForeignKey('environment.id'))
    tasks = Column(String)
    environment = relationship("Environment", backref=backref('jobs', order_by=id))

class ExecuteLog(Base):
    __tablename__ = 'execute_log'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job.id'))
    success = Column(Boolean)
    started = Column(DateTime)
    finished = Column(DateTime)
    jobs = relationship("Job", backref=backref('execute_logs', order_by=id.desc()))
