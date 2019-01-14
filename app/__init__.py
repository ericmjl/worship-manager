import os
from pathlib import Path

import boto3
import psycopg2
from flask import Flask, render_template
from hanziconv import HanziConv
from tinydb import TinyDB

from .views import songs
from .config import DB_URL
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.register_blueprint(songs.mod)
# Register other blueprints later.

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("index.html.j2")
