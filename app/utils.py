from .env import convert


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


def get_lyrics(request, exclude_id=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.
    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.
    :param exclude_id: an integer identifying which lyrics section to exclude.
    :type exclude_id: `int`
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
                lyrics = convert(request.form[f"lyrics-{idx}"])
                section = request.form[k]
                lyr.add_section(section=section, lyrics=lyrics)
    return lyr
