from pathlib import Path
from dotenv import load_dotenv
import os
import boto3
from hanziconv import HanziConv

root = Path(".")
dotenv_path = root / ".env"
load_dotenv(dotenv_path, verbose=True)

# Instantiate connection to the database on Heroku
DB_URL = os.getenv("DATABASE_URL")

# Instantiate s3 bucket
s3 = boto3.resource("s3")
bucket = os.getenv("S3_BUCKET_NAME")

# Commonly-used text conversion
hzc = HanziConv()
convert = hzc.toTraditional
