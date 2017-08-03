"""
Data models used in the project.
"""


class Song(object):
    def __init__(self, name='name', copyright='organization',
                 composer='composer', lyrics=None, ccli=None,
                 default_arrangement=None):
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
