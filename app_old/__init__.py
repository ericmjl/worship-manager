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
from sqlalchemy.dialects.postgresql import JSON


app = Flask(__name__)
app.register_blueprint(songs.mod)
# Register other blueprints later.

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
db = SQLAlchemy(app)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    copyright = db.Column(db.String(), nullable=True)
    lyrics = db.Column(JSON, nullable=True)
    ccli = db.Column(db.String(), nullable=True)
    default_arrangement = db.Column(db.String(), nullable=True)
    youtube = db.Column(db.String(), nullable=True)
    sheet_music = db.Column(db.String(), nullable=True)
    composer = db.Column(db.String(), nullable=True)

    def _add_lyrics(self, lyrics=None):
        """
        Adds lyrics to the Song object.

        :param lyrics: A Lyrics object
        """
        if lyrics:
            assert isinstance(lyrics, Lyrics)
            self.lyrics = lyrics

    def _add_default_arrangement(self, default_arrangement):
        # Firstly, we make sure that every element in default_arrangement is
        # a key in the lyrics' sections.
        if default_arrangement:
            for section in default_arrangement:
                assert (
                    section in self.lyrics.sections.keys()
                ), f"{section} not specified"

            # Now, we allow the default arrangement to be set.
            self.default_arrangement = default_arrangement


@app.route("/")
def home():
    return render_template("index.html.j2")
