import os.path as osp

import gspread

from ..static import gsheets_template


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

    credpath = osp.join(osp.dirname(osp.realpath(__file__)),
                        '..',
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
    pg1 = spreadsheet.worksheet('時間，程序，負責同工，與參與團隊')

    for cell, value in gsheets_template().items():
        pg1.update_acell(cell, value)


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
        spreadsheet.share('ericmajinglong@gmail.com',
                          perm_type='user',
                          role='writer')
        # spreadsheet.share('amenda860111@gmail.com',
        #                   perm_type='user',
        #                   role='writer')
    update_spreadsheet(spreadsheet)
    return spreadsheet


def delete_spreadsheet(gc, eid, program_db):
    """
    Deletes the particular spreadsheet.
    """
    program = program_db.get(eid=eid)
    try:
        gc.del_spreadsheet(program['gsheets'])
    except:
        pass
    program_db.update({'gsheets': ''}, eids=[eid])
