# -*- coding: utf-8 -*-
from editor import app
from flask import redirect, url_for, render_template
from flask_github import GitHub
github = GitHub(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return github.authorize()
#    return 'test'

@app.route('/github-callback')
@github.authorized_handler
def authorized(oath_token):
    return render_template('login.html')
    
