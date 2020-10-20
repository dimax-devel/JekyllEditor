# -*- coding: utf-8 -*-
import os
from editor import app
from flask import redirect, url_for, render_template, session, request
from flask_github import GitHub
from datetime import datetime
app.config['GITHUB_CLIENT_ID'] = os.environ['GITHUB_CLIENT_ID']
app.config['GITHUB_CLIENT_SECRET'] = os.environ['GITHUB_CLIENT_SECRET']
app.secret_key = os.urandom(16)
github = GitHub(app)

@app.route('/')
def index():
    if 'oath_token' not in session:
        return redirect(url_for('login'))
    else:
        token = session['oath_token']
        user_json = github.raw_request('GET', 'https://api.github.com/user', access_token=token).json()
        repo_json = github.raw_request('GET', 'https://api.github.com/user/repos', access_token=token).json()
        session['uname'] = user_json['name']
        return render_template('edit.html', uname=user_json['name'], repos=[d.get('name') for d in repo_json])

@app.route('/login')
def login():
    return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
def authorized(oath_token):
    session['oath_token'] = oath_token
    return redirect(url_for('index'))
    
@app.route('/post', methods = ['POST'])
def post():
    input = request.form
    uname = session['uname']
    token = session['oath_token']
    repo = str(input["select-repo"])
    title = str(input["title"])
    categories = str(input["categories"])
    post_contents = str(input["post-contents"])
    ref_object_sha = github.raw_request('GET', 'https://api.github.com/repos/{0}/{1}/git/refs/heads/master'.format(uname, repo), access_token=token)['object']['sha']
    commit_json = github.raw_request('GET', 'https://api.github.com/repos/{0}/{1}/git/commits/{2}'.format(uname, repo, ref_object_sha), access_token=token)
    commit_sha = commit_json['sha']
    commit_tree_sha = commit_json['tree']['sha']
    blob_sha = github.raw_request('POST', 'https://api.github.com/repos/{0}/{1}/git/blobs'.format(uname, repo), access_token=token, kwargs={'headers':{'content':post_contents}})['sha']
    now = datetime.now()
    tree_sha = github.raw_request('POST', 'https://api.github.com/repos/{0}/{1}/git/trees', access_token=token, kwargs={'headers':{'base_tree':commit_tree_sha, 'tree':{'path':'_post/{0:%Y%m%d%H%M%S}.md'.format(now), 'mode':'100644', 'type':'blob', 'sha':blob_sha}}})
    new_commit_sha = github.raw_request('POST', 'https://api.github.com/repos/{0}/{1}/git/commits'.format(uname, repo), access_token=token, kwargs={'headers':{'message':'new post:{0:%Y/%m/%d %H:%M:%S}'.format(now), 'parents':[commit_sha], 'tree':tree_sha}})
    status = github.raw_request('PATCH', 'https://api.github.com/repos/{0}/{1}/git/refs/heads/master'.format(uname, repo), access_token=token, kwargs={'headers':{'sha':new_commit_sha}})
    return redirect(url_for('posted'), sts=status)

@app.route('/posted')
def posted(sts):
    return render_template('posted.html', status=sts)
