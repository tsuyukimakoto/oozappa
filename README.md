oozappa
=======

Fabric task runner and helper. Execute tasks via web browser.

oozappa is 大雑把.

install
=======

    $ git clone https://github.com/tsuyukimakoto/oozappa.git oozappa
    $ cd oozappa
    $ ln -s `pwd`/oozappa VIRTUALENV/lib/Python2.7/site-packages/oozappa
    $ pip install -r requirements.txt

oozappa fabric structures.
=======

see sample oozappa project(sample/ops).

    .
    ├── common
    │   ├── __init__.py
    │   ├── files
    │   ├── functions
    │   │   └── common_multiple_fabric_environment.py.py
    │   ├── templates
    │   │   └── sample_a.txt
    │   └── vars.py
    ├── production
    │   ├── fabfile
    │   │   └── __init__.py
    │   └── vars.py
    └── staging
        ├── fabfile
        │   └── __init__.py
        ├── templates
        │   └── sample_a.txt
        └── vars.py

__common__ is reserved directory. __production__ and __staging__ are environment directory. These two names are just example.

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

*) operation will change near future.

Change directory to outside environment directory.

    $ cd ..
    $ ls
    common		production	staging
    $ gunicorn -k flask_sockets.worker oozappa:app

It's ok to move outside more.

Open Safari and browse http://localhost:8000/ .

Modify left hand side input to __staging__ and click _run_tasks_. You can see what tasks exists.

Then input __ls ps__ to right hand side input and click _run_tasks_ .

That's it.

comming features
=======

Oozappa should manage environment and job, that is chained tasks, and execute log using database.

So, comming features are

* Admin interface
* Operation interface
