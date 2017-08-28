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


def gsheets_template():
    """
    Key-value pairs that specify what content goes into which cells on the
    standard weekly program sheet. Only non-dynamic information is stored here;
    all dynamic information has to be updated in a separate function.
    """

    gsheets_template = {
        'A1': '时间',
        'B1': '程序',
        'C1': '内容',
        'D1': '负责同工',
        'E1': '参与团队',

        'B2': '序乐',
        'D2': '【司琴】',
        'E2': '会众',

        'B3': '宣召',
        'C3': '【宣召经文】',
        'D3': '【领会】\n【领诗】',

        'B4': '音乐敬拜',
        'C4': '【诗歌（一）】\n【诗歌（二）】\n【诗歌（三）】',
        'D4': '【领会】\n【领诗】',

        'A5': '1点20分',
        'B5': '奉献',
        'C5': '【奉献诗歌】',
        'D5': '【领会】',
        'E5': '会众\n【敬拜团】',

        'B6': '读经',
        'C6': '【经文】',
        'D6': '【领会】',

        'A7': '1点25分',
        'B7': '证道',
        'C7': '【讲道题目】',
        'D7': '【讲员】',

        'A8': '2点',
        'B8': '圣餐／回应',
        'E8': '圣餐同工／敬拜团',

        'B9': '欢迎与报告',
        'D9': '牧师／长老',

        'B10': '三一颂／祝祷',
        'D10': '牧师\n长老',

        'A11': '2点15分',
        'B11': '殿乐',
        'D11': '司琴',
        'E11': '会众',
    }

    return gsheets_template
