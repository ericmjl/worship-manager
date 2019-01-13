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

import psycopg2

from ..utils.dbutils import connect


# Project Root
# This is for loading local environment variables that we do not version
# place under version control. These have to be manually obtained from the
# heroku dashboard.
root = Path('.')
dotenv_path = root / '.env'
load_dotenv(dotenv_path, verbose=True)

# Instantiate connection to Database
DB_URL = os.getenv("DATABASE_URL")
conn, cur = connect(DB_URL)

# Commonly-used paths.
# 2019-01-12: I don't think the following are necessary.
###### UNNECESSARY START ######
# home = Path.home()
# worship_dir = home / ".worship-manager"
# data_dir = worship_dir / "data"
# data_dir.mkdir(parents=True, exist_ok=True)

# db_dir = data_dir / "database"
# db_dir.mkdir(parents=True, exist_ok=True)

# upload_dir = data_dir / "files"
# upload_dir.mkdir(parents=True, exist_ok=True)

# db_path = db_dir / "song.db"
###### UNNECESSARY END ######

# Instantiate s3 bucket
s3 = boto3.resource("s3")
bucket = os.getenv("S3_BUCKET_NAME")

###### UNNECESSARY START ######
# s3.Bucket(bucket).download_file("song.db", str(db_path))

# # Common database objects.
# song_db = TinyDB(db_path)
###### UNNECESSARY END ######

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
