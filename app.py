from flask import Flask, render_template, request, redirect
from tinydb import TinyDB
from tinydb.operations import delete
from hanziconv import HanziConv
from datamodels import Song, Lyrics

app = Flask(__name__)
song_db = TinyDB('song.db')
coworker_db = TinyDB('coworker.db')
calendar_db = TinyDB('calendar.db')

hzc = HanziConv()

# Keep a list of song keys
song_datamodel = list(Song().to_dict().keys())


@app.route('/')
def home():
    return render_template('index.html')


def get_lyrics(data, exclude_id=None):
    """
    Utility function that returns a Lyrics object containing the song lyrics.

    Parameters:
    ===========
    - data: (dict-like) pass in `request.form` from Flask app.
    - exclude_id: (int) used in excluding a particular lyrics section.
    """
    # Defensive programming checks
    if exclude_id:
        assert isinstance(exclude_id, int)

    # Get lyrics
    l = Lyrics()
    for k, v in data.items():
        if 'section' in k:
            idx = int(k.split('-')[-1])
            if idx is not exclude_id:
                lyrics = hzc.toTraditional(request.form[f'lyrics-{idx}'])
                section = request.form[k]
                l.add_section(section=section,
                              lyrics=lyrics)
    return l


def update_song_info(request, eid, exclude_id=None):
    """
    Updates song information in database.

    Parameters:
    ===========
    - request: (dict-like) the `request` object from the Flask app.
    - eid: (int) the eid of the song to be updated in the database.
    """
    data = {k: hzc.toTraditional(v)
            for k, v in request.form.items()
            if k in song_datamodel}
    print(data)

    lyrics = get_lyrics(data=request.form, exclude_id=exclude_id)
    data['lyrics'] = lyrics.to_dict()
    song_db.update(data, eids=[eid])


@app.route('/songs', methods=['POST'])
@app.route('/songs')  # there are two paths to here.
def view_songs():
    all_songs = song_db.all()
    return render_template('songs.html', all_songs=all_songs)


@app.route('/songs/<int:eid>/view')
@app.route('/songs/<int:eid>')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/add', methods=['POST'])
@app.route('/songs/add')
def new_song():
    data = Song().to_dict()
    eid = song_db.insert(data)
    print(eid)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/save', methods=['POST'])
@app.route('/songs/<int:eid>/save')
def save_song(eid):
    update_song_info(request=request, eid=eid)
    return redirect('/songs')


@app.route('/songs/<int:eid>/remove', methods=['POST'])
def delete_song(eid):
    song_db.remove(eids=[eid])
    return redirect('/songs')


@app.route('/songs/<int:eid>/edit')
def edit_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/add_lyrics_section', methods=['POST'])
def add_lyrics_section(eid):
    """
    Adds a lyrics section to the song.
    """
    update_song_info(request=request, eid=eid)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=True)


@app.route('/songs/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.
    """
    update_song_info(request=request, eid=eid, exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/clean', methods=['POST'])
@app.route('/songs/clean')
def clean_songs_database():
    """
    Cleans every entry in the songs database to match the Songs datamodel.
    """
    all_songs = song_db.all()
    for s in all_songs:
        for k, v in s.items():
            if k == 'id':
                pass
            elif k not in song_datamodel:
                song_db.update(delete(k), eids=[s.eid])
    return redirect('/songs')


@app.route('/coworkers', methods=['POST'])
def view_coworkers():
    return render_template('coworkers.html')


@app.route('/coworkers/<int:id>/view', methods=['POST'])
def view_coworker(id):
    pass


@app.route('/coworkers/<int:id>/edit', methods=['POST'])
def edit_coworker(id):
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5678)
