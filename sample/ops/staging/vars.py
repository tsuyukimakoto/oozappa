# -*- coding:utf8 -*-
from oozappa.config import OozappaSetting
_ = OozappaSetting

settings = _(
    domain = 'localhost',
    instance_type = 't1.micro',
    sample_template_vars = _(
        sample_a = _(
            key_a_1 = "a's 1 value from stging.vars",
        ),
    ),
)
