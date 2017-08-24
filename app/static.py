"""
Static information that's used across the modules. Generally useful. This
module collects them all here so that when there's a need to update them, they
can be updated in just one place.

We use functions that return data as the implementation. This makes it easier
to document using Sphinx. If not for the documentation requirement, it would
be easier to just import the variables directly.
"""


def fellowships():
    """
    Fellowships that are a part of COM.
    """
    fellowships = {
        'MIT': 'MIT 團契',
        'Longwood': 'Longwood 團契',
        'BSF': 'BSF 學生團契',
        'ROD': 'ROD 樂河團契',
        'Malden': 'Malden 學生事工',
        'COM': 'CBCGB-COM 同工',  # for those whose primary roles cross fellowships  # noqa
        }
    return fellowships


def service():
    """
    Roles for service every Sunday.
    """
    service = {
        'presider': '領會',
        'speaker': '講員',
        'vocalist': '領唱',
        'pianist': '司琴',
        'guitarist': '吉他手',
        'bassist': '貝斯手',
        'drummer': '鼓手',
        'communion': '聖餐',
        'powerpoint': 'PPT',
        'audio': '音控',
        'sundayschool': '主日學'
        }
    return service


# Genesis 1:27
def genders():
    """
    Genders. God created them, male and female.
    """
    genders = {
        'male': '男',
        'female': '女',
        'group': '团体'
    }
    return genders


# Standard song types each week
def standard_program_songs():
    """
    Standard program songs.
    """
    standard_program_songs = [
        'song1',
        'song2',
        'song3',
        'offering',
        'response',
        ]
    return standard_program_songs


def standard_program_song_arrangements():
    """
    Names for the song arrangements. Should mirror `standard_program_songs()`.
    """
    standard_program_song_arrangements = [
        'song1_arrangement',
        'song2_arrangement',
        'song3_arrangement',
        'offering_arrangement',
        'response_arrangement',
        ]
    return standard_program_song_arrangements


def standard_program_roles():
    """
    Standard service roles that every week.
    """
    standard_program_roles = [
        'presider',
        'vocalist1',
        'vocalist2',
        'vocalist3',
        'pianist',
        'guitarist',
        'drummer',
        'bassist',
        'audio',
        'powerpoint',
        'speaker'
        ]
    return standard_program_roles
