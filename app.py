import json
import os
import os.path as osp

from app.datamodels import Song

from app.utils import (allowed_file, clean_song_arrangement, search_songs_db,
                       update_song_info)

from flask import (Flask, flash, redirect, render_template,
                   request, send_from_directory)
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb

from hanziconv import HanziConv

from tinydb import TinyDB
from tinydb.operations import delete

import yaml

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'files/'

Breadcrumbs(app=app)

song_db = TinyDB('song.db')
coworker_db = TinyDB('coworker.db')
calendar_db = TinyDB('calendar.db')

hzc = HanziConv()
convert = hzc.toTraditional


# Keep a list of song keys
song_datamodel = list(Song().to_dict().keys())


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/songs', methods=['POST'])
@app.route('/songs')  # there are two paths to here.
def view_songs():
    all_songs = song_db.all()
    return render_template('songs.html', all_songs=all_songs)


@app.route('/songs/search', methods=['POST'])
@app.route('/songs/search')
def search_songs():
    term = convert(request.form['search'])
    # Perform a search of all key/value pairs in the database.
    filtered_songs = search_songs_db(term, song_db)
    return render_template('songs.html', all_songs=filtered_songs, term=term)


@app.route('/songs/<int:eid>/view')
@app.route('/songs/<int:eid>/edit')
@app.route('/songs/<int:eid>')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/add', methods=['POST'])
@app.route('/songs/add')
def new_song():
    data = Song().to_dict()
    eid = song_db.insert(data)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/save', methods=['POST'])
def save_song(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    return redirect('/songs')


@app.route('/songs/<int:eid>/update', methods=['POST'])
def update_song(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/remove', methods=['POST'])
def delete_song(eid):
    song_db.remove(eids=[eid])
    return redirect('/songs')


@app.route('/songs/<int:eid>/add_lyrics_section', methods=['POST'])
def add_lyrics_section(eid):
    """
    Adds a lyrics section to the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    sect_ct = len(song['lyrics']) + 1
    song['lyrics'][f'section-{sect_ct}'] = f'lyrics-{sect_ct}'
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db,
                     exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/sheet_music/upload', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/upload')
def upload_sheet_music(eid):
    """
    Uploads a PDF for the song.
    """
    song = song_db.get(eid=eid)
    if 'file-upload' not in request.files:
        flash('No file part')
        return render_template('song.html', song=song)
    f = request.files['file-upload']

    if f.filename == '':
        flash('No selected file')
        return render_template('song.html', song=song)

    if f and allowed_file(f.filename):
        fname = f'{song["name"]}-{song["copyright"]}.pdf'
        fname = osp.join(app.config['UPLOAD_FOLDER'], fname)
        f.save(fname)
        song_db.update({'sheet_music': fname}, eids=[eid])
        song = song_db.get(eid=eid)
        return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/sheet_music/download', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/download')
def download_sheet_music(eid):
    """
    Returns the sheet music to be downloaded.
    """
    song = song_db.get(eid=eid)
    return send_from_directory(song['sheet_music'])


@app.route('/songs/<int:eid>/sheet_music/delete', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/delete')
def delete_sheet_music(eid):
    song = song_db.get(eid=eid)
    os.system(f'rm {song["sheet_music"]}')
    song_db.update(delete('sheet_music'), eids=[eid])
    song = song_db.get(eid=eid)
    return render_template("song.html", song=song)


@app.route('/songs/clean', methods=['POST'])
@app.route('/songs/clean')
def clean_songs_database():
    """
    Cleans every entry in the songs database to match the Songs datamodel.
    """
    all_songs = song_db.all()
    for s in all_songs:
        for k, v in s.items():
            if k == 'id':
                pass
            elif k not in song_datamodel:
                song_db.update(delete(k), eids=[s.eid])
    return redirect('/songs')


@app.route('/songs/export', methods=['POST'])
@app.route('/songs/export')
def export_songs_database():
    """
    Exports the songs database as a YAML file.
    """
    with open('song.db', 'r+') as f:
        data = json.load(f)
    return yaml.dump(data, default_flow_style=False)


# @app.route('/songs/<int:eid>/export/<fmt>', methods=['POST'])
# @app.route('/songs/<int:eid>/export/<fmt>')
# def export_song_lyrics(eid, fmt):
#     """
#     Exports a song's lyrics as a string.
#     """
#     song = song_db.get(eid=eid)
#     arrangement = clean_song_arrangement(
#         arrangement=song['default_arrangement'], song_data=song)
#     arr_lyrics = arrange_lyrics(arrangement=arrangement, song_data=song)
#
#     if fmt == 'txt':
#         response = make_response(arr_lyrics)
#         response.headers["Content-Disposition"] = "attachment; filename=lyrics.txt"  # noqa
#
#         return response
#     elif fmt == 'pptx':
#         make_lyrics_presentation(song)
#         return send_from_directory('tmp/slides.pptx')


@app.route('/songs/<int:eid>/slides', methods=['POST'])
@app.route('/songs/<int:eid>/slides')
def view_song_slides(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    arrangement = clean_song_arrangement(song['default_arrangement'], song)
    return render_template('slides.html', song=song, arrangement=arrangement,
                           eid=eid)


@app.route('/coworkers', methods=['POST'])
def view_coworkers():
    return render_template('coworkers.html')


@app.route('/coworkers/<int:id>/view', methods=['POST'])
def view_coworker(id):
    pass


@app.route('/coworkers/<int:id>/edit', methods=['POST'])
def edit_coworker(id):
    pass


@app.route('/test/<int:eid>/slides')
def testing_slides(eid):
    """
    Created 3 August 2017. Used to test slide generation functionality. Not
    intended to be used for production. DO NOT MAKE UI ELEMENTS THAT RELY ON
    THIS! Feel free to delete at later date.
    """
    song = song_db.get(eid=eid)
    arrangement = clean_song_arrangement(song['default_arrangement'], song)
    return render_template('slides.html', song=song, arrangement=arrangement)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True, port=5678)
