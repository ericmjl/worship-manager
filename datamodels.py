"""
Data models used in the project.
"""


class Song(object):
    def __init__(self, name='name', copyright='organization',
                 composer='composer', lyrics=None, ccli=None):
        self.name = name
        self.copyright = copyright
        self.composer = composer
        self.ccli = ccli
        self.lyrics = lyrics
        self._add_lyrics(lyrics)

    def _add_lyrics(self, lyrics):
        if lyrics:
            assert isinstance(lyrics, Lyrics)
            self.lyrics = lyrics

    def to_dict(self):
        return self.__dict__


class Lyrics(object):
    def __init__(self):
        self.sections = dict()

    def add_section(self, section, lyrics):
        self.sections[section] = lyrics

    def to_dict(self):
        return self.sections
