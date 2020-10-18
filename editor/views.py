# -*- coding: utf-8 -*-
import os
from editor import app
from flask import redirect, url_for, render_template, session
from flask_github import GitHub
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
app.secret_key = os.urandom(16)
github = GitHub(app)

@app.route('/')
def index():
    if 'oath_token' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('edit.html')

@app.route('/login')
def login():
    return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
def authorized(oath_token):
    session['oath_token'] = oath_token
    return redirect(url_for('/'))
    
