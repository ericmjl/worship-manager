from flask import Blueprint, redirect, render_template, request

from .__init__ import coworker_db, program_db, song_db

from ..datamodels import Program

from ..utils import clean_arrangement, fill_program_information, get_grouped_coworkers, save_program_information

mod = Blueprint('programs', __name__, url_prefix='/programs')


@mod.route('/add', methods=['POST'])
@mod.route('/add')
def new():
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


@mod.route('/', methods=['POST'])
@mod.route('/')
def view_all():
    all_programs = program_db.all()
    for program in all_programs:
        program = fill_program_information(program=program,
                                           coworker_db=coworker_db,
                                           song_db=song_db)
    return render_template('programs.html.j2', all_programs=all_programs)


@mod.route('/<int:eid>/view')
@mod.route('/<int:eid>/edit')
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


@mod.route('/<int:eid>/update', methods=['POST'])
def update_program(eid):
    """
    Used for updating the list of available coworkers.
    """
    save_program_information(request, eid, program_db, song_db)
    return redirect(f'/programs/{eid}/view')


@mod.route('/<int:eid>/save', methods=['POST'])
def save_program(eid):
    """
    Saves the program to the program_db.
    """
    # Collect the form data into a dictionary.
    save_program_information(request, eid, program_db, song_db)
    return redirect('/programs/')


@mod.route('/<int:eid>/slides', methods=['POST'])
@mod.route('/<int:eid>/slides')
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
