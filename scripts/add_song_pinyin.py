"""
This file automatically adds the pinyin field to each song in the database.
"""

import os
import os.path as osp

import pinyin
from tinydb import TinyDB

filepath = os.path.dirname(os.path.realpath(__file__))
data_folder = osp.join(
    os.environ["HOME"], ".worship-manager", "data", "database"
)
song_db_path = f"{data_folder}/song.db"

song_db = TinyDB(song_db_path)

songs = song_db.all()
for song in songs:
    eid = song.eid
    name = song["name"]

    py = pinyin.get(name, format="strip", delimiter="")

    song_db.update({"pinyin": py}, eids=[eid])
