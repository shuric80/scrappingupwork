import os
import sys
#from celery import Celery
import argparse
from flask import Flask, jsonify, redirect
from flask import render_template
#from celery import Celery
#import subprocess

from browser import UpworkProcess
import db

#app = Flask(__name__, static_folder="frontend/dist", static_url_path="", template_folder="frontend/dist")
app = Flask(__name__)
#celery = Celery(__name__, backend='amqp', broker='amqp://')
#celery.config_from_object('config')

parser = argparse.ArgumentParser(description='Process scrape upword site')

parser.add_argument('cmd', action='store', nargs='+')
parser.add_argument('--add', '-a', nargs='+', action='store', help='Append new words')
parser.add_argument('--headless', action='store_false', help='Browser set headless')
parser.add_argument('--login', '-l', type=str, help='User login', action='store')
parser.add_argument('--password', '-p', type=str, help='User password', action='store')
parser.add_argument('--debug', '-d', action='store_true', help='Debug mode')
parser.add_argument('--noname', '-u', action='store_true', help='Noname mode')

@app.route('/')
def index():
    posts = db.getAllPosts()
    return render_template('index.html', posts = posts)


@app.route('/api/v1/posts')
def api_posts_all():
    posts = db.getAllPosts()
    return jsonify(posts)

@app.route('/api/v1/words')
def api_words_all():
    words = db.getWordsSearch()
    return jsonify(words)


#@celery.task
#def periodic_task():
#    UpworkProcess.run()


if __name__ ==  '__main__':
    options = parser.parse_args()
    if 'create' in options.cmd:
        db.createDB()

    elif 'add' in options.cmd:
        for word in options.cmd[1:]:
            db.addWordsSearch(word)

    elif 'runserver' in options.cmd:
        app.run(debug=options.debug)

    elif 'run' in options.cmd:
        d_params = dict(
            headless=options.headless,
            debug=options.debug,
            login=options.login,
            password=options.password,
            noname=options.noname
        )

        UpworkProcess.run(d_params)
    #elif sys.argv[1] == 'start':
    #    subprocess.Popen("celery -A manager.celery worker --beat --loglevel=info")
