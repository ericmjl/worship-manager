"""
General purpose utility functions for use in this project.
"""

import os

from hanziconv import HanziConv

import pinyin

from tinydb import Query

from .datamodels import Lyrics, Program, Song

from .static import (standard_program_roles,
                     standard_program_song_arrangements,
                     standard_program_songs)

hzc = HanziConv()
convert = hzc.toTraditional
# Keep a list of song keys
song_datamodel = list(Song().to_dict().keys())

# We only allow uploading of PDFs.
ALLOWED_EXTENSIONS = set(['pdf'])


def makedir(path):
    """
    Creates a path if it doesn't already exist.

    :param path: Path to be created.
    :type path: `str`
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_lyrics(request, exclude_id=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.


    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.

    :param exclude_id: an integer identifying which lyrics section to exclude.
    :type exclude_id: `int`
    """
    # Defensive programming checks
    if exclude_id:
        assert isinstance(exclude_id, int)

    # Get lyrics
    l = Lyrics()
    for k, v in request.form.items():
        if 'section-' in k:
            idx = int(k.split('-')[-1])
            if idx is not exclude_id:
                lyrics = convert(request.form[f'lyrics-{idx}'])
                section = request.form[k]
                l.add_section(section=section,
                              lyrics=lyrics)
    return l


def update_song_info(request, eid, song_db, exclude_id=None):
    """
    Updates song information in database.

    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.

    :param eid: the eid of the song to be updated in the database.
    :type eid: `int`
    """
    data = {k: convert(v)
            for k, v in request.form.items()
            if k in song_datamodel}
    data['pinyin'] = pinyin.get(data['name'], format="strip", delimiter=" ")

    lyrics = get_lyrics(request=request, exclude_id=exclude_id)
    data['lyrics'] = lyrics.to_dict()
    song_db.update(data, eids=[eid])


def update_coworker_info(request, eid, coworker_db):
    """
    Updates coworker information in database.

    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.

    :param eid: the eid of the coworker to be updated in the database.
    :type eid: `int`
    """
    data = {k: convert(v) for k, v in request.form.items() if k != 'service'}
    data['service'] = []
    # print(request.form.getlist('service'))
    for serv in request.form.getlist('service'):
        data['service'].append(serv)
    coworker_db.update(data, eids=[eid])


def arrange_lyrics(arrangement, song_data):
    """
    Returns the lyrics of a song arranged by the song data.

    :param arrangement: A list of strings describing the arrangement of the
                        lyrics. We do not do checking in this function, so the
                        type must be correct.
    :type arrangement: `list` of `str`

    :param song_data: Song information, conforming to the model sepecification
                      in `datamodels.py`. One of the keys has to be `lyrics`.
    :type song_data: `dict`

    :returns: `arranged_lyrics` (`str`), the lyrics arranged according to the specified
              arrangement.
    """
    # Now, we allow the default arrangement to be set.
    arranged_lyrics = ''
    for a in arrangement:
        arranged_lyrics += song_data['lyrics'][a]
        arranged_lyrics += '\n\n'
    # print(arranged_lyrics)
    return arranged_lyrics


def allowed_file(filename):
    """
    Utility function that checks that the filename has an allowed extension.
    Used when uploading the file. Checks the module-level variable
    `ALLOWED_EXTENSIONS` for allowed uploads.

    :param filename: The name of the file that is being uploaded.
    :type filename: `str`

    :example:
    >>> ALLOWED_EXTENSIONS = ['.pdf', '.jpg']  # module-level variable
    >>> file1 = 'my_file.txt'
    >>> allowed_file(file1)
    False
    >>> file2 = 'my_file'
    >>> allowed_file(file2)
    False
    >>> file3 = 'my_file.jpg'
    >>> allowed_file(file3)
    True
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def search_songs_db(term, db):
    """
    Performs a search of the songs database. Searches all fields' values, as
    well as all lyrics' values.

    The search performed is strictly a sub-string search; capitalization must
    match in order for the search to be done right.

    :param term: Search term.
    :type term: `str`

    :param db: The database object to search. In this project, we use TinyDB
               for simplicity and portability (it's very, very small).
    :type db: `tinydb.TinyDB()`

    :returns: one of `filtered_songs` or `all_songs`, the search results.
    """
    filtered_songs = list()
    all_songs = db.all()
    if term:
        for song in all_songs:
            for k, v in song.items():
                if k == 'lyrics':
                    for sec, txt in v.items():
                        if txt and term in txt and song not in filtered_songs:
                            filtered_songs.append(song)
                else:
                    if v and term in v and song not in filtered_songs:
                        filtered_songs.append(song)
        return filtered_songs
    else:
        return all_songs


def search_coworkers_db(term, db):
    filtered_coworkers = list()
    all_coworkers = db.all()
    if term:
        for coworker in all_coworkers:
            for k, v in coworker.items():
                # print(k, v)
                if k == 'service':
                    for srvc in v:
                        if (srvc
                                and term in srvc
                                and coworker not in filtered_coworkers):
                            filtered_coworkers.append(coworker)
                else:
                    if (v
                            and hasattr(v, '__iter__')
                            and term in v
                            and coworker not in filtered_coworkers):
                        filtered_coworkers.append(coworker)
        return filtered_coworkers
    else:
        return all_coworkers


def get_grouped_coworkers(coworker_db):
    """
    Gets coworkers grouped together by their type. A very hacky function.

    :param coworker_db: The coworker database.
    :type coworker_db: `tinydb.TinyDB()`

    :returns: `coworkers` (`dict`)
    """
    p = Query()
    coworkers = dict()
    coworkers['presiders'] = coworker_db.search(p.service.any(['presider']))
    coworkers['vocalists'] = coworker_db.search(p.service.any(['vocalist']))
    coworkers['pianists'] = coworker_db.search(p.service.any(['pianist']))
    coworkers['speakers'] = coworker_db.search(p.service.any(['speaker']))
    coworkers['audios'] = coworker_db.search(p.service.any(['audio']))
    coworkers['powerpoints'] = coworker_db.search(p.service.any(['powerpoint']))  # noqa

    return coworkers


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
        if program[role]:
            program[role] = coworker_db.get(eid=int(program[role]))

    for song in standard_program_songs():
        if program[song]:
            program[song] = song_db.get(eid=int(program[song]))

    return program


def save_program_information(request, eid, program_db, song_db):
    """
    Commits program information to the program DB.
    """
    program_model = Program().to_dict()
    form_data = {k: v
                 for k, v in request.form.items()
                 if k in program_model.keys()}

    # Validate song arrangements
    for song_label, song_arrangement in \
            zip(standard_program_songs(), standard_program_song_arrangements()):  # noqa
        arrangement = clean_arrangement(form_data[song_arrangement])
        song = song_db.get(eid=int(form_data[song_label]))
        if not is_valid_arrangement(arrangement, song):
            form_data[song_arrangement] = song['default_arrangement']
    program_db.update(form_data, eids=[eid])


def clean_arrangement(arrangement):
    """
    Cleans the song arrangement and turns it into a list.

    :param arrangement: a string containing the arrangement of the song.
    :type arrangement: `str`

    :param song_data: a data dictionary. Keys are the data model fields as
                      specified in `datamodels.py`. One of the keys has to be
                      `lyrics`.
    :type song_data: `dict`

    :returns: arrangement (`list` of `str`) a list of strings, each of which is
              a key in song's lyrics dictionary.

    :example:
    >>> str_arr = 'V, C, V, C'
    >>> clean_arrangement(str_arr)
    ['V', 'C', 'V', 'C']
    """
    arrangement = [a.strip(' ') for a in arrangement.split(',')]
    return arrangement


def is_valid_arrangement(arrangement, song):
    """
    Validates an arrangement against a song. Returns True (valid) or
    False (invalid). Valid means that every section specified in the
    arrangement exists in the song's specified sections.

    Inputs:
    =======
    - song: a dictionary conforming to the Song object data model.
    - arrangement: a list specifying the arrangement of the song.

    Returns:
    ========
    - is_valid: boolean indicating whether the arrangement is valid.
    """

    is_valid = True
    for section in arrangement:
        if section not in song['lyrics'].keys():
            is_valid = False
            print(f'{section} not in {song["lyrics"].keys()}')
            break
    return is_valid
