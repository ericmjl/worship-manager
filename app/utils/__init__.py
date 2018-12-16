import os

from ..datamodels import Song

# Keep a list of song keys
song_datamodel = list(Song().to_dict().keys())

# We only allow uploading of PDFs.
ALLOWED_EXTENSIONS = set(["pdf"])


def makedir(path):
    """
    Creates a path if it doesn't already exist.

    :param path: Path to be created.
    :type path: `str`
    """
    if not os.path.exists(path):
        os.makedirs(path)
