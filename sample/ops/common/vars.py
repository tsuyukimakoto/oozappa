# -*- coding:utf8 -*-
from oozappa.config import OozappaSetting
_ = OozappaSetting

settings = _(
    email = 'mtsuyuki at gmail.com',
    instance_type = 'c3.large',
    sample_template_vars = _(
        sample_a = _(
            key_a_1 = "a's 1 value from common.vars",
            key_a_2 = "a's 2 value from common.vars",
        ),
    ),
)
