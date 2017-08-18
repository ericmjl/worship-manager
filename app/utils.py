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
    if not os.path.exists(path):
        os.makedirs(path)


def get_lyrics(request, exclude_id=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.

    Parameters:
    ===========
    - request: pass in `request` from Flask app.
    - exclude_id: (int) used in excluding a particular lyrics section.
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

    Parameters:
    ===========
    - request: (dict-like) the `request` object from the Flask app.
    - eid: (int) the eid of the song to be updated in the database.
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

    Parameters:
    ===========
    - request: (dict-like) the `request` object from the Flask app.
    - eid: (int) the eid of the coworker to be updated in the database.
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

    Parameters:
    ===========
    - arrangement: (list of str) a list of strings, each of which is a key in
                   the song's lyrics dictionary.
    - song_data: (dict) the song's data dictionary conforming to the
                 specification in `datamodels.py`. One of the keys is `lyrics`.

    Returns:
    ========
    - arranged_lyrics: (str) the lyrics arranged according to the specified
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
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def search_songs_db(term, db):
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
    for role in standard_program_roles:
        if program[role]:
            program[role] = coworker_db.get(eid=int(program[role]))

    for song in standard_program_songs:
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
            zip(standard_program_songs, standard_program_song_arrangements):
        arrangement = clean_arrangement(form_data[song_arrangement])
        song = song_db.get(eid=int(form_data[song_label]))
        if not is_valid_arrangement(arrangement, song):
            form_data[song_arrangement] = song['default_arrangement']
    program_db.update(form_data, eids=[eid])


def clean_arrangement(arrangement):
    """
    Cleans the song arrangement and turns it into a list.

    Parameters:
    ===========
    - arrangement: (str) a string containing the arrangement of the song.
    - song_data: (dict) a data dictionary. Keys are the data model fields as
                 specified in `datamodels.py`. One of the keys has to be
                 `lyrics`.

    Returns:
    ========
    - arrangement: (list of str) a list of strings, each of which is a key in
                   song's lyrics dictionary.
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
