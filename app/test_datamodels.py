from .datamodels import Lyrics, Song

l = Lyrics()
sections = ['A', 'B']
lyrics = ['lyrics-1', 'lyrics-2']


def test_lyrics():
    for section, lyric in zip(sections, lyrics):
        l.add_section(section, lyric)

    assert len(l.sections) == 2
    for section in sections:
        assert section in l.sections


def test_songs():
    s = Song(lyrics=l, default_arrangement=['A', 'B'])
    assert isinstance(s.lyrics, Lyrics)
