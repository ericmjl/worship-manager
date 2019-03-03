from flask import Flask, render_template, request, redirect, flash, send_file
from .env import DB_URL
from .utils import get_lyrics, clean_arrangement, allowed_file
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from pathlib import Path
from hanziconv import HanziConv

import pinyin
import uuid
import boto3
import os
import logging as log

# Start app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
db = SQLAlchemy(app)
convert = HanziConv.toTraditional


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
                assert section in self.lyrics.sections.keys(), \
                    f"{section} not specified"

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

    We do not save the song sheet, because it should already be saved after
    uploading the sheet music to s3.
    """
    song = Song.query.get(id)
    song.name = convert(request.form.get('name', ''))
    song.copyright = convert(request.form.get('copyright', ''))
    song.lyrics = get_lyrics(request).to_dict()
    song.ccli = convert(request.form.get('ccli', ''))
    song.default_arrangement = convert(request.form.get('default_arrangement', ''))
    song.youtube = request.form.get('youtube', '')
    song.composer = convert(request.form.get('composer', ''))
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
@app.route('/<int:id>/slides', methods=['POST'])
def slides(id):
    """
    Render slides using revealjs.
    """
    if request.method == 'POST':
        save_song(id, request)
    song = Song.query.get(id)
    arrangement = clean_arrangement(song.default_arrangement)
    return render_template(
        "slides_single_song.html.j2", song=song, arrangement=arrangement, id=id
    )


@app.route('/<int:id>/add_lyrics_section', methods=['POST'])
def add_lyrics_section(id):
    # Update song
    save_song(id, request)
    song = Song.query.get(id)
    count = len(song.lyrics) + 1
    song.lyrics.update({f'section-{count}': f'section-{count}'})
    flag_modified(song, "lyrics")

    # Commit to database
    db.session.merge(song)
    db.session.commit()

    # Redirect
    return redirect(f"/{id}")


@app.route(
    '/<int:id>/remove_lyrics_section/<int:section_id>',
    methods=['POST']
)
def remove_lyrics_section(id, section_id):
    # Update song
    save_song(id, request)
    song = Song.query.get(id)
    del song.lyrics[f"section-{section_id}"]
    flag_modified(song, "lyrics")

    # Commit to database
    db.session.merge(song)
    db.session.commit()

    # Redirect
    return redirect(f"/{id}")


@app.route("/<int:id>/sheet_music/upload", methods=["POST"])
def upload_sheet_music(id):
    """
    Uploads a PDF of the sheet music for the song.

    :param id: The id of the song for which a sheet music is to be attached.
    :type id: int

    .. note:: The only acceptable upload formats are indicated in
              `app.utils.ALLOWED_EXTENSIONS`.

    :returns: The view page for the song.
    """
    log.debug('User wants to upload a song sheet.')
    if "file-upload" not in request.files:
        flash("No file part")
        return redirect(f"/songs/{id}")
    log.debug('Getting file from for.')
    f = request.files["file-upload"]

    if f.filename == "":
        flash("No selected file")
        return redirect(f"/songs/{id}")

    if f and allowed_file(f.filename):
        # Compute the song filename.
        fname = f"{str(uuid.uuid4())}.pdf"
        # Save the file to disk temporarily.
        log.debug('Saving to disk temporarily')
        fpath = str(f'/tmp/{fname}')
        f.save(fpath)

        log.debug('Uploading to s3')
        # Save the file to S3
        s3ul(fpath, fname)
        # Update the song database
        log.debug('Updating song database.')
        song = Song.query.get(id)
        song.sheet_music = fname
        flag_modified(song, "sheet_music")
        db.session.merge(song)
        db.session.commit()

        return redirect(f"/{id}")


@app.route('/<int:id>/sheet_music/download')
def download_sheet_music(id):
    """
    Returns the sheet music to be downloaded.

    :param id: The id of the song.
    :type id: int

    :returns: The song sheet PDF.
    """
    song = Song.query.get(id)
    fname = song.sheet_music
    # Use s3dl utility function to conditionally download file.
    s3dl(fname)

    # Change the name of the file so that it is easier to read.
    new_fname = f'{song.name}-{song.composer}-{song.copyright}.pdf'
    os.system(f"cp /tmp/{fname} /tmp/{new_fname}")

    # Return the file.
    return send_file(f"/tmp/{new_fname}", as_attachment=True)


# Below are a bunch of s3-specific utility functions. I may refactor them
# out at a later date.


def s3bucket():
    s3 = boto3.resource("s3")
    bucket = os.environ["S3_BUCKET_NAME"]
    return s3.Bucket(bucket)


def s3dl(fname):
    """
    Downloads a file from S3. Does this conditionally; if the file already
    exists, then we do not download it.

    Does not return anything
    """
    pathstr = f"/tmp/{fname}"
    if not Path(pathstr).exists():
        s3bucket().download_file(fname, f"/tmp/{fname}")


def s3ul(fpath, fname):
    """
    Uploads a file to S3.
    """
    s3bucket().upload_file(fpath, fname, ExtraArgs={"ACL": "public-read"})


def s3del(fname):
    """
    Deletes a file from s3.
    """
    s3bucket().delete_objects(Delete={"Objects": [{"Key": fname}]})


def s3rename(old, new):
    """
    Renames a file on s3.
    """
    s3dl(old)
    s3ul(f"/tmp/{old}", new)
    s3del(old)
