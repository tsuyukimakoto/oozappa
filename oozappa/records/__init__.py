# -*- coding:utf8 -*-
from fabric.main import load_fabfile
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

import os
import sys
from datetime import datetime

Base = declarative_base()

from functools import wraps

import logging
logger = logging.getLogger('oozappa')

from oozappa.fabrictools import FabricHelper


def need_task(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        if not hasattr(self, 'task_dict'):
            if 'fabfile' in sys.modules.keys():
                del sys.modules['fabfile']
            self.task_dict = FabricHelper(os.path.join(self.execute_path, 'fabfile')).task_list()
        return f(self, *args, **kwargs)
    return inner


class Environment(Base):
    '''Target, normally this indicates fabfile.py or fabfile directory'''
    __tablename__ = 'environment'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    sort_order = Column(Integer)
    execute_path = Column(String)

    def __init__(self):
        self.task_dict = None

    @need_task
    def task_list(self):
        return self.task_dict.values()

    def __repr__(self):
        return "<Environment(name='%s', sort_order='%d', execute_path='%s')>" % (
            self.name, self.sort_order, self.execute_path)


class Jobset(Base):
    __tablename__ = 'jobset'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    sort_order = Column(Integer, server_default="1")
    cli_only = Column(Boolean)

    __mapper_args__ = {'order_by': 'Jobset.sort_order'}

    @property
    def jobs(self):
        return [j.job for j in self.jobsetlist]


class Job(Base):
    __tablename__ = 'job'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    environment_id = Column(Integer, ForeignKey('environment.id'))
    tasks = Column(String)
    environment = relationship("Environment", backref=backref('jobs', order_by=id))

    @staticmethod
    def choices():
        return [(x.id, x.name) for x in get_db_session().query(Job).all()]


class JobsetJobList(Base):
    __tablename__ = 'jobset_job'
    id = Column(Integer, primary_key=True)
    jobset_id = Column(Integer, ForeignKey('jobset.id'))
    job_id = Column(Integer, ForeignKey('job.id'))

    jobset = relationship("Jobset", backref=backref('jobsetlist', order_by=id))
    job = relationship("Job", backref=backref('jobsetlist', order_by=id))


class ExecuteLog(Base):
    __tablename__ = 'execute_log'
    id = Column(Integer, primary_key=True)
    success = Column(Boolean)
    started = Column(DateTime)
    finished = Column(DateTime)
    logfile = Column(String)
    jobset_id = Column(Integer, ForeignKey('jobset.id'))
    jobset = relationship("Jobset", backref=backref('execute_logs', order_by=id.desc()))

    def __init__(self):
        self.success = False
        self.started = datetime.now()

    def execute_time(self):
        if self.started and self.finished:
            return '{0:08.3f}'.format((self.finished - self.started).total_seconds())
        return ''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oozappa.config import get_config
_settings = get_config()


def get_db_session():
    engine = create_engine(_settings.OOZAPPA_DB, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def init():
    from sqlalchemy import create_engine
    engine = create_engine(_settings.OOZAPPA_DB, echo=False)
    metadata = Base.metadata  # this knows table mapping class.
    metadata.create_all(engine)  # create table if not exists.
