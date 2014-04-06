# -*- coding:utf8 -*-
from fabric.main import load_fabfile
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref

import os

Base = declarative_base()

from functools import wraps

import logging
logger = logging.getLogger('oozappa')


def need_task(f):
    @wraps(f)
    def inner(self, *args, **kwargs):
        if not hasattr(self, 'task_dict'):
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

DB = 'sqlite:////tmp/oozappa.sqlite'

def get_db_session():
  engine = create_engine(DB, echo=True) #
  Session = sessionmaker(bind=engine)
  return Session()

from sqlalchemy import create_engine
engine = create_engine(DB, echo=True) #

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
metadata = Base.metadata #this knows table mapping class.
metadata.create_all(engine) #create table if not exists.

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

# job1 = Job(name='job1', description=u'とあるジョブ1', tasks='ls ps')
# job1.environment = stg_environment

# job2 = Job(name='job2', description=u'とあるジョブ2', tasks='sleep')
# job2.environment = stg_environment

# job3 = Job(name='job3', description=u'とあるジョブ3', tasks='ls')
# job3.environment = prd_environment

# jobset = Jobset(title=u'複数ジョブ', description=u'あれをやってこれをやる')
# jobset.jobs.append(job1)
# jobset.jobs.append(job2)
# jobset.jobs.append(job3)

# session.commit()

# how can i pass env through different environment ?
# Set value to env that results execute task. how?

# JobSet organize Job, job is multiple fabric task. JobSet contains Job consists an environment and tasks.
