import os
from flask import Flask, jsonify, redirect
from flask import render_template

from browser import UpworkProcess
import db

app = Flask(__name__, static_folder="frontend/dist", static_url_path="", template_folder="frontend/dist")

@app.route('/')
def index():
    return redirect('index.html')


@app.route('/api/v1/posts')
def api():
    posts = db.getAllPosts()
    return jsonify(posts)



if __name__ ==  '__main__':
    app.run(debug=True)
