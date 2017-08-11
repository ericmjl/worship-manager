"""
Data models used in the project.
"""


class Song(object):
    def __init__(self, name='', copyright='',
                 composer='', lyrics=None, ccli='',
                 default_arrangement=None, youtube=''):
        """
        Initialization.

        :name: Name of the song.
        :type name: str

        :copyright: Organization that owns the copyright of the songs.
        :type copyright: str

        :composer: Name of the composer(s).
        :type composer: str

        :lyrics: The lyrics of the song.
        :type lyrics: Lyrics object.

        :ccli: The CCLI number.
        :type ccli: str

        :default_arrangement: How the songs are arranged.
        :type default_arrangement: str

        :youtube: URL to a YouTube video.
        :type youtube: str
        """
        self.name = name
        self.copyright = copyright
        self.composer = composer
        self.ccli = ccli

        self.lyrics = lyrics
        self._add_lyrics(lyrics)

        self.default_arrangement = default_arrangement
        self._add_default_arrangement(default_arrangement)

        self.sheet_music = None
        self.youtube = youtube

    def _add_lyrics(self, lyrics=None):
        """
        Adds lyrics to the Song object.
        """
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
                assert section in self.lyrics.sections.keys(), \
                    f'{section} not specified'

            # Now, we allow the default arrangement to be set.
            self.default_arrangement = default_arrangement


class Lyrics(object):
    def __init__(self):
        self.sections = dict()

    def add_section(self, section, lyrics):
        self.sections[section] = lyrics

    def to_dict(self):
        return self.sections


class Coworker(object):
    def __init__(self, name="", alias="", fellowship="", email="", phone="",
                 service=[]):
        self.name = name
        self.alias = alias
        self.fellowship = fellowship
        self.email = email
        self.phone = phone
        self.service = service
        self.active = True

    def __repr__(self):
        return f"{self.name}, {self.fellowship}"

    def to_dict(self):
        return self.__dict__
