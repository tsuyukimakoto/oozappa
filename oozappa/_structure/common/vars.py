# -*- coding:utf8 -*-
from oozappa.config import OozappaSetting
_ = OozappaSetting

import tempfile

settings = _(
        # OOZAPPA_DB: specify sqlite database stored file path.
        OOZAPPA_DB = '{OOZAPPA_DB}',
        # OOZAPPA_LOG: set True if you need output log to file.
        OOZAPPA_LOG = True,
        # OOZAPPA_BASEDIR: specify output log file directory.
        OOZAPPA_LOG_BASEDIR = '{OOZAPPA_LOG_BASEDIR}',
        # FLASK_SECRET_KEY: flask thing.
        FLASK_SECRET_KEY = '{FLASK_SECRET_KEY}',
)
