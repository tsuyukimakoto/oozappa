oozappa
=======

[![Join the chat at https://gitter.im/tsuyukimakoto/oozappa](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/tsuyukimakoto/oozappa?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Fabric task runner and helper. Execute tasks via web browser.

oozappa is 大雑把.

install
=======

Install from Cheese Shop (pypi).

    $ pip install oozappa

If you use Xcode 5.1(above) and failed with __clang: error: unknown argument: '-mno-fused-madd'__, export flags before install pycrypt (before pip install -r requirements.txt).

    $ export CPPFLAGS=-Qunused-arguments
    $ export CFLAGS=-Qunused-arguments

oozappa data models.
=======

## Environment

Environment is a category that has fibfile directory and vars.py .

A problem about fabric with large project is, too many fabric tasks and complicated task orders.

So you should separate fabfile into domain category. That is Environment.

## Job

Job is like a normal fabric execution command.

 _eg. fab task1 task2 is a job._

## Jobset

Jobset is oozappa operation unit.

Jobset can contain multiple job, even extend over environments. 

oozappa fabric structures.
=======

see sample oozappa project(sample/ops).

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

__common__ is reserved directory. __construction__ and others are environment directory. These names are just example.

## vars

common and each environment's vars.py might have oozappa.config.OozappaSetting instance named settings.
OozappaSetting is dict like object.
common.vars.setting is updated by executed environment's vars.setting, so you can set base configuration to common.vars.setting and environment's one overwrite it.

Check printsetting task on staging environment.

You can run fabric task within environment directory as usual.

    $ cd sample/ops/staging
    $ fab printsetting
    {'instance_type': 't1.micro', 'domain': 'localhost', 'sample_template_vars': {'sample_a': {'key_a_2': "a's 2 value from common.vars", 'key_a_1': "a's 1 value from stging.vars"}}, 'email': 'mtsuyuki at gmail.com'}

See common/vars.py and staging/vars.py .

## templates

Same as vars, __oozappa.fabrictools.upload_template__ search template. upload_template is almost same as __fabric.contrib.files.upload_template__ . oozappa's upload_template doesn't accept use_jinja, because oozappa's upload_template pass use_jinja=True to fabric.contrib.files.upload_template.

Jinja2 has inheritance template system and search template from multipul paths. fabric's upload_template accept only one template_dir string not list. __fabric doesn't assume multiplu environment__, so it's reasonable.
Because of this, oozappa's upload_template search template path is limited only one template_dir that found filename.
It mean that you can't store child template and parent template separately.

## common/functions

Call __oozappa.config.procure_common_functions__() and add commons/functions directory to sys.path for convinient to using on multiple fabric environment.

run fabric task via web browser.
=======

Change directory to outside environment directory.

    $ cd ..
    $ ls
    common		production	staging
    $ gunicorn -t 3600 -w 4 -k flask_sockets.worker oozappa.webui:app

Running oozappa:app creates __/tmp/oozappa.sqlite__ .

Open your web browser and browse http://localhost:8000/ .

## rapid execution

rapid execution function removed(version 0.9.0).

~~Modify _Run fabric in raw_'s left hand side input to __staging__ and click _run_tasks_. You can see what tasks exists.~~

~~Then input __ls ps__ to right hand side input and click _run_tasks_ .~~

~~That's it.~~

## better way using sample

### register environment to db.

* Click environment button via top menu.
* Add new Environment
	* name: constructiton 
	* sort_order: 1
	* execute_path: constructiton
* Add 3 more.

![environments](https://raw.github.com/wiki/tsuyukimakoto/oozappa/images/readme/environments.png "environments")

### create job in each environments.

* Click environment you created
* Create new Job.
	* Click task from Possible tasks in order

![job](https://raw.github.com/wiki/tsuyukimakoto/oozappa/images/readme/create_job.png "job")

### create jobset

* Click jobset button via top menu.
* Click jobs you'd like to execute once.

![jobset](https://raw.github.com/wiki/tsuyukimakoto/oozappa/images/readme/create_jobset.png "jobset")

### run jobset

* Click navigation button or jobset button via top menu.
* Click jobset you'd like to execute.
* Click _run jobset_ button.
* Running log displays __Running log__.
* Reload page when jobset done. or Go to top(via navigation button)
	* You see Execute Logs and show raw log when you click success (or fail).

![runnig jobset](https://raw.github.com/wiki/tsuyukimakoto/oozappa/images/readme/jobset.png "running jobset")

How to create your own
=======

## Create common directory

Change directory your own oozappa.

    $ mkdir devops
    $ cd devops

Then run zappa command.

    $ zappa init
    Create common environment here? [y/N] : y
    Sqlite database stored path. [/tmp/oozappa/data.sqlite] :
    Log files stored path. [/tmp/oozappa] :
    Create directory or exit? "/tmp/oozappa" [y/N] : y
    created common directory. db/log file path and flask secret key are in common/vars.py.

> attention:: Default stored path is not for production use.
  You should input your own file/directory path. Or data/results disapear when you reboot your machine or server.

## How to Change settings

Open `common/vars.py` and change settings.

* __OOZAPPA_DB__ : sqlite's data store path.
* __OOZAPPA_LOG_BASEDIR__ : Jobset execute log store directory path.

## create environment

Run oozappa.create_environment with environment name(s).

    $ zappa create_environment --names construction deployment
    2014-04-20 16:43:26,543 INFO create environment : construction
    2014-04-20 16:43:26,544 INFO create environment : deployment

Then you can write fabfile normally and execute via oozappa.


## run jobset from zappa command.

### list jobsets

    $ zappa list
    ----------------------------------------
    |id:001|CLI_ONLY:False|title:デプローイのテスト１|
    |id:002|CLI_ONLY:True|title:デプロイプリント|
    ----------------------------------------

### run jobset

    $ zappa run_jobset --jobset 1

### make jobset runnable only cli

Only jobset which CLI_ONLY flag is False can run using webui.

You can set CLI_ONLY flag to True with zappa command.

    $ zappa manage
    <manage:/Users/makoto/oozappa/oozappa>
     commands
        -> q: quit
        -> c: Modify Jobset's CLI Flag.
        -> l: List Jobsets
        -> n: next
    c
    ----------------------------------------
    |id:001|CLI_ONLY:False|title:デプローイのテスト１|
    |id:002|CLI_ONLY:True|title:デプロイプリント|
    ----------------------------------------
    Which Jobset id?2
    ----------------------------------------
    |id:001|CLI_ONLY:False|title:デプローイのテスト１|
    |id:002|CLI_ONLY:False|title:デプロイプリント|
    ----------------------------------------
     commands
        -> q: quit
        -> c: Modify Jobset's CLI Flag.
        -> l: List Jobsets
        -> n: next
    q

