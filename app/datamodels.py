"""
Data models used in the project.
"""

import pinyin
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy


class Song(object):
    """
    :param name: Name of the song.
    :type name: `str`

    :param copyright: Organization that owns the copyright of the songs.
    :type copyright: `str`

    :param composer: Name of the composer(s).
    :type composer: `str`

    :param lyrics: The lyrics of the song.
    :type lyrics: `Lyrics` object.

    :param ccli: The CCLI number.
    :type ccli: `str`

    :param default_arrangement: How the songs are arranged.
    :type default_arrangement: `str`

    :param youtube: URL to a YouTube video.
    :type youtube: `str`
    """

    def __init__(
        self,
        name="",
        copyright="",
        composer="",
        lyrics=None,
        ccli="",
        default_arrangement=None,
        youtube="",
    ):
        self.name = name
        self.pinyin_name = pinyin.get(self.name, format="strip", delimiter=" ")
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

        :param lyrics: A Lyrics object
        """
        if lyrics:
            assert isinstance(lyrics, Lyrics)
            self.lyrics = lyrics

    def to_dict(self):
        """
        :returns: `dict` representation of Song object.
        """
        return self.__dict__

    def _add_default_arrangement(self, default_arrangement):
        # Firstly, we make sure that every element in default_arrangement is
        # a key in the lyrics' sections.
        if default_arrangement:
            for section in default_arrangement:
                assert (
                    section in self.lyrics.sections.keys()
                ), f"{section} not specified"

            # Now, we allow the default arrangement to be set.
            self.default_arrangement = default_arrangement


class Lyrics(object):
    """
    Data model for a song's lyrics.

    :attr sections: A key-value pairing of section to lyrics.
    """

    def __init__(self):
        self.sections = dict()

    def add_section(self, section, lyrics):
        """
        Adds a section to the Lyrics object.

        :param section: The name of the section. (e.g. `V1`, `A`, `Chorus`
                        etc.)
        :type section: `str`

        :param lyrics: The lyrics of that section.
        :type lyrics: `str`
        """
        self.sections[section] = lyrics

    def to_dict(self):
        """
        :returns: a `dict` representation of the Lyrics object.
        """
        return self.sections
