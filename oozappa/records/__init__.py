# -*- coding:utf8 -*-
from fabric.main import load_fabfile
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

import os
import sys

Base = declarative_base()

from functools import wraps

import logging
logger = logging.getLogger('oozappa')


def need_task(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        if not hasattr(self, 'task_dict'):
            if 'fabfile' in sys.modules.keys():
                del sys.modules['fabfile']
            self.task_dict = load_fabfile(os.path.join(self.execute_path, 'fabfile'))[1]
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
        return self.task_dict.values()

    def __repr__(self):
       return "<Environment(name='%s', sort_order='%d', execute_path='%s')>" % (
                            self.name, self.sort_order, self.execute_path)

jobset_job_table = Table('jobset_job', Base.metadata,
    Column('jobset_id', Integer, ForeignKey('jobset.id')),
    Column('job_id', Integer, ForeignKey('job.id'))
)

class Jobset(Base):
    __tablename__ = 'jobset'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    jobs = relationship("Job",
                    secondary=jobset_job_table)

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

class ExecuteLog(Base):
    __tablename__ = 'execute_log'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job.id'))
    success = Column(Boolean)
    started = Column(DateTime)
    finished = Column(DateTime)
    jobset_id = Column(Integer, ForeignKey('jobset.id'))
    jobset = relationship("Jobset", backref=backref('execute_logs', order_by=id.desc()))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from oozappa.config import get_config, procure_common_functions
_settings = get_config()
DB = _settings.OOZAPPA_DB

def get_db_session():
    engine = create_engine(DB, echo=False) #
    Session = sessionmaker(bind=engine)
    return Session()

def init():
    from sqlalchemy import create_engine
    engine = create_engine(DB, echo=False) #

    from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
    metadata = Base.metadata #this knows table mapping class.
    metadata.create_all(engine) #create table if not exists.

