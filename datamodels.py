"""
Data models used in the project.
"""


class Song(object):
    def __init__(self, name='name', copyright='organization',
                 composer='composer', lyrics=None, ccli=None,
                 default_arrangement=None):
        self.name = name
        self.copyright = copyright
        self.composer = composer
        self.ccli = ccli

        self.lyrics = lyrics
        self._add_lyrics(lyrics)

        self.default_arrangement = default_arrangement
        self._add_default_arrangement(default_arrangement)

    def _add_lyrics(self, lyrics):
        if lyrics:
            assert isinstance(lyrics, Lyrics)
            self.lyrics = lyrics

    def to_dict(self):
        return self.__dict__

    def _add_default_arrangement(self, default_arrangement):
        # Firstly, we make sure that every element in default_arrangement is
        # a key in the lyrics' sections.
        if default_arrangement:
            for section in default_arrangement:
                assert section in self.lyrics.keys(), f'{section} not specified'  # noqa

            # Now, we allow the default arrangement to be set.
            self.default_arrangement = default_arrangement


class Lyrics(object):
    def __init__(self):
        self.sections = dict()

    def add_section(self, section, lyrics):
        self.sections[section] = lyrics

    def to_dict(self):
        return self.sections
