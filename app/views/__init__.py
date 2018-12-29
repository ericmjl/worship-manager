"""
This module contains elements commonly used across all of the other modules
under /views.
"""
from hanziconv import HanziConv

from tinydb import TinyDB

from pathlib import Path

import boto3
import os


# Commonly-used paths.
home = Path.home()
worship_dir = home / ".worship-manager"
data_dir = worship_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)

db_dir = data_dir / "database"
db_dir.mkdir(parents=True, exist_ok=True)

upload_dir = data_dir / "files"
upload_dir.mkdir(parents=True, exist_ok=True)

# Get song database from S3.
s3 = boto3.resource("s3")
bucket = os.environ["S3_BUCKET_NAME"]
s3.Bucket(bucket).download_file("song.db", str(db_dir / "song.db"))

# Common database objects.
song_db = TinyDB(db_dir / "song.db")

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
