# -*- coding: utf-8 -*-
from editor import app
from flask import redirect, url_for, render_template
from flask_github import GITHUB
# github = GitHub(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')
