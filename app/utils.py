from .env import convert
from flask import request

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


def get_lyrics(request: request, exclude_id: int=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.

    :param request: `request` object from the Flask app.
    :param exclude_id: an integer identifying which lyrics section to exclude.
    :returns: A Lyrics object containing the song's lyrics in a structured
              format.
    """
    # Defensive programming checks
    if exclude_id:
        assert isinstance(exclude_id, int)

    # Get lyrics
    lyr = Lyrics()
    for k, v in request.form.items():
        if "section-" in k:
            idx = int(k.split("-")[-1])
            if idx is not exclude_id:
                # First, convert to traditional.
                lyrics = convert(request.form[f"lyrics-{idx}"])

                section = request.form[k]
                lyr.add_section(section=section, lyrics=lyrics)
    return lyr


def clean_lyrics(song):
    """
    Cleans the lyrics in a song object.
    """
    cleaned_lyrics = dict()
    for name, lyrics in song.lyrics.items():
        # Strip trailing punctuation except for question marks.
        lyrics = lyrics.strip("。，；：").strip(',.;:')

        # Replace middle punctuation with special blank-space character.
        # The special space character is specified here:
        # https://unicodelookup.com/#%E3%80%80/1
        lyrics = (
            lyrics.replace("。", "　")
            .replace("，", "　")
            .replace("；", "　")
            .replace("、", "　")
            .replace(".", "　")
            .replace(",", "　")
            .replace(";", "　")
            .replace(" ", "　")
        )
        cleaned_lyrics[name] = lyrics
    song.lyrics.update(cleaned_lyrics)
    return song


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
    arrangement = [a.strip(" ") for a in arrangement.split(",")]
    return arrangement


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
    ALLOWED_EXTENSIONS = set(["pdf"])

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def lyrics_plaintext(song):
    """
    Get lyrics as plaintext.
    """
    output = ""

    song = validate_song(song)

    output += song.default_arrangement
    output += "\n\n\n\n"
    output += song.composer
    output += "\n"
    output += song.copyright
    output += "\n\n"

    for section, lyrics in song.lyrics.items():
        output += section
        output += "\n"
        output += lyrics
        output += "\n\n"
    return output


def validate_song(song):
    """
    Converts song fields from None to '' for string outputs.
    """
    attrs = ["default_arrangement", "composer", "copyright", "youtube", "ccli"]
    for a in attrs:
        if getattr(song, a) in [None, "None"]:
            setattr(song, a, "")
    return song
