import os.path as osp

from app import app

from app.datamodels import Coworker, Program

from app.static import fellowships, genders, service

from app.utils import (clean_arrangement, fill_program_information,
                       get_grouped_coworkers, makedir,
                       save_program_information,
                       search_coworkers_db,
                       update_coworker_info)

from flask import redirect, render_template, request

from hanziconv import HanziConv

from tinydb import TinyDB

datafolder = 'data/'

app.config['UPLOAD_FOLDER'] = osp.join(datafolder,
                                       'files/')
makedir(app.config['UPLOAD_FOLDER'])

dbfolder = osp.join(datafolder, 'database')
makedir(dbfolder)

song_db = TinyDB(osp.join(dbfolder, 'song.db'))
coworker_db = TinyDB(osp.join(dbfolder, 'coworker.db'))
calendar_db = TinyDB(osp.join(dbfolder, 'calendar.db'))
program_db = TinyDB(osp.join(dbfolder, 'program.db'))

hzc = HanziConv()
convert = hzc.toTraditional


# -------- coworkers section -------- #

@app.route('/coworkers', methods=['POST'])
@app.route('/coworkers')
def view_coworkers():
    all_coworkers = coworker_db.all()
    return render_template('coworkers.html.j2',
                           all_coworkers=all_coworkers,
                           service=service())


@app.route('/coworkers/add', methods=['POST'])
@app.route('/coworkers/add')
def new_coworker():
    data = Coworker().to_dict()
    eid = coworker_db.insert(data)
    coworker = coworker_db.get(eid=eid)
    return render_template('coworker.html.j2',
                           coworker=coworker,
                           fellowships=fellowships(),
                           service=service(),
                           genders=genders())


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
    return render_template('coworker.html.j2',
                           coworker=coworker,
                           fellowships=fellowships(),
                           service=service(),
                           genders=genders())


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
                           service=service())


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
    arrangement = clean_arrangement(song['default_arrangement'], song)
    return render_template('slides_single_song.html.j2',
                           song=song,
                           arrangement=arrangement)

# -------- programs section -------- #


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
    # print(program)
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
    save_program_information(request, eid, program_db, song_db)
    return redirect(f'/programs/{eid}/view')


@app.route('/programs/<int:eid>/save', methods=['POST'])
def save_program(eid):
    """
    Saves the program to the program_db.
    """
    # Collect the form data into a dictionary.
    save_program_information(request, eid, program_db, song_db)
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
             [program['song1'], program['song1_arrangement']],
             [program['song2'], program['song2_arrangement']],
             [program['song3'], program['song3_arrangement']],
             [program['offering'], program['offering_arrangement']]
             ]

    for i, (song, arr) in enumerate(songs):
        if arr:
            songs[i][1] = clean_arrangement(arr)
        else:
            songs[i][1] = clean_arrangement(song['default_arrangement'])  # noqa
    print(songs)
    return render_template('slides_multi_song.html.j2', songs=songs)


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True, port=8080, host='0.0.0.0')
