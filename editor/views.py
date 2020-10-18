# -*- coding: utf-8 -*-
import os
from editor import app
from flask import redirect, url_for, render_template
from flask_github import GitHub
github = GitHub(app)
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GIHTUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
print(os.environ['GITHUB_CLIENT_ID'])

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
    
