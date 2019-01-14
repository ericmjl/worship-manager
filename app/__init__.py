from flask import Flask, render_template, request, redirect
from .env import DB_URL
from .utils import get_lyrics
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from collections import defaultdict

# Start app
app = Flask(__name__)
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
    pdf_preview = db.Column(db.Text(), nullable=True)
    composer = db.Column(db.String(), nullable=True)

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
def view_all():
    """
    Master view for all songs in the database.

    :returns: Renders an HTML table of songs.
    """

    all_songs = Song.query.all()
    return render_template("songs.html.j2", all_songs=all_songs)


@app.route("/<int:id>")
def view(id):
    """
    Displays a page to view a particular song. The view page doubles up as the
    edit page as well.

    :param int id: The id of the song in the database.
    :returns: Renders the view page for a single song.
    """
    song = Song.query.filter_by(id=id).first()
    return render_template("song.html.j2", song=song)


@app.route("/add")
def new():
    """
    Sends us to a blank song.
    """
    # data = Song().to_dict()
    # id = song_db.insert(data)
    # song = song_db.get(id=id)
    return render_template("song.html.j2", song=song)


@app.route('/<int:id>/save', methods=['POST'])
def save(id):
    """
    Saves the song information to the database.
    """
    song = Song.query.get(id)
    song.name = request.form.get('name', None)
    song.copyright = request.form.get('copyright', None)
    song.lyrics = get_lyrics(request).to_dict()
    song.ccli = request.form.get('ccli', None)
    song.default_arrangement = request.form.get('default_arrangement', None)
    song.youtube = request.form.get('youtube', None)
    song.sheet_music = request.form.get('sheet_music', None)
    song.pdf_preview = request.form.get('pdf_preview', None)
    song.composer = request.form.get('composer', None)

    db.session.commit()
    return redirect('/')
