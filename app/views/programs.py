from flask import Blueprint, redirect, render_template, request

from .__init__ import coworker_db, program_db, song_db

from ..datamodels import Program

from ..utils import (authorize_google_sheets,
                     clean_arrangement,
                     create_gsheet,
                     delete_spreadsheet,
                     fill_program_information,
                     get_grouped_coworkers,
                     save_program_information)


mod = Blueprint('programs', __name__, url_prefix='/programs')


@mod.route('/add', methods=['POST'])
@mod.route('/add')
def new():
    """
    Adds a new program to the database. To ensure that the program is entered
    into the database, we first create the program in the db, and then return
    the empty information to Jinja, including the eid. In this way, we are
    guaranteed an eid for the /save function (below).
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
    """
    Master view for all weekly programs in the database.

    :returns: Renders an HTML table of all programs.
    """
    all_programs = program_db.all()
    for program in all_programs:
        program = fill_program_information(program=program,
                                           coworker_db=coworker_db,
                                           song_db=song_db)
    return render_template('programs.html.j2', all_programs=all_programs)


@mod.route('/<int:eid>/view')
@mod.route('/<int:eid>/edit')
@mod.route('/<int:eid>')
def view(eid):
    """
    Displays a page to view a particular week's program. The view page doubles
    up as the edit page as well.

    :param eid: The eid of the program to be viewed.
    :type eid: int

    :returns: Renders the view of the individual program.
    """
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
def update(eid):
    """
    Updates the program information to the database. In contrast to save(eid),
    this function will come back to the song page.

    :param eid: The eid of the program to be updated.
    :type eid: int

    :returns: Redirects to view the same program.
    """
    save_program_information(request, eid, program_db, song_db)
    return redirect(f'/programs/{eid}/view')


@mod.route('/<int:eid>/save', methods=['POST'])
def save(eid):
    """
    Saves the program to the program_db.

    :param eid: The eid of the program to save.
    :type eid: int

    :returns: Redirects back to the master view.
    """
    # Collect the form data into a dictionary.
    save_program_information(request, eid, program_db, song_db)
    return redirect('/programs/')


@mod.route('/<int:eid>/slides', methods=['POST'])
@mod.route('/<int:eid>/slides')
def view_program_slides(eid):
    """
    Creates the HTML slides for the songs associated with a program sheet.

    :param eid: The eid of the program for which the HTML slides are to be
        made.
    :type eid: int

    :returns: Renders the HTML slides.
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
            songs[i][1] = clean_arrangement(song['default_arrangement'])
    return render_template('slides_multi_song.html.j2', songs=songs)


@mod.route('/<int:eid>/create_gsheet')
def create_google_sheets(eid):
    """
    Creates the Google Spreadsheet for that week's Program.

    :param eid: The eid of the program for which the Google Sheet is to be
        created/updated.
    :type eid: int

    :returns: Redirects to the view page for the program.
    """
    gc = authorize_google_sheets()
    spreadsheet = create_gsheet(gc, eid, program_db)
    program_db.update({'gsheets': spreadsheet.id}, eids=[eid])

    return redirect(f'/programs/{eid}')


@mod.route('/<int:eid>/delete_gsheet')
def delete_google_sheets(eid):
    gc = authorize_google_sheets()
    delete_spreadsheet(gc, eid, program_db)

    return redirect(f'programs/{eid}')
