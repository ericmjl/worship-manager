"""
Data models used in the project.
"""


class Song(object):
    def __init__(self, name, source, lyrics):
        self.name = name
        self.source = source
        assert isinstance(lyrics, Lyrics)
        self.lyrics = lyrics


class Lyrics(object):
    def __init__(self):
        self.sections = dict()

    def add_section(self, section_name, lyrics):
        self.sections[section_name] = lyrics
