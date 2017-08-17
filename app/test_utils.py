from collections import defaultdict

import pytest

from .datamodels import Lyrics

from .utils import (allowed_file,
                    arrange_lyrics,
                    clean_song_arrangement,
                    get_lyrics,
                    search_songs_db,
                    update_song_info)


# Define a mock "request" class to mimick the real "request" object returned.
class Request(object):
    def __init__(self):
        self.form = dict()


# Define a mock "database" class to mimick the real "database" object.
class Database(object):
    def __init__(self):
        self.data = defaultdict(dict)

    def update(self, data, eids):
        for eid in eids:
            self.data[eid].update(data)

    def all(self):
        recs = []
        for k, v in self.data.items():
            recdata = v
            recs.append(recdata)
        return recs


def to_request(song_data):
    r = Request()
    for k, v in song_data.items():
        if k == 'lyrics':
            for i, (section, lyrics) in enumerate(v.items()):
                r.form[f'section-{i+1}'] = section
                r.form[f'lyrics-{i+1}'] = lyrics
        else:
            r.form[k] = v
    return r


# Setup some mock data for tests below.
song1_data = {'lyrics': {'A': 'lyrics1', 'B': 'lyrics2', 'C': 'lyrics3'},
              'name': 'test_song',
              'composer': '',
              'copyright': 'copyright',
              'pinyin': 't e s t _ s o n g'}
song2_data = {'lyrics': {'A': 'lyrics1', 'B': 'lyrics2', 'C': 'lyrics3'},
              'name': 'test_song2',
              'composer': '',
              'copyright': 'copyright',
              'pinyin': 't e s t _ s o n g 2'}
request = to_request(song1_data)

song_db = Database()
song_db.update(song1_data, [1])
song_db.update(song2_data, [2])


def test_clean_song_arrangement():
    # This first test is a "correctness" test - we give a valid input and
    # check to make sure that the output is valid too.
    arrangement = 'A, B, A, C'
    new_arrangement = clean_song_arrangement(arrangement, song1_data)

    assert new_arrangement == ['A', 'B', 'A', 'C']

    # This second test is an "incorrectness" test - we give it an invalid input
    # and check that an error is raised.
    with pytest.raises(AssertionError):
        invalid_arrangement = 'A, B, A, D'
        new_arrangement = clean_song_arrangement(invalid_arrangement,
                                                 song1_data)


def test_arrange_lyrics():
    # This first test is the "correctness" test. Give valid input, return
    # valid output.
    arrangement = ['A', 'B']

    arranged_lyrics = arrange_lyrics(arrangement, song1_data)

    assert arranged_lyrics == 'lyrics1\n\nlyrics2\n\n'

    # The second test is an "incorrectness" test. Give an invalid input,
    # check that an error is raised.
    invalid_arrg = ['A', 'D']
    with pytest.raises(KeyError):
        arranged_lyrics = arrange_lyrics(invalid_arrg, song1_data)


def test_get_lyrics():
    # This is the "correctness" test.
    lyrics = get_lyrics(request)
    assert isinstance(lyrics, Lyrics)
    assert lyrics.sections['A'] == 'lyrics1'
    assert lyrics.sections['B'] == 'lyrics2'

    # This next test explicitly tests the exclusion of a section.
    lyrics = get_lyrics(request, exclude_id=1)
    assert lyrics.sections['B'] == 'lyrics2'
    with pytest.raises(KeyError):
        assert lyrics.sections['A'] == 'lyrics1'


def test_update_song_info():
    eid = 1
    update_song_info(request, eid, song_db)

    assert song_db.data[eid] == song1_data


# def test_ensure_dir():
#     file_path = os.path.join(os.getcwd(), 'testdir')
#     print(os.path.dirname(file_path))
#     print(file_path)
#     ensure_dir(file_path)
#     assert os.path.exists(file_path)
#     # os.rmdir(file_path)


def test_allowed_file():
    assert allowed_file('myfile.pdf')
    assert not allowed_file('myfile.jpg')


def test_search_songs_db():
    term = 'song2'
    filtered_songs = search_songs_db(term, song_db)
    assert len(filtered_songs) == 1

    term = 'test_song'
    filtered_songs = search_songs_db(term, song_db)
    assert len(filtered_songs) == 2
