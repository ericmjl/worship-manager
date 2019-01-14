from dotenv import load_dotenv
import os
from .utils.db import connect
from pathlib import Path
import boto3
from hanziconv import HanziConv

# Project Root
# This is for loading local environment variables that we do not version
# place under version control. These have to be manually obtained from the
# heroku dashboard.
root = Path(".")
dotenv_path = root / ".env"
load_dotenv(dotenv_path, verbose=True)

# Instantiate connection to the database on Heroku
DB_URL = os.getenv("DATABASE_URL")
conn, cur = connect(DB_URL)

# Instantiate s3 bucket
s3 = boto3.resource("s3")
bucket = os.getenv("S3_BUCKET_NAME")

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
