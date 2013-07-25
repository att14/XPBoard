#!/usr/bin/env python
import os

from flask import Flask, url_for


app = Flask(__name__)
app.jinja_env.variable_start_string = '<%'
app.jinja_env.variable_end_string = '%>'
app.jinja_env.globals['get_static_url'] = lambda filename: url_for(
    'static',
    filename=filename
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///{app_dir}/database.db'.format(
        app_dir=os.path.abspath(os.path.dirname(__file__))
    )
)
