# -*- coding: utf-8 -*-

import os, sys, datetime, locale
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, 'app'))
from fetcher import *
from classes import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

url = 'http://jesion.pl'


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LottoForm(FlaskForm):
    handNumbers = StringField('Podaj swoje typy (np. 2,9,12,19,32,48; itd.):', validators=[DataRequired()])
    date = DateField('Data losowania:', format='%Y-%m-%d')
    submit = SubmitField(u'Sprawdź wyniki')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home Page
    """
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/learn')
def learn():
    url = request.args.get('q')
    if url:
        fetchedData = get_links(url)
    else:
        fetchedData = ''
    return render_template('learn_template.html', url = url, fetchedData = fetchedData)

@app.route('/movies')
def movies():
    url = request.args.get('q')
    if url:
        fetchedData = get_movies(url)
    else:
        fetchedData = ''
    return render_template('learn_template.html', url = url, fetchedData = fetchedData)

@app.route('/lotto', methods=['GET', 'POST'])
def lotto():
    form = LottoForm()
    data = 'to sa dane tratarata'
    if form.validate_on_submit():
        session['date'] = form.date.data
        session['handNumbers'] = form.handNumbers.data
        return redirect(url_for('wyniki'))
    return render_template('lotto_home.html', data=data, form=form)

@app.route('/lotto-wyniki')
def wyniki():
    date = datetime.datetime.strptime(session.get('date'), '%a, %d %b %Y %X %Z').strftime('%Y-%m-%d')
    handNumbers_temp = session.get('handNumbers').split(';')
    handNumbers = []
    for pos in handNumbers_temp:
        handNumbers.append(map(int, pos.split(',')))
    # sprawdzanie wyników w różnych kuponach
    template_data = []
    for kupon in handNumbers:
        dic_temp = {}
        wyniki = lotto.check_numbers(kupon, date)
        dic_temp['wyniki'] = wyniki
        dic_temp['results'] = lotto.get_results()[0]
        dic_temp['handNumbers'] = kupon
        dic_temp['results_format'] = lotto.drawResult(lotto.get_results()[0], wyniki)
        template_data.append(dic_temp)

    return render_template('wyniki.html', date=date, template_data=template_data)


if __name__ == '__main__':
    db.create_all()
    lotto = Lotto()
    fetchedData = get_links(url)
    manager.run()