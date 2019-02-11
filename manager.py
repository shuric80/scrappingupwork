from flask import Flask, jsonify
from flask import render_template

import db

app = Flask(__name__)

@app.route('/')
def mainPage():
    posts = db.getAllPosts()
    return render_template('index.html', posts=posts)


if __name__ ==  '__main__':
    app.run(debug=True)
