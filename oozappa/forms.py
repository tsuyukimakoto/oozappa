# -*- coding:utf8 -*-
import os
from flask_wtf import Form
from wtforms import TextField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class EnvironmentForm(Form):
    name = TextField('name', validators=[DataRequired()])
    sort_order = IntegerField('sort_order', validators=[NumberRange(min=0, max=50)])
    execute_path = TextField('execute_path', validators=[DataRequired()])

    def validate_execute_path(form, field):
        if field.data and (not os.path.exists(field.data)):
            raise ValidationError('path {0} not found.'.format(field.data))
