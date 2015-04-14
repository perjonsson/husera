# -*- coding: utf-8 -*-
import os, urllib, hashlib, string, sendgrid, re, base64, httplib, time, random, json
from sendgrid import SendGridError, SendGridClientError, SendGridServerError
from datetime import datetime, date, timedelta
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory, session, abort, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func, select
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, BooleanField, TextField, PasswordField, TextAreaField, SelectField, FileField, HiddenField, DateField, IntegerField, DateTimeField, validators, ValidationError
from wtforms.ext.sqlalchemy.orm import QuerySelectField, QuerySelectMultipleField
from slugify import slugify
from flask.ext.login import LoginManager, current_user, current_app, login_required, login_user, logout_user, confirm_login, fresh_login_required
from flask_oauth import OAuth, OAuthException
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import object_session
from sqlalchemy import or_, not_
from  sqlalchemy.sql.expression import func
from flask.ext.heroku import Heroku
from uuid import uuid4
from urlparse import urlparse, urljoin
from random import *
from hashlib import sha1 

app = Flask(__name__)

# Conf
app.config.from_pyfile('config.cfg')
# Prod
if 'DATABASE_URL' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# Dev
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/booli'

# Init events
heroku = Heroku(app)
db = SQLAlchemy(app)
# Init login manager

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', sodermalm=sales_prices("sodermalm"))


def sales_prices(area):
    callerId = "husera"
    timestamp = str(int(time.time()))
    unique = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
    hashstr = sha1(callerId+timestamp+"HBkjpeFRPFHBZxqqfnoegTJIzX4wr0P94pAowH6V"+unique).hexdigest()
     
    url = "/listings?q=%s&callerId="+callerId+"&time="+timestamp+"&unique="+unique+"&hash="+hashstr % (area)
     
    connection = httplib.HTTPConnection("api.booli.se")
    connection.request("GET", url)
    response = connection.getresponse()
    data = response.read()
    connection.close()
     
    if response.status != 200:
        print "fail"
     
    return data


if __name__ == '__main__':
    app.run()