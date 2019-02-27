from flask import Flask, render_template, request, redirect
from .env import DB_URL
from .utils import get_lyrics, clean_arrangement
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
import pinyin

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
    pinyin = db.Column(db.String(), nullable=True)

    def _add_default_arrangement(self, default_arrangement):
        # Firstly, we make sure that every element in default_arrangement is
        # a key in the lyrics' sections.
        if default_arrangement:
            for section in default_arrangement:
                assert section in self.lyrics.sections.keys(), f"{section} not specified"

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


@app.route("/<int:id>/export")
def export(id):
    """
    Exports the song lyrics to plain text that gets rendered inside a text box.

    :param int id: The id of the song in the database.
    :returns: Renders the view page for the lyrics of a song.
    """
    song = Song.query.filter_by(id=id).first()


@app.route("/add")
def new():
    """
    Sends us to a blank song.
    """
    song = Song()
    song.id = len(Song.query.all())
    song.name = "Name"
    song.copyright = None
    song.lyrics = {'section-1': 'section-1', 'section-2': 'section-2'}
    song.ccli = None
    song.default_arrangement = None
    song.youtube = None
    song.sheet_music = None
    song.pdf_preview = None
    song.composer = None
    song.pinyin = None
    db.session.add(song)
    db.session.commit()
    return redirect(f'/{song.id}')


def save_song(id, request):
    """
    Refactored out of `save()` to support both saving and updating.
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
    song.pinyin = pinyin.get(song.name, format="strip", delimiter=" ")
    db.session.commit()


@app.route('/<int:id>/save', methods=['POST'])
def save(id):
    """
    Saves the song information to the database.
    """
    save_song(id, request)
    return redirect('/')


@app.route('/<int:id>/update', methods=['POST'])
def update(id):
    """
    Update song and return to same page.

    Note: essentially just a different redirect compared to `save(id)`.
    """
    save_song(id, request)
    return redirect(f"/{id}")


@app.route('/<int:id>/slides')
def slides(id):
    """
    Render slides using revealjs.
    """
    song = Song.query.filter_by(id=id).first()
    arrangement = clean_arrangement(song.default_arrangement)
    return render_template(
        "slides_single_song.html.j2", song=song, arrangement=arrangement, id=id
    )


@app.route('/<int:id>/add_lyrics_section')
def add_lyrics_section(id):
    song = Song.query.filter_by(id=id).first()
    count = len(song.lyrics) + 1
    song.lyrics.update({f'section-{count}':f'section-{count}'})
    print(song.lyrics, count)
    flag_modified(song, "lyrics")
    db.session.merge(song)
    db.session.commit()
    return redirect(f"/{id}")


@app.route('/<int:id>/remove_lyrics_section/<int:section_id>')
def remove_lyrics_section(id, section_id):
    song = Song.query.filter_by(id=id).first()
    del song.lyrics[f"section-{section_id}"]
    # song.lyrics.pop(section_id, None)
    flag_modified(song, "lyrics")
    db.session.commit()
    return redirect(f"/{id}")
