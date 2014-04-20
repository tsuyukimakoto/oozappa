# -*- coding:utf8 -*-
from oozappa.config import OozappaSetting
_ = OozappaSetting

import tempfile

settings = _(
	# OOZAPPA_DB: specify sqlite database stored file path.
	OOZAPPA_DB = 'sqlite:////tmp/oozappa.sqlite',
	# OOZAPPA_LOG: set True if you need output log to file.
	OOZAPPA_LOG = True, 
	# OOZAPPA_BASEDIR: specify output log file directory.
	OOZAPPA_LOG_BASEDIR = tempfile.gettempdir(), 
	# FLASK_SECRET_KEY: flask thing.
	FLASK_SECRET_KEY = '{0}',
)
