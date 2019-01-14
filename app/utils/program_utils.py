from ..datamodels import Program
from ..static import (standard_program_roles,
                      standard_program_song_arrangements,
                      standard_program_songs)
from .song_utils import clean_arrangement, is_valid_arrangement


def fill_program_information(program, coworker_db, song_db):
    """
    Fills in program information given the program.

    In the program database, only `eid` numbers are stored for each of the
    coworkers and the songs. Thus, the program dictinary has to be populated
    with the correct information.

    :param program: A dictionary returned from the program database. This maps
                    to one entry in the database.
    :type program: `dict`

    :param coworker_db: The coworker database object.
    :type coworker_db: `tinydb.TinyDB()`

    :param song_db: The song database object.
    :type song_db: `tinydb.TinyDB()`

    :returns: `program` (`dict`), with song information and coworker
              information populated.
    """
    for role in standard_program_roles():
        if role in program.keys() and program[role]:
            program[role] = coworker_db.get(eid=int(program[role]))

    for song in standard_program_songs():
        if song in program.keys() and program[song]:
            program[song] = song_db.get(eid=int(program[song]))

    return program


def save_program_information(request, eid, program_db, song_db):
    """
    Commits program information to the program DB.
    """
    program_model = Program().to_dict()
    form_data = {
        k: v for k, v in request.form.items() if k in program_model.keys()
    }

    # Validate song arrangements
    for song_label, song_arrangement in zip(
        standard_program_songs(), standard_program_song_arrangements()
    ):  # noqa
        arrangement = clean_arrangement(form_data[song_arrangement])
        if form_data[song_label]:
            song = song_db.get(eid=int(form_data[song_label]))
            if not is_valid_arrangement(arrangement, song):
                form_data[song_arrangement] = song["default_arrangement"]
    program_db.update(form_data, eids=[eid])
