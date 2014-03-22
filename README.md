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
    │   └── vars.py
    ├── production
    │   ├── fabfile
    │   │   └── __ini__.py
    │   └── vars.py
    └── staging
        ├── fabfile
        │   └── __init__.py
        └── vars.py

__common__ is reserved directory. __production__ and __staging__ are environment directory. These two names are just example.

common and each environment's vars.py might have oozappa.config.OozappaSetting instance named settings.
OozappaSetting is dict like object.
common.vars.setting is updated by executed environment's vars.setting, so you can set base configuration to common.vars.setting and environment's one overwrite it.

Check printsetting task on staging environment.

You can run fabric task within environment directory as usual.

    $ cd sample/ops/staging
    $ fab printsetting
    {'instance_type': 't1.micro', 'domain': 'localhost', 'email': 'mtsuyuki at gmail.com'}

See common/vars.py and staging/vars.py .

run fabric task via web browser.
=======

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
