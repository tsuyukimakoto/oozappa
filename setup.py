#!/usr/bin/env python
# -*- coding:utf8 -*-
u'''
Oozappa
============================================================

Fabric task runner and helper. Execute tasks via web browser.

oozappa is 大雑把.

Change logs.
-------------------------------------------

0.9.0
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding new subcommands to zappa.

  * list
  * run_jobset
  * manage

Removed rapid execution.

Adding cli_only flag to Jobset.Now set cli_only flag using zappa manage. Now you can make Jobset can't run from web ui.

Decoupling webui from fabric execution(Error doesn't occur even if connection reset).

Show comfirm dialog before leaving web ui. and better ux. thank you yusuke furukawa.

0.8.5
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding new feature, modify Jobsets sort order on jobsets page.

Adding new feature, modify a Job data on environ page.

Improve Fabric task's behavior better when failed.

You need db migration if you use 0.8.4 or below.

Download zip archive from https://github.com/tsuyukimakoto/oozappa/raw/master/migration/to_0.8.5.zip

::

  $ unzip to_0.8.5.zip && cd oozappa_to_0_8_5

  If you have not alembic installed. You need install it using pip or any way you like.
  Open alembic.ini and modify sqlalchemy.url to indicate your own oozappa's db. then

  $ alembic upgrade 1e26220da128

0.8.4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Jobset runs exclusively from webui.

0.8.3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A zappa command added and removed oozappa.create_environment module.

0.8.2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Oozappa finds tasks from imported modules, not recursive.

Install
-------------------------------------------

Install from Cheese Shop (pypi).

::

    $ pip install oozappa

If you use Xcode 5.1(above) and failed with **clang: error: unknown argument: '-mno-fused-madd'** , export flags before install.
::

    $ export CPPFLAGS=-Qunused-arguments
    $ export CFLAGS=-Qunused-arguments

Oozappa data models.
-------------------------------------------

Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Environment is a category that has fibfile directory and vars.py .

A problem about fabric with large project is, too many fabric tasks and complicated task orders.

So you should separate fabfile into domain category. That is Environment.

Job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Job is like a normal fabric execution command.

note::

 fab task1 task2 is a job.

Jobset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Jobset is oozappa operation unit.

Jobset can contain multiple job, even extend over environments.

Oozappa fabric structures.
-------------------------------------------

See sample oozappa project( https://github.com/tsuyukimakoto/oozappa/tree/master/sample/ops ).
::

    .
    ├── common
    │   ├── __init__.py
    │   ├── files
    │   ├── functions
    │   │   ├── common_multiple_fabric_environment.py
    │   ├── templates
    │   │   └── sample_a.txt
    │   └── vars.py
    ├── construction
    │   ├── fabfile
    │   │   ├── __init__.py
    │   │   └── cloud.py
    │   ├── templates
    │   └── vars.py
    ├── deployment
    │   ├── fabfile
    │   │   ├── __init__.py
    │   ├── templates
    │   └── vars.py
    ├── production
    │   ├── fabfile
    │   │   ├── __init__.py
    │   ├── templates
    │   └── vars.py
    └── staging
        ├── fabfile
        │   ├── __init__.py
        ├── templates
        │   └── sample_a.txt
        └── vars.py

**common** is reserved directory. **construction** and others are environment directory. These names except common are just example.

vars
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

common and each environment's vars.py might have oozappa.config.OozappaSetting instance named settings.
OozappaSetting is dict like object.

**common.vars.setting** is updated by executed environment's **vars.setting** , so you can set base configuration to common.vars.setting and environment's one overwrite it.

Check printsetting task on staging environment.

You can run fabric task within environment directory as usual.
::

    $ cd sample/ops/staging
    $ fab printsetting
    {'instance_type': 't1.micro', 'domain': 'localhost', 'sample_template_vars': {'sample_a': {'key_a_2': "a's 2 value from common.vars", 'key_a_1': "a's 1 value from stging.vars"}}, 'email': 'mtsuyuki at gmail.com'}

See common/vars.py and staging/vars.py .

templates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Same as vars, **oozappa.fabrictools.upload_template** search template. upload_template is almost same as **fabric.contrib.files.upload_template** . oozappa's upload_template doesn't accept use_jinja, because oozappa's upload_template pass use_jinja=True to fabric.contrib.files.upload_template.

Jinja2 has inheritance template system and search template from multipul paths. fabric's upload_template accept only one template_dir string not list. **fabric doesn't assume multiplu environment** , so it's reasonable.
Because of this, oozappa's upload_template search template path is limited only one template_dir that found filename.
It mean that you can't store child template and parent template separately.

common/functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Call **oozappa.config.procure_common_functions** () and add commons/functions directory to sys.path for convinient to using on multiple fabric environment.

Run fabric task via web browser.
-----------------------------------------------------------

Change directory to outside environment directory.
::

    $ cd ..
    $ ls
    common    production  staging
    $ gunicorn -t 3600 -k flask_sockets.worker oozappa.webui:app

Running oozappa:app creates **/tmp/oozappa.sqlite** .

Open your web browser and browse http://localhost:8000/ .

Rapid execution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modify *Run fabric in raw*'s left hand side input to **staging** and click *run_tasks*. You can see what tasks exists.

Then input **ls ps** to right hand side input and click *run_tasks* .

That's it.

Better way using sample
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

register environment to db.
___________________________

* Click environment button via top menu.

* Add new Environment

  * name: constructiton

  * sort_order: 1

  * execute_path: constructiton

* Add 3 more.

.. image:: https://dl.dropboxusercontent.com/u/382460/oozappa/readme/environments.png
  :alt: environments

create job in each environments.
_________________________________

* Click environment you created

* Create new Job.

  * Click task from Possible tasks in order

.. image:: https://dl.dropboxusercontent.com/u/382460/oozappa/readme/create_job.png
  :alt: job

create jobset
___________________________

* Click jobset button via top menu.

* Click jobs you'd like to execute once.

.. image:: https://dl.dropboxusercontent.com/u/382460/oozappa/readme/create_jobset.png
  :alt: jobset


run jobset
___________________________

* Click navigation button or jobset button via top menu.

* Click jobset you'd like to execute.

* Click *run jobset* button.
* Running log displays **Running log**.

* Reload page when jobset done. or Go to top(via navigation button)

  * You see Execute Logs and show raw log when you click success (or fail).

.. image:: https://dl.dropboxusercontent.com/u/382460/oozappa/readme/jobset.png
  :alt: running jobset

How to create your own
-------------------------------------------

Create common directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change directory your own oozappa.
::

    $ mkdir devops
    $ cd devops

Then run zappa command.
::

    $ zappa init
    Create common environment here? [y/N] : y
    Sqlite database stored path. [/tmp/oozappa/data.sqlite] :
    Log files stored path. [/tmp/oozappa] :
    Create directory or exit? "/tmp/oozappa" [y/N] : y
    created common directory. db/log file path and flask secret key are in common/vars.py.

.. attention:: Default stored path is not for production use.
   You should input your own file/directory path. Or data/results disapear when you reboot your machine or server.

How to change settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open `common/vars.py` and change settings.

* **OOZAPPA_DB**

  sqlite's data store path.

* **OOZAPPA_LOG_BASEDIR**

  Jobset execute log store directory path.

Create environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run `zappa` command with names option.
::

  $ zappa create_environment --names construction deployment
  2014-04-20 16:43:26,543 INFO create environment : construction
  2014-04-20 16:43:26,544 INFO create environment : deployment

Then you can write fabfile normally and execute via oozappa.
'''
import setuptools
from distutils.core import setup

from oozappa import __version__

setup(name='oozappa',
      version=__version__,
      description='Fabric task runner and helper. Executes and manages tasks via web browser.',
      author='makoto tsuyuki',
      author_email='mtsuyuki@gmail.com',
      url='https://github.com/tsuyukimakoto/oozappa',
      zip_safe=False,
      entry_points='''
            [console_scripts]
            zappa = oozappa.zappa:main
            ''',
      long_description=__doc__,
      classifiers=['Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Clustering',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
      ],
      packages=['oozappa', 'oozappa.records',],
      package_data={'oozappa': ['_structure/_environment/vars.py','_structure/_environment/*/*', '_structure/_environment/templates/*',
        '_structure/common/vars.py','_structure/common/__init__.py','_structure/common/*/*', 'static/css/*', 'templates/*']},
      include_package_data=True,
      install_requires=['Fabric>=1.8.3','Flask-WTF>=0.9.5','Flask-SQLAlchemy>=1.0','Flask-Sockets>=0.1',
        'Jinja2>=2.7.2', 'Pygments>=1.6', 'gevent-websocket>=0.9.3','gunicorn>=18.0','filelock>=0.2.0'],
     )
