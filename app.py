import json

from datamodels import Song

from flask import (Flask, make_response, redirect, render_template, request,
                   send_file)

from tinydb import TinyDB
from tinydb.operations import delete

from utils import (arrange_lyrics, clean_song_arrangement,
                   make_lyrics_presentation, update_song_info)

import yaml


UPLOAD_FOLDER = 'files/'
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
song_db = TinyDB('song.db')
coworker_db = TinyDB('coworker.db')
calendar_db = TinyDB('calendar.db')


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


@app.route('/songs/<int:eid>/view')
@app.route('/songs/<int:eid>')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/add', methods=['POST'])
@app.route('/songs/add')
def new_song():
    data = Song().to_dict()
    eid = song_db.insert(data)
    print(eid)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/save', methods=['POST'])
@app.route('/songs/<int:eid>/save')
def save_song(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    return redirect('/songs')


@app.route('/songs/<int:eid>/remove', methods=['POST'])
def delete_song(eid):
    song_db.remove(eids=[eid])
    return redirect('/songs')


@app.route('/songs/<int:eid>/edit')
def edit_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/add_lyrics_section', methods=['POST'])
def add_lyrics_section(eid):
    """
    Adds a lyrics section to the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=True)


@app.route('/songs/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db,
                     exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


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


@app.route('/songs/<int:eid>/export/<fmt>', methods=['POST'])
@app.route('/songs/<int:eid>/export/<fmt>')
def export_song_lyrics(eid, fmt):
    """
    Exports a song's lyrics as a string.
    """
    song = song_db.get(eid=eid)
    arrangement = clean_song_arrangement(
        arrangement=song['default_arrangement'], song_data=song)
    arr_lyrics = arrange_lyrics(arrangement=arrangement, song_data=song)

    if fmt == 'txt':
        response = make_response(arr_lyrics)
        response.headers["Content-Disposition"] = "attachment; filename=lyrics.txt"  # noqa

        return response
    elif fmt == 'pptx':
        make_lyrics_presentation(song)
        return send_file('tmp/slides.pptx')


@app.route('/coworkers', methods=['POST'])
def view_coworkers():
    return render_template('coworkers.html')


@app.route('/coworkers/<int:id>/view', methods=['POST'])
def view_coworker(id):
    pass


@app.route('/coworkers/<int:id>/edit', methods=['POST'])
def edit_coworker(id):
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5678)
