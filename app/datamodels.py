"""
Data models used in the project.
"""


import pinyin


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
    def __init__(self, name='', copyright='',
                 composer='', lyrics=None, ccli='',
                 default_arrangement=None, youtube=''):
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
                assert section in self.lyrics.sections.keys(), \
                    f'{section} not specified'

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


class Coworker(object):
    """
    Data model for a coworker.

    :param name: Coworker's name
    :type name: `str`

    :param alias: Alternative names for the coworker.
    :type alias: `str`

    :param pinyin: Pinyin of coworker's name. Makes searching for them easier. 
    :type pinyin: `str`

    :param fellowship: Coworker's primary fellowship. Refer to `static.py` for
                       the full list of fellowships.
    :type fellowship: `str`

    :param email: Coworker's email address.
    :type email: `str`

    :param phone: Coworker's phone number. Should be of format `###-###-####`.
    :type phone: `str`

    :param service: List of roles that a coworker serves in.
    :type service: `list` of `str`

    :param gender: Coworker's gender. Genesis 1:26-27
    :type gender: `str`, one of "M" or "F".
    """
    def __init__(self, name="", alias="", fellowship="", email="", phone="",
                 service=[], gender=""):
        self.name = name
        self.alias = alias
        self.fellowship = fellowship
        self.email = email
        self.phone = phone
        self.service = service
        self.active = True
        self.gender = gender

    def __repr__(self):
        return f"{self.name}, {self.fellowship}"

    def to_dict(self):
        return self.__dict__


class Program(object):
    """
    Data model for a program.

    :param date: The worship service date.
    :type date: `str`

    :param presider: The name of the presider.
    :type presider: `str`

    :param pianist: The name of the pianist.
    :type pianist: `str`

    :param drummer: The name of the drummer.
    :type drummer: `str`

    :param guitarist: The name of the guitarist.
    :type guitarist: `str`

    :param vocalist1: The name of vocalist #1.
    :type vocalist1: `str`

    :param vocalist2: The name of vocalist #2.
    :type vocalist2: `str`

    :param vocalist3: The name of vocalist #3.
    :type vocalist3: `str`

    :param speaker: The name of the speaker.
    :type speaker: `str`

    :param audio: The name of the audio controller coworker.
    :type audio: `str`

    :param powerpoint: The name of the slides controller coworker.
    :type powerpoint: `str`

    :param song1: The eid of the first worship song.
    :type song1: `int`

    :param song2: The eid of the second worship song.
    :type song2: `int`

    :param song3: The eid of the third worship song.
    :type song3: `int`

    :param offering: The eid of the offering song.
    :type offering: `int`

    :param response: The eid of the response song.
    :type response: `int`

    .. note:: Arrangements are stored in the corresponding `{song}_arrangement`
              object attribute.
    """
    def __init__(self, date='',
                 presider='',
                 pianist='', guitarist='', drummer='',
                 vocalist1='', vocalist2='', vocalist3='',
                 speaker='',
                 audio='', powerpoint='',
                 song1='', song2='', song3='', offering='', response=''):

        # Coworkers
        self.date = date
        self.presider = presider
        self.pianist = pianist
        self.vocalist1 = vocalist1
        self.vocalist2 = vocalist2
        self.vocalist3 = vocalist3
        self.audio = audio
        self.powerpoint = powerpoint
        self.speaker = speaker
        self.guitarist = guitarist
        self.drummer = drummer

        # Songs + Arrangements
        self.song1 = song1
        self.song1_arrangement = None
        self.song2 = song2
        self.song2_arrangement = None
        self.song3 = song3
        self.song3_arrangement = None
        self.offering = offering
        self.offering_arrangement = None
        self.response = None
        self.response_arrangement = None

    def to_dict(self):
        return self.__dict__
