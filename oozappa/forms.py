# -*- coding:utf8 -*-
import os
from flask_wtf import Form
from wtforms.widgets import TextArea, HiddenInput
from wtforms import TextField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange, ValidationError


class EnvironmentForm(Form):
    name = TextField('name', validators=[DataRequired()])
    sort_order = IntegerField('sort_order', validators=[NumberRange(min=0, max=50)])
    execute_path = TextField('execute_path', validators=[DataRequired()])

    def validate_execute_path(form, field):
        if field.data and (not os.path.exists(field.data)):
            raise ValidationError('path {0} not found.'.format(field.data))


class JobForm(Form):
    name = TextField('name', validators=[DataRequired()])
    description = TextField('description', widget=TextArea(), validators=[DataRequired()])
    environment_id = IntegerField('environment_id', widget=HiddenInput(), validators=[DataRequired()])
    tasks = TextField('tasks',
        #widget=HiddenInput,
        validators=[DataRequired()])


class JobSetForm(Form):
    title = TextField('title', validators=[DataRequired()])
    description = TextField('description', widget=TextArea(), validators=[DataRequired()])
    job_id = SelectMultipleField(u'Job', coerce=int, validators=[DataRequired()])
