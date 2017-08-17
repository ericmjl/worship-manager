import json
import os
import os.path as osp

from app.datamodels import Coworker, Program, Song

from app.static import fellowships, genders, service

from app.utils import (allowed_file,
                       clean_song_arrangement, fill_program_information,
                       get_grouped_coworkers, makedir,
                       save_program_information,
                       search_coworkers_db, search_songs_db,
                       update_coworker_info, update_song_info)

from flask import (Flask, flash, redirect, render_template,
                   request, send_file)

# from flask_breadcrumbs import Breadcrumbs

from hanziconv import HanziConv

from tinydb import TinyDB
from tinydb.operations import delete

import yaml

app = Flask(__name__)
datafolder = 'data/'

app.config['UPLOAD_FOLDER'] = osp.join(datafolder,
                                       'files/')
makedir(app.config['UPLOAD_FOLDER'])

dbfolder = osp.join(datafolder, 'database')
makedir(dbfolder)

# Breadcrumbs(app=app)
song_db = TinyDB(osp.join(dbfolder, 'song.db'))
coworker_db = TinyDB(osp.join(dbfolder, 'coworker.db'))
calendar_db = TinyDB(osp.join(dbfolder, 'calendar.db'))
program_db = TinyDB(osp.join(dbfolder, 'program.db'))

hzc = HanziConv()
convert = hzc.toTraditional


# Keep a list of song keys
song_datamodel = list(Song().to_dict().keys())


@app.route('/')
def home():
    return render_template('index.html.j2')


@app.route('/songs', methods=['POST'])
@app.route('/songs')  # there are two paths to here.
def view_songs():
    all_songs = song_db.all()
    return render_template('songs.html.j2', all_songs=all_songs)


@app.route('/songs/search', methods=['POST'])
@app.route('/songs/search')
@app.route('/songs/search/<term>')
def search_songs(term=None):
    if term:
        pass
    elif request.form['search']:
        term = convert(request.form['search'])
    # Perform a search of all key/value pairs in the database.
    filtered_songs = search_songs_db(term, song_db)
    return render_template('songs.html.j2', all_songs=filtered_songs, term=term)


@app.route('/songs/<int:eid>/view')
@app.route('/songs/<int:eid>/edit')
@app.route('/songs/<int:eid>')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@app.route('/songs/add', methods=['POST'])
@app.route('/songs/add')
def new_song():
    data = Song().to_dict()
    eid = song_db.insert(data)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@app.route('/songs/<int:eid>/save', methods=['POST'])
def save_song(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    return redirect('/songs')


@app.route('/songs/<int:eid>/update', methods=['POST'])
def update_song(eid):
    update_song_info(request=request, eid=eid, song_db=song_db)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@app.route('/songs/<int:eid>/remove', methods=['POST'])
def remove_song(eid):
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
    print(sect_ct)
    song['lyrics'][f'section-{sect_ct}'] = f'lyrics-{sect_ct}'
    return render_template('song.html.j2', song=song)


@app.route('/songs/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.
    """
    update_song_info(request=request, eid=eid, song_db=song_db,
                     exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html.j2', song=song)


@app.route('/songs/<int:eid>/sheet_music/upload', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/upload')
def upload_sheet_music(eid):
    """
    Uploads a PDF for the song.
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
        f.save(osp.join(app.config['UPLOAD_FOLDER'], fname))
        song_db.update({'sheet_music': fname}, eids=[eid])
        song = song_db.get(eid=eid)
        return render_template('song.html.j2', song=song)


@app.route('/songs/<int:eid>/sheet_music/download', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/download')
def download_sheet_music(eid):
    """
    Returns the sheet music to be downloaded.
    """
    song = song_db.get(eid=eid)
    return send_file(osp.join(app.config['UPLOAD_FOLDER'],
                              song['sheet_music']
                              )
                     )


@app.route('/songs/<int:eid>/sheet_music/delete', methods=['POST'])
@app.route('/songs/<int:eid>/sheet_music/delete')
def delete_sheet_music(eid):
    song = song_db.get(eid=eid)
    os.system(f'rm {song["sheet_music"]}')
    song_db.update(delete('sheet_music'), eids=[eid])
    song = song_db.get(eid=eid)
    return render_template("song.html.j2", song=song)


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
#         return send_file('tmp/slides.pptx')


@app.route('/songs/<int:eid>/slides', methods=['POST'])
@app.route('/songs/<int:eid>/slides')
def view_song_slides(eid):
    song = song_db.get(eid=eid)
    arrangement = clean_song_arrangement(song['default_arrangement'], song)
    return render_template('slides_single_song.html.j2',
                           song=song,
                           arrangement=arrangement,
                           eid=eid)


@app.route('/coworkers', methods=['POST'])
@app.route('/coworkers')
def view_coworkers():
    all_coworkers = coworker_db.all()
    return render_template('coworkers.html.j2',
                           all_coworkers=all_coworkers,
                           service=service)


@app.route('/coworkers/add', methods=['POST'])
@app.route('/coworkers/add')
def new_coworker():
    data = Coworker().to_dict()
    eid = coworker_db.insert(data)
    coworker = coworker_db.get(eid=eid)
    return render_template('coworker.html.j2',
                           coworker=coworker,
                           fellowships=fellowships,
                           service=service,
                           genders=genders)


@app.route('/coworkers/<int:eid>/save', methods=['POST'])
@app.route('/coworkers/<int:eid>/save')
def save_coworker(eid):
    update_coworker_info(request=request, eid=eid, coworker_db=coworker_db)
    return redirect('/coworkers')


@app.route('/coworkers/<int:eid>/view', methods=['POST'])
@app.route('/coworkers/<int:eid>/view')
@app.route('/coworkers/<int:eid>/edit', methods=['POST'])
@app.route('/coworkers/<int:eid>/edit')
def view_coworker(eid):
    coworker = coworker_db.get(eid=eid)
    return render_template('coworker.html.j2', coworker=coworker,
                           fellowships=fellowships, service=service,
                           genders=genders)


@app.route('/coworkers/search', methods=['POST'])
@app.route('/coworkers/search')
@app.route('/coworkers/search/<term>')
def search_coworkers(term=None):
    if term:
        pass
    elif request.form['search']:
        term = convert(request.form['search'])
    # Perform a search of all key/value pairs in the database.
    filtered_coworkers = search_coworkers_db(term, coworker_db)
    return render_template('coworkers.html.j2',
                           all_coworkers=filtered_coworkers,
                           term=term,
                           service=service)


@app.route('/coworkers/<int:eid>/remove', methods=['POST'])
@app.route('/coworkers/<int:eid>/remove')
def remove_coworker(eid):
    coworker_db.remove(eids=[eid])
    return redirect('/coworkers')


@app.route('/test/<int:eid>/slides')
def testing_slides(eid):
    """
    Created 3 August 2017. Used to test slide generation functionality. Not
    intended to be used for production. DO NOT MAKE UI ELEMENTS THAT RELY ON
    THIS! Feel free to delete at later date.
    """
    song = song_db.get(eid=eid)
    arrangement = clean_song_arrangement(song['default_arrangement'], song)
    return render_template('slides_single_song.html.j2',
                           song=song,
                           arrangement=arrangement)


@app.route('/programs/add', methods=['POST'])
@app.route('/programs/add')
def new_program():
    """
    Creates a new program
    """
    program_model = Program().to_dict()
    eid = program_db.insert(program_model)
    program = program_db.get(eid=eid)

    songs = song_db.all()
    coworkers = get_grouped_coworkers(coworker_db)

    return render_template('program.html.j2',
                           program=program,
                           songs=songs,
                           coworkers=coworkers)


@app.route('/programs', methods=['POST'])
@app.route('/programs')
def view_programs():
    all_programs = program_db.all()
    for program in all_programs:
        program = fill_program_information(program=program,
                                           coworker_db=coworker_db,
                                           song_db=song_db)
    return render_template('programs.html.j2', all_programs=all_programs)


@app.route('/programs/<int:eid>/view')
@app.route('/programs/<int:eid>/edit')
def view_program(eid):
    program = fill_program_information(program_db.get(eid=eid),
                                       coworker_db=coworker_db,
                                       song_db=song_db)
    print(program)
    songs = song_db.all()
    coworkers = get_grouped_coworkers(coworker_db)
    return render_template('program.html.j2',
                           program=program,
                           coworkers=coworkers,
                           songs=songs)


@app.route('/programs/<int:eid>/update', methods=['POST'])
def update_program(eid):
    """
    Used for updating the list of available coworkers.
    """
    save_program_information(request, eid, program_db)
    program = program_db.get(eid=eid)
    coworkers = get_grouped_coworkers(coworker_db)
    songs = song_db.all()
    return render_template('program.html.j2',
                           program=program,
                           coworkers=coworkers,
                           songs=songs)


@app.route('/programs/<int:eid>/save', methods=['POST'])
def save_program(eid):
    """
    Saves the program to the program_db.
    """
    # Collect the form data into a dictionary.
    save_program_information(request, eid, program_db)
    return redirect('/programs')


@app.route('/programs/<int:eid>/slides', methods=['POST'])
@app.route('/programs/<int:eid>/slides')
def view_program_slides(eid):
    """
    Creates the HTML slides for the songs associated with a program sheet.
    """
    program = fill_program_information(program_db.get(eid=eid),
                                       coworker_db=coworker_db,
                                       song_db=song_db)
    songs = [
             program['song1'],
             program['song2'],
             program['song3'],
             program['offering']
             ]

    for song in songs:
        song['default_arrangement'] = \
            clean_song_arrangement(song['default_arrangement'], song)
    return render_template('slides_multi_song.html.j2', songs=songs)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True, port=8080, host='0.0.0.0')
