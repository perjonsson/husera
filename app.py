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
from calendar import TimeEncoding, month_name, month_abbr, day_name, day_abbr
from sqlalchemy.orm import object_session
from sqlalchemy import or_, not_
from  sqlalchemy.sql.expression import func
from flask.ext.heroku import Heroku
from uuid import uuid4
from urlparse import urlparse, urljoin
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

class BooliHelper:

    callerId = "husera"
    timestamp = str(int(time.time()))
    unique = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
    hashstr = sha1(callerId+timestamp+"HBkjpeFRPFHBZxqqfnoegTJIzX4wr0P94pAowH6V"+unique).hexdigest()

    def listings(self, area):
        url = "/listings?q=%s&callerId=%s&time=%s&unique=%s&hash=%s&limit=10000" % (area, BooliHelper.callerId, BooliHelper.timestamp, BooliHelper.unique, BooliHelper.hashstr)
        connection = httplib.HTTPConnection("api.booli.se")
        connection.request("GET", url)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        if response.status != 200:
            print "fail"
        return json.loads(data)

    def sales_prices(self, area):
        url = "/sold?q=%s&callerId=%s&time=%s&unique=%s&hash=%s&limit=10000" % (area, BooliHelper.callerId, BooliHelper.timestamp, BooliHelper.unique, BooliHelper.hashstr)
        connection = httplib.HTTPConnection("api.booli.se")
        connection.request("GET", url)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        if response.status != 200:
            print "fail"
        return json.loads(data)


@app.route('/', methods=['GET', 'POST'])
def index():
    sales_prices=BooliHelper().sales_prices("södermalm")
    listings=BooliHelper().listings("nacka")
    return render_template('index.html', 
        sales_prices=sales_prices,
        listings=listings
        )

@app.template_filter('date')
def date_filter(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()

@app.template_filter('weekday')
def weekday_filter(date):
    return get_day_name(date.weekday())

@app.template_filter('month_and_year')
def month_and_year_filter(date):
    return get_month_name(date.month) + " " + date.strftime("%Y")

@app.template_filter('same_month_and_year')
def same_month_and_year_filter(date_one, date_two):
    return True if date_one.year == date_two.year and date_one.month == date_two.month else False

@app.template_filter('same_date')
def same_date(date_one, date_two):
    return True if date_one == date_two else False

def get_month_name(month_no, locale="sv_SE.UTF-8", short=False, lowercase=True):
    with TimeEncoding(locale) as encoding:
        s = month_abbr[month_no] if short else month_name[month_no]
        if encoding is not None:
            s = s.decode(encoding)
        if lowercase:
            return s.lower()
        else:
            return s

def get_day_name(day_no, locale="sv_SE.UTF-8", short=False, lowercase=True):
    with TimeEncoding(locale) as encoding:
        if short:
            s = day_abbr[day_no]
        else:
            s = day_name[day_no]
        if encoding is not None:
            s = s.decode(encoding)
        if lowercase:
            return s.lower()
        else:
            return s

if __name__ == '__main__':
    app.run()
