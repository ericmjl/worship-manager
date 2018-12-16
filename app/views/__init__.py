"""
This module contains elements commonly used across all of the other modules
under /views.
"""
from hanziconv import HanziConv

from tinydb import TinyDB

from pathlib import Path

# Commonly-used paths.
home = Path.home()
worship_dir = home / ".worship-manager"
data_dir = worship_dir / "data"
db_dir = data_dir / "database"
upload_dir = data_dir / "files"

# Common database objects.
song_db = TinyDB(db_dir / "song.db")
coworker_db = TinyDB(db_dir / "coworker.db")
program_db = TinyDB(db_dir / "program.db")

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
