"""
This file automatically adds the pinyin field to each song in the database.
"""

import os

from tinydb import TinyDB


filepath = os.path.dirname(os.path.realpath(__file__))
program_db_path = f'{filepath}/../data/database/program.db'

program_db = TinyDB(program_db_path)

programs = program_db.all()
for song in programs:
    eid = song.eid
    program_db.update({'response': ''}, eids=[eid])
