from pathlib import Path
from dotenv import load_dotenv
import os
import boto3
from hanziconv import HanziConv
from functools import partial

root = Path(".")
dotenv_path = root / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path, verbose=True)

# Instantiate connection to the database on Heroku
DB_URL = os.getenv("DATABASE_URL")

# Instantiate s3 bucket
s3 = boto3.resource("s3")
bucket = os.getenv("S3_BUCKET_NAME")

# Commonly-used text conversion
hzc = HanziConv()
custom_mapping = {
    "祢": "祢",
    "袮": "祢",
    "面": "面",
    "麵": "面",
    "裡": "裡",
    "里": "裡",
    "裏": "裡",
    "傢": "家",
    "家": "家",
    "禰": "祢",
    "只": "只",
    "隻": "只",
    "衹": "只",
    "瞭": "了",
    "了": "了",
    "犧": "犠",
    "犠": "犠",
    "喔": "哦",
    "哦": "哦",
    "嚮": "向",
    "向": "向",
    "麽": "麼",
    "麼": "麼",
    "麯": "曲",
    "曲": "曲",
    "爲": "為",
    "為": "為",
    "齣": "出",
    "出": "出",
    "噹": "當",
    "當": "當",
    "当": "當",
    "迴": "回",
    "回": "回",
}

convert = partial(HanziConv.toTraditional, custom_mapping=custom_mapping)
