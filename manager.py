import os
import sys
#from celery import Celery
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
    
    if sys.argv[1] == "create":
        db.createDB()
    elif sys.argv[1] == 'add':
        for w in sys.argv[2:]:
            db.addWordsSearch(w)
    elif sys.argv[1] == 'runserver':
        app.run(debug=True)

    elif sys.argv[1] == 'run':
        UpworkProcess.run(headless=False)
    else:
        pass

    #elif sys.argv[1] == 'start':
    #    subprocess.Popen("celery -A manager.celery worker --beat --loglevel=info")
