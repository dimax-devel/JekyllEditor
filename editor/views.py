# -*- coding: utf-8 -*-
import os
import json
import requests
from editor import app
from flask import redirect, url_for, render_template, session, request
from flask_github import GitHub
from datetime import datetime, timedelta, timezone
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
        return render_template('edit.html', uname=user_json['login'], repos=[d.get('name') for d in repo_json])

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
    try:
        input = request.form
        uname = str(input['user-name'])
        token = str(input['auth-token'])
        repo = str(input['select-repo'])
        title = str(input['title'])
        categories = str(input['categories'])
        post_contents = str(input['post-contents'])
        jst = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(jst)
        ref_object_sha = http_request('GET', '/repos/{0}/{1}/git/refs/heads/master'.format(uname, repo), token)['object']['sha']
        commit_json = http_request('GET', '/repos/{0}/{1}/git/commits/{2}'.format(uname, repo, ref_object_sha), token)
        commit_sha = commit_json['sha']
        commit_tree_sha = commit_json['tree']['sha']
        blob_result = http_request('POST', '/repos/{0}/{1}/git/blobs'.format(uname, repo), token, {'content':'---\nlayout: post\ntitle: "{0}"\ndate: {1:%Y/%m/%d %H:%M:%S} +0900\ncategories: {2}\n---\n\n{3}'.format(title, now, categories, post_contents)})
        blob_sha = blob_result['sha']
        tree_sha = http_request('POST', '/repos/{0}/{1}/git/trees'.format(uname, repo), token, {'base_tree':commit_tree_sha, 'tree':[{'path':'_posts/{0:%Y-%m-%d-%H%M%S}.md'.format(now), 'mode':'100644', 'type':'blob', 'sha':blob_sha}]})['sha']
        new_commit_sha = http_request('POST', '/repos/{0}/{1}/git/commits'.format(uname, repo), token, {'message':'new post: {0:%Y/%m/%d %H:%M:%S}'.format(now), 'parents':[commit_sha], 'tree':tree_sha})['sha']
        res = http_request('PATCH', '/repos/{0}/{1}/git/refs/heads/master'.format(uname, repo), token, {'sha':new_commit_sha})
        return redirect(url_for('posted'))
    except KeyError as instance:
        print(instance)
        return redirect(url_for('error'))

@app.route('/posted')
def posted():
    return render_template('posted.html', message='Posted!')

@app.route('/error')
def error():
    return render_template('posted.html', message='Failed!')

def http_request(method, path, token, data=None):
    url = 'https://api.github.com{0}'.format(path)
    auth_header = {'Authorization': 'token {0}'.format(token)}
    if method == 'GET':
        print('GET {0}', url)
        res = requests.get(url, headers=auth_header)
    elif method == 'POST':
        print('POST {0}', url)
        res = requests.post(url, headers=auth_header, json=data)
    elif method == 'PATCH':
        print('PATCH {0}', url)
        res = requests.patch(url, headers=auth_header, json=data)
    else:
        return None
    print(url)
    print(res.status_code)
    print(res.text)
    return res.json()
