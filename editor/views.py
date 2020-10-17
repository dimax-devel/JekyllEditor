# -*- coding: utf-8 -*-
from editor import app

@app.route('/')
def index():
    return 'hello, world'
