"""
This module contains elements commonly used across all of the other modules
under /views.
"""
from hanziconv import HanziConv

from tinydb import TinyDB

from pathlib import Path

import boto3
import os
from dotenv import load_dotenv

# Project Root
root = Path('.')
dotenv_path = root / '.env'
load_dotenv(dotenv_path, verbose=True)

# Commonly-used paths.
home = Path.home()
worship_dir = home / ".worship-manager"
data_dir = worship_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)

db_dir = data_dir / "database"
db_dir.mkdir(parents=True, exist_ok=True)

upload_dir = data_dir / "files"
upload_dir.mkdir(parents=True, exist_ok=True)

db_path = db_dir / "song.db"

# Get song database from S3.
s3 = boto3.resource("s3")
bucket = os.getenv("S3_BUCKET_NAME")
s3.Bucket(bucket).download_file("song.db", str(db_path))

# Common database objects.
song_db = TinyDB(db_path)

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
