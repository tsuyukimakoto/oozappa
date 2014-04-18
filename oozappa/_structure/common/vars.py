# -*- coding:utf8 -*-
from oozappa.config import OozappaSetting
_ = OozappaSetting

import tempfile

settings = _(
	OOZAPPA_DB = 'sqlite:////tmp/oozappa.sqlite',
	OOZAPPA_LOG = True, 
	OOZAPPA_LOG_BASEDIR = tempfile.gettempdir(), 
	FLASK_SECRET_KEY = '{0}',
)
