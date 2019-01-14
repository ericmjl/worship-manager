import base64
import json
import os
import uuid
from pathlib import Path

import boto3
import yaml
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
)
# from preview_generator.manager import PreviewManager
from tinydb.operations import delete

from ..utils.song_utils import (
    allowed_file,
    clean_arrangement,
    get_one_song,
    update_song_info,
)
from ..config import conn, cur

mod = Blueprint("songs", __name__, url_prefix="/songs")

# manager = PreviewManager("/tmp/cache/", create_folder=True)


@mod.route("/")
def view_all():
    """
    Master view for all songs in the database.

    :returns: Renders an HTML table of songs.
    """
    cur.execute("SELECT * FROM songs")
    all_songs = cur.fetchall()
    return render_template("songs.html.j2", all_songs=all_songs)


@mod.route("/<int:id>")
def view(id):
    """
    Displays a page to view a particular song. The view page doubles up as the
    edit page as well.

    :param int id: The id of the song in the database.
    :returns: Renders the view page for a single song.
    """
    song = get_one_song(id)
    return render_template("song.html.j2", song=song)


@mod.route("/add")
def new():
    """
    Adds a new song to the database. To ensure that the song is entered into
    the database, we first create the song in the db, and then return the empty
    information to Jinja, including the `id`. In this way, we are guaranteed
    an `id` for the `/save` function (below).

    :returns: Renders the view page for a new song, but under the url path
              /add.
    """
    # data = Song().to_dict()
    # id = song_db.insert(data)
    # song = song_db.get(id=id)
    return render_template("song.html.j2", song=song)


@mod.route("/<int:id>/save", methods=["POST"])
def save(id):
    """
    Saves the song to the database. This function calls on the
    `app.utils.update_song_info` function.

    Also refreshes the database on s3.

    :param id: The id of the song to be saved.
    :type id: int

    :returns: Redirects to the `/songs/` page (master table).
    """

    update_song_info(request, id=id, cur=cur, conn=conn)
    # s3ul(str(db_path), "song.db")
    return redirect("/songs/")


@mod.route("/<int:id>/update", methods=["POST"])
def update(id):
    """
    Updates the song information to the database. In contrast to `save(id)`,
    this function will come back to the song page.

    :param id: The id of the song to be updated.
    :type id: int

    :returns: Renders the view page for the song that was updated.
    """
    update_song_info(request, id=id, cur=cur, conn=conn)
    song = get_one_song(id)
    return render_template("song.html.j2", song=song)


@mod.route("/<int:id>/remove")
def remove(id):
    """
    Removes a song from the database.

    :param id: The id of the song to be removed.
    :type id: int

    :returns: Redirects to the `/songs/` page (master table).
    """
    song_db.remove(ids=[id])
    return redirect("/songs/")


@mod.route("/<int:id>/add_lyrics_section", methods=["POST"])
def add_lyrics_section(id):
    """
    Adds a lyrics section to the song.

    :param id: The id of the song to add a lyrics section to.
    :type id: int

    :returns: Renders the view page for a song, but with an added lyrics
              section to the song.
    """
    update_song_info(request, id=id, cur=cur, conn=conn)
    song = get_one_song(id=id)
    sect_ct = len(song["lyrics"]) + 1
    # print(sect_ct)
    song["lyrics"][f"section-{sect_ct}"] = f"lyrics-{sect_ct}"
    return render_template("song.html.j2", song=song)


@mod.route(
    "/<int:id>/remove_lyrics_section/<int:section_id>", methods=["POST"]
)
def remove_lyrics_section(id, section_id):
    """
    Removes a lyric section from the song.

    :param id: The id of the song to remove a section from.
    :type id: int

    :param section_id: The section ID to be removed.
    :type section_id: str

    .. note:: `section_id` comes from the HTML form that is submitted. It
              should be of the form `section-1` or `section-2` (for example).

    :returns: Renders the view page for the song, but with the indicated
              section removed.
    """
    update_song_info(request, id=id, cur=cur, conn=conn, exclude_id=section_id)
    song = get_one_song(id)
    return render_template("song.html.j2", song=song)


@mod.route("/<int:id>/sheet_music/upload", methods=["POST"])
def upload_sheet_music(id):
    """
    Uploads a PDF of the sheet music for the song.

    :param id: The id of the song for which a sheet music is to be attached.
    :type id: int

    .. note:: The only acceptable upload formats are indicated in
              `app.utils.ALLOWED_EXTENSIONS`.

    :returns: The view page for the song.
    """

    if "file-upload" not in request.files:
        flash("No file part")
        return redirect(f"/songs/{id}")
    f = request.files["file-upload"]

    if f.filename == "":
        flash("No selected file")
        return redirect(f"/songs/{id}")

    if f and allowed_file(f.filename):
        # Compute the song filename.
        fname = f"{str(uuid.uuid4())}.pdf"
        # Save the file to disk temporarily.
        fpath = str(upload_dir / fname)
        f.save(fpath)

        # Save the file to S3
        s3ul(fpath, fname)
        # Update the song database
        song_db.update({"sheet_music": fname}, ids=[id])
        # Redirect to preview generator, which will then generate the preview.
        # This will then redirect back to the original.
        return redirect(f"/songs/{id}/preview")


@mod.route("/<int:id>/sheet_music/download")
def download_sheet_music(id):
    """
    Returns the sheet music to be downloaded.

    :param id: The id of the song.
    :type id: int

    :returns: The song sheet PDF.
    """
    song = get_one_song(id)
    fname = song["sheet_music"]
    # Use s3dl utility function to conditionally download file.
    s3dl(fname)

    # Change the name of the file so that it is easier to read.
    new_fname = f'{song["name"]}-{song["composer"]}-{song["copyright"]}.pdf'
    os.system(f"cp /tmp/{fname} /tmp/{new_fname}")

    # Return the file.
    return send_file(f"/tmp/{new_fname}", as_attachment=True)


@mod.route("/<int:id>/sheet_music/delete")
def delete_sheet_music(id):
    """
    Deletes the sheet music from the song.

    .. note:: The file on disk is not actually removed; only the file path
              recorded in the database is. This is an intentional choice during
              development, to prevent data losses from happening. Before going
              into production, this should be changed.

    .. todo:: Make sure to fix the problem indicated in the note above.

    :param id: The id of the song to remove sheet music from.
    :type id: int
    """
    song_db.update(delete("sheet_music"), ids=[id])
    return redirect(f"/songs/{id}")


@mod.route("/clean")
def clean_database():
    """
    Cleans every entry in the songs database to match the Songs datamodel.

    :returns: Renders the master songs page.
    """
    all_songs = song_db.all()
    for s in all_songs:
        for k, v in s.items():
            if k == "id":
                pass
            elif k not in song_datamodel:
                song_db.update(delete(k), ids=[s.id])
    return redirect("/songs/")


@mod.route("/export")
def export_database():
    """
    Exports the songs database as a YAML file.

    .. note:: We do a YAML dump because this makes it easier for humans to read
              compared to a JSON file without necessary whitespace.

    :returns: a YAML dump of the database.
    """
    with open("song.db", "r+") as f:
        data = json.load(f)
    return yaml.dump(data, default_flow_style=False)


@mod.route("/<int:id>/slides")
def view_slides(id):
    """
    Creates `reveal.js` slides for the song of interest, using the default
    arrangement specified in the song's database entry.

    :param id: The id of the song to create slides for.
    :type id: int

    :returns: Renders the HTML slides for that song.
    """
    cur.execute(f"SELECT * FROM songs WHERE id={id}")
    song = cur.fetchone()
    arrangement = clean_arrangement(song["default_arrangement"])
    return render_template(
        "slides_single_song.html.j2", song=song, arrangement=arrangement, id=id
    )


@mod.route("/<int:id>/export")
def export_lyrics(id):
    """
    View function for lyrics export.
    """
    cur.execute(f"SELECT * FROM songs WHERE id={id}")
    song = cur.fetchone()
    output = lyrics_plaintext(song)
    return render_template("song_export.html.j2", output=output)


def lyrics_plaintext(song):
    """
    Get lyrics as plaintext.
    """
    output = ""

    output += song["default_arrangement"]
    output += "\n\n\n\n"
    output += song["composer"]
    output += "\n"
    output += song["copyright"]
    output += "\n\n"

    for section, lyrics in song["lyrics"].items():
        output += section
        output += "\n"
        output += lyrics
        output += "\n\n"
    return output


def generate_songsheet_preview(fpath, song_db, id):
    """
    Generates a JPEG preview of the sheet music, and stores it as a
    base64-encoded string in the database.
    """
    # Generate preview of the file
    thumbnail_file_path = manager.get_jpeg_preview(fpath, height=400)
    # Base64 encode image for preview purposes
    with open(thumbnail_file_path, "rb") as thumbnail:
        encoded = base64.b64encode(thumbnail.read())

    # Save b64-encoded image to the database.
    song_db.update({"pdf_preview": encoded.decode()}, ids=[id])


@mod.route("/<int:id>/preview")
def songsheet_preview(id):
    """
    Generates a JPEG preview for each file.
    """
    cur.execute(f"SELECT * FROM songs WHERE id={id}")
    song = cur.fetchone()
    fname = song["sheet_music"]
    # Use s3dl utility function to conditionally download file.
    s3dl(fname)
    fpath = f"/tmp/{fname}"
    generate_songsheet_preview(fpath, song_db, id)
    return redirect(f"/songs/{id}")


# @mod.route('/<int:id>/update_filename')
# def update_filename(id):
#     song = song_db.get(id=id)
#     old_fname = song["sheet_music"]
#     new_fname = f'{song["name"]}-{song["composer"]}-{song["copyright"]}.pdf'
#     song_db.update({"sheet_music": new_fname})
#     s3rename(old_fname, new_fname)
#     return redirect(f"/songs/{id}")


"""
Below are a bunch of s3-specific utility functions. I may refactor them
out at a later date.
"""


def s3bucket():
    s3 = boto3.resource("s3")
    bucket = os.environ["S3_BUCKET_NAME"]
    return s3.Bucket(bucket)


def s3dl(fname):
    """
    Downloads a file from S3. Does this conditionally; if the file already
    exists, then we do not download it.

    Does not return anything
    """
    pathstr = f"/tmp/{fname}"
    if not Path(pathstr).exists():
        s3bucket().download_file(fname, f"/tmp/{fname}")


def s3ul(fpath, fname):
    """
    Uploads a file to S3.
    """
    s3bucket().upload_file(fpath, fname, ExtraArgs={"ACL": "public-read"})


def s3del(fname):
    """
    Deletes a file from s3.
    """
    s3bucket().delete_objects(Delete={"Objects": [{"Key": fname}]})


def s3rename(old, new):
    """
    Renames a file on s3.
    """
    s3dl(old)
    s3ul(f"/tmp/{old}", new)
    s3del(old)
