# -*- coding:utf8 -*-
from fabric.api import task, local, run, sudo, env

from oozappa.config import get_config, procure_common_functions
_settings = get_config()
procure_common_functions()

# your own task below
