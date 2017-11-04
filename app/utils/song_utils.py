"""
Utility functions used in songs.
"""
import pinyin

from ..datamodels import Lyrics
from ..views.__init__ import convert
from .__init__ import ALLOWED_EXTENSIONS, song_datamodel


def clean_arrangement(arrangement):
    """
    Cleans the song arrangement and turns it into a list.

    :example:
    >>> str_arr = 'V, C, V, C'
    >>> clean_arrangement(str_arr)
    ['V', 'C', 'V', 'C']

    :param arrangement: a comma-delimited string containing the arrangement of
        the song.
    :type arrangement: `str`

    :param song_data: a data dictionary. Keys are the data model fields as
        specified in `datamodels.py`. One of the keys has to be "lyrics".
    :type song_data: `dict`

    :returns: arrangement a list of strings, each of which is a key in song's
        lyrics dictionary.
    :rtype: `list(str)`
    """
    arrangement = [a.strip(' ') for a in arrangement.split(',')]
    return arrangement


def is_valid_arrangement(arrangement, song):
    """
    Validates an arrangement against a song. Returns True (valid) or
    False (invalid). Valid means that every setion specified in the
    arrangement exists in the song's specified sections.

    :param song: a dictionary conforming to the Song object data model.
    :param arrangement: a list specifying the arrangement of the song.

    :returns: `is_valid`, indicating whether the arrangement is valid.
    :rtype: `bool`
    """

    is_valid = True
    for section in arrangement:
        if section not in song['lyrics'].keys():
            is_valid = False
            print(f'{section} not in {song["lyrics"].keys()}')
            break
    return is_valid


def arrange_lyrics(arrangement, song_data):
    """
    Returns the lyrics of a song arranged by the song data.

    :param arrangement: A list of strings describing the arrangement of the
                        lyrics. We do not do checking in this function, so the
                        type must be correct.
    :type arrangement: `list(str)`

    :param song_data: Song information, conforming to the model sepecification
                      in `datamodels.py`. One of the keys has to be `lyrics`.
    :type song_data: `dict`

    :returns: `arranged_lyrics`, the lyrics arranged according to the
              specified arrangement.
    :rtype: `str`
    """
    # Now, we allow the default arrangement to be set.
    arranged_lyrics = ''
    for a in arrangement:
        arranged_lyrics += song_data['lyrics'][a]
        arranged_lyrics += '\n\n'
    # print(arranged_lyrics)
    return arranged_lyrics


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
    :rtype: `iterable(dict)`
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


def get_lyrics(request, exclude_id=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.


    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.

    :param exclude_id: an integer identifying which lyrics section to exclude.
    :type exclude_id: `int`

    :returns: A Lyrics object containing the song's lyrics in a structured
              format.
    """
    # Defensive programming checks
    if exclude_id:
        assert isinstance(exclude_id, int)

    # Get lyrics
    lyr = Lyrics()
    for k, v in request.form.items():
        if 'section-' in k:
            idx = int(k.split('-')[-1])
            if idx is not exclude_id:
                lyrics = convert(request.form[f'lyrics-{idx}'])
                section = request.form[k]
                lyr.add_section(section=section,
                                lyrics=lyrics)
    return lyr
