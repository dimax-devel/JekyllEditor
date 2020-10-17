# -*- coding: utf-8 -*-
from app import app

@app.route('/')
def index():
    return 'hello, world'

if __name__ == '__main__':
    app.run()
