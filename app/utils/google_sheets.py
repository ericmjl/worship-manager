import os
import os.path as osp

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from ..static import (gsheets_template, standard_program_roles,
                      standard_program_songs)
from ..views import coworker_db, program_db, song_db


def authorize_google_sheets():
    """
    Connects the app to Google Sheets.

    Assumes that there is a `credentials.json` file in the same directory as
    `run.py`.

    :example:
    >>> gc = authorize_google_sheets()

    :returns: `gc` (`gspread.Client` object). Use this object around the app.
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credpath = osp.join(os.environ['HOME'],
                        '.worship-manager',
                        'credentials.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credpath, scope)  # noqa
    gc = gspread.authorize(credentials)

    return gc


def update_spreadsheet(spreadsheet, program):
    """
    Highly customized function...

    :param spreadsheet: A gspread Spreadsheet object. This is the spreadsheet
        that is to be updated.
    :type spreadsheet: `gspread.Spreadsheet` object.

    :param program: A TinyDB record from the program database.
    :type program: dict
    """
    # --------- Set up some commonly-used stuff first. --------- #
    avail_data = dict()

    # Get the names of coworkers
    for role in standard_program_roles():
        if role in program.keys() and program[role]:
            avail_data[role] = coworker_db.get(eid=int(program[role]))

    # Get the names of songs
    for song in standard_program_songs():
        if song in program.keys() and program[song]:
            avail_data[song] = song_db.get(eid=int(program[song]))

    # Get the song data (particularly arrangements.)
    song_string = ''  # this song string is entered into line C4 of pg1.
    if 'song1' in avail_data.keys():
        song_string += avail_data['song1']['name'] + '\n'   # note: pg1 cell C4
        avail_data['song1']['arrangement'] = program['song1_arrangement']
    if 'song2' in avail_data.keys():
        song_string += avail_data['song2']['name'] + '\n'  # note: pg1 cell C4
        avail_data['song2']['arrangement'] = program['song2_arrangement']
    if 'song3' in avail_data.keys():
        song_string += avail_data['song3']['name']  # note: pg1 cell C4
        avail_data['song3']['arrangement'] = program['song3_arrangement']
    if 'offering' in avail_data.keys():
        avail_data['offering']['arrangement'] = program['offering_arrangement']
    if 'response' in avail_data.keys():
        avail_data['response']['arrangement'] = program['response_arrangement']

    # --------- This section is for Page 1 of the spreadsheet. --------- #
    pg1 = spreadsheet.worksheet('時間，程序，負責同工，與參與團隊')

    for cell, value in gsheets_template().items():
        pg1.update_acell(cell, value)

    update_data = {
        'D2': avail_data['pianist']['name'],
        'D3': avail_data['presider']['name'],
        'C4': song_string,
        'C5': avail_data['offering']['name'],
        'D5': avail_data['presider']['name'],
        'D6': avail_data['presider']['name'],
        'D7': avail_data['speaker']['name'],
        'D8': avail_data['speaker']['name'],
        'D11': avail_data['pianist']['name']
    }

    for cell, value in update_data.items():
        pg1.update_acell(cell, value)

    # --------- This section is for Page 2 of the spreadsheet. --------- #
    pg2 = spreadsheet.worksheet('敬拜詩歌')

    pg2_data = {
        "A1": '詩歌',
        "A2": "編排",
        "A6": "詞、曲",
        "A7": "版權",
        "A9": "歌詞",
    }
    for cell, value in pg2_data.items():
        pg2.update_acell(cell, value)

    def add_song_to_sheet(song, column):
        song_data = {
            f"{column}1": f"{song} " + avail_data[song]['name'],
            f"{column}2": avail_data[song]['arrangement'],
            f"{column}6": avail_data[song]['composer'],
            f"{column}7": avail_data[song]['copyright'],
        }

        idx = 9  # start at row 9 in the spreadsheet for the lyrics.
        for section, lyrics in avail_data[song]['lyrics'].items():
            key = f"{column}{idx}"
            val = section
            song_data.update({key: val})
            for l in lyrics.split('\n'):
                idx += 1
                key = f"{column}{idx}"
                song_data.update({key: l.strip('\r')})
            idx += 2
        print(song_data)

        for cell, value in song_data.items():
            pg2.update_acell(cell, value)

    add_song_to_sheet('song1', column='B')
    add_song_to_sheet('song2', column='C')
    add_song_to_sheet('song3', column='D')
    add_song_to_sheet('offering', column='E')
    add_song_to_sheet('response', column='F')

    # --------- This section is for Page 3 of the worksheet. --------- #


def create_gsheet(gc, eid, program_db):
    """
    Creates a Google sheet for the program.

    :param gc: The `gspread.Client` object. Should have called
        `gc = authorize_google_sheets()` before passing into this function.
    :type gc: `gspread.Client` object

    :param eid: The eid of the program.
    :type eid: int

    :param program_db: The program database object.
    :type program_db: `tindyb.TinyDB()` database.
    """
    program = program_db.get(eid=eid)
    year, month, day = program['date'].split('-')
    gsname = f'城區主日崇拜程序 - 主後{year}年{month}月{day}日'  # gsname means "google spreadsheet name"  # noqa
    try:
        spreadsheet = gc.open(gsname)
    except gspread.SpreadsheetNotFound:
        spreadsheet = gc.create(gsname)
        spreadsheet.add_worksheet('時間，程序，負責同工，與參與團隊', rows=200, cols=15)  # noqa
        spreadsheet.add_worksheet('敬拜詩歌', rows=200, cols=10)
        spreadsheet.add_worksheet('宣召 (Invocation)', rows=50, cols=2)
        spreadsheet.add_worksheet('奉獻詩歌&歡迎歌', rows=20, cols=4)
        try:
            ws = spreadsheet.worksheet('Sheet1')
            spreadsheet.del_worksheet(ws)
        except gspread.exceptions.WorksheetNotFound:
            pass
    spreadsheet.share('ericmajinglong@gmail.com',
                      perm_type='user',
                      role='writer')
    # spreadsheet.share('amenda860111@gmail.com',
    #                   perm_type='user',
    #                   role='writer')
    update_spreadsheet(spreadsheet, program)
    return spreadsheet


def delete_gsheet(gc, eid, program_db):
    """
    Deletes the particular spreadsheet.
    """
    program = program_db.get(eid=eid)
    try:
        gc.del_spreadsheet(program['gsheets'])
    except:  # noqa
        pass
    program_db.update({'gsheets': ''}, eids=[eid])
