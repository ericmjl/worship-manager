"""
This module contains elements commonly used across all of the other modules
under /views.
"""
import os
import os.path as osp

from hanziconv import HanziConv

from tinydb import TinyDB

# Commonly-used paths.
data_folder = osp.join(os.environ['HOME'], '.worship-manager', 'data')
db_folder = osp.join(data_folder, 'database')
upload_folder = osp.join(data_folder, 'files')  # upload folder

# Common database objects.
song_db = TinyDB(osp.join(db_folder, 'song.db'))
coworker_db = TinyDB(osp.join(db_folder, 'coworker.db'))
program_db = TinyDB(osp.join(db_folder, 'program.db'))

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
