import json

import os.path as osp

from flask import (Blueprint, flash, redirect, render_template, request,
                   send_file)

from hanziconv import HanziConv

from tinydb import TinyDB
from tinydb.operations import delete

import yaml

from ..datamodels import Song

from ..utils import (allowed_file, clean_arrangement, search_songs_db,
                     update_song_info)


# from .utils import makedir

mod = Blueprint('songs', __name__, url_prefix='/songs')


data_folder = 'data/'
db_folder = osp.join(data_folder, 'database')
upload_folder = osp.join(data_folder, 'files')  # upload folder

# Connect to the database
song_db = TinyDB(osp.join(db_folder, 'song.db'))

# Other setup
hzc = HanziConv()
convert = hzc.toTraditional

song_datamodel = list(Song().to_dict().keys())


@mod.route('/')
def view_all():
    """
    Master view for all songs in the database.

    :returns: Renders an HTML table of songs.
    """
    all_songs = song_db.all()
    return render_template('songs.html.j2', all_songs=all_songs)


@mod.route('/search', methods=['POST'])
@mod.route('/search')
@mod.route('/search/<term>')
def search(term=None):
    """
    Search function for songs in the database. Performs a strict substring
    search by calling on `app.utils.search_songs_db`.

    :param term: The search term.
    :type term: `str`

    :returns: Renders an HTML table of songs.
    """
    if term:
        pass
    elif request.form['search']:
        term = convert(request.form['search'])
    # Perform a search of all key/value pairs in the database.
    filtered_songs = search_songs_db(term, song_db)
    return render_template('songs.html.j2',
                           all_songs=filtered_songs,
                           term=term)


@mod.route('/<int:eid>/view')
@mod.route('/<int:eid>/edit')
@mod.route('/<int:eid>')
def view(eid):
    """
    Displays a page to view a particular song. The view page doubles up as the
    edit page as well.

    :param eid: The eid of the song in the database.
    :type eid: `int`

    :returns: Renders the view page for a single song.
    """
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@mod.route('/add', methods=['POST'])
@mod.route('/add')
def new():
    """
    Adds a new song to the database. To ensure that the song is entered into
    the database, we first create the song in the db, and then return the empty
    information to Jinja, including the `eid`. In this way, we are guaranteed
    an `eid` for the `/save` function (below).

    :returns: Renders the view page for a new song, but under the url path
              /add.
    """
    data = Song().to_dict()
    eid = song_db.insert(data)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@mod.route('/<int:eid>/save', methods=['POST'])
def save(eid):
    """
    Saves the song to the database. This function calls on the
    `app.utils.update_song_info` function.

    :param eid: The eid of the song to be saved.
    :type eid: `int`

    :returns: Redirects to the `/songs/` page (master table).
    """
    update_song_info(request=request, eid=eid, song_db=song_db)
    return redirect('/songs/')


@mod.route('/<int:eid>/update', methods=['POST'])
def update(eid):
    """
    Updates the song information to the database. In contrast to `save(eid)`,
    this function will come back to the song page.

    :param eid: The eid of the song to be updated.
    :type eid: `int`

    :returns: Renders the view page for the song that was updated.
    """
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@mod.route('/<int:eid>/remove', methods=['POST'])
def remove(eid):
    """
    Removes a song from the database.

    :param eid: The eid of the song to be removed.
    :type eid: `int`

    :returns: Redirects to the `/songs/` page (master table).
    """
    song_db.remove(eids=[eid])
    return redirect('/songs/')


@mod.route('/<int:eid>/add_lyrics_section', methods=['POST'])
def add_lyrics_section(eid):
    """
    Adds a lyrics section to the song.

    :param eid: The eid of the song to add a lyrics section to.
    :type eid: `int`

    :returns: Renders the view page for a song, but with an added lyrics
              section to the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    sect_ct = len(song['lyrics']) + 1
    # print(sect_ct)
    song['lyrics'][f'section-{sect_ct}'] = f'lyrics-{sect_ct}'
    return render_template('song.html.j2', song=song)


@mod.route('/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.

    :param eid: The eid of the song to remove a section from.
    :type eid: `int`

    :param section_id: The section ID to be removed.
    :type section_id: `str`

    .. note:: `section_id` comes from the HTML form that is submitted. It
              should be of the form `section-1` or `section-2` (for example).

    :returns: Renders the view page for the song, but with the indicated
              section removed.
    """
    update_song_info(request=request, eid=eid, song_db=song_db,
                     exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@mod.route('/<int:eid>/sheet_music/upload', methods=['POST'])
@mod.route('/<int:eid>/sheet_music/upload')
def upload_sheet_music(eid):
    """
    Uploads a PDF of the sheet music for the song.

    :param eid: The eid of the song for which a sheet music is to be attached.
    :type eid: `int`

    .. note:: The only acceptable upload formats are indicated in
              `app.utils.ALLOWED_EXTENSIONS`.

    :returns: The view page for the song.
    """
    song = song_db.get(eid=eid)
    if 'file-upload' not in request.files:
        flash('No file part')
        return render_template('song.html.j2', song=song)
    f = request.files['file-upload']

    if f.filename == '':
        flash('No selected file')
        return render_template('song.html.j2', song=song)

    if f and allowed_file(f.filename):
        fname = f'{song["name"]}-{song["copyright"]}.pdf'
        f.save(osp.join(upload_folder, fname))
        song_db.update({'sheet_music': fname}, eids=[eid])
        song = song_db.get(eid=eid)
        return render_template('song.html.j2', song=song)


@mod.route('/<int:eid>/sheet_music/download', methods=['POST'])
@mod.route('/<int:eid>/sheet_music/download')
def download_sheet_music(eid):
    """
    Returns the sheet music to be downloaded.

    :param eid: The eid of the song.
    :type eid: `int`

    :returns: The song sheet PDF.

    .. note:: The path for sending the file is very hacky; assumes that `data/`
              is one directory above `app/__init__.py`. Could be brittle to
              changes in the future...
    """
    song = song_db.get(eid=eid)
    # return send_from_directory(upload_folder, filename=song['sheet_music'])
    return send_file(osp.join('..', upload_folder, song['sheet_music']))


@mod.route('/<int:eid>/sheet_music/delete', methods=['POST'])
@mod.route('/<int:eid>/sheet_music/delete')
def delete_sheet_music(eid):
    """
    Deletes the sheet music from the song.

    .. note:: The file on disk is not actually removed; only the file path
              recorded in the database is. This is an intentional choice during
              development, to prevent data losses from happening. Before going
              into production, this should be changed.

    .. todo:: Make sure to fix the problem indicated in the note above.

    :param eid: The eid of the song to remove sheet music from.
    """
    song = song_db.get(eid=eid)
    song_db.update(delete('sheet_music'), eids=[eid])
    song = song_db.get(eid=eid)
    return render_template("song.html.j2", song=song)


@mod.route('/clean', methods=['POST'])
@mod.route('/clean')
def clean_database():
    """
    Cleans every entry in the songs database to match the Songs datamodel.

    :returns: Renders the master songs page.
    """
    all_songs = song_db.all()
    for s in all_songs:
        for k, v in s.items():
            if k == 'id':
                pass
            elif k not in song_datamodel:
                song_db.update(delete(k), eids=[s.eid])
    return redirect('/songs/')


@mod.route('/export', methods=['POST'])
@mod.route('/export')
def export_database():
    """
    Exports the songs database as a YAML file.

    .. note:: We do a YAML dump because this makes it easier for humans to read
              compared to a JSON file without necessary whitespace.

    :returns: a YAML dump of the database.
    """
    with open('song.db', 'r+') as f:
        data = json.load(f)
    return yaml.dump(data, default_flow_style=False)


@mod.route('/<int:eid>/slides', methods=['POST'])
@mod.route('/<int:eid>/slides')
def view_slides(eid):
    """
    Creates `reveal.js` slides for the song of interest, using the default
    arrangement specified in the song's database entry.

    :param eid: The eid of the song to create slides for.
    :type eid: `int`

    :returns: Renders the HTML slides for that song.
    """
    song = song_db.get(eid=eid)
    arrangement = clean_arrangement(song['default_arrangement'])
    return render_template('slides_single_song.html.j2',
                           song=song,
                           arrangement=arrangement,
                           eid=eid)
