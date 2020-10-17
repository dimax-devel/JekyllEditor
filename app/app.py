# -*- coding: utf-8 -*-
@app.route('/')
def index():
    return 'hello, world'

if __name__ == '__main__':
    app.run()
