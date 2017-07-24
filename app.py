from flask import Flask, render_template, request, redirect
from tinydb import TinyDB
from hanziconv import HanziConv
from datamodels import Lyrics
from validation import validate_song

app = Flask(__name__)
song_db = TinyDB('song.db')
coworker_db = TinyDB('coworker.db')
calendar_db = TinyDB('calendar.db')

hzc = HanziConv()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/coworkers', methods=['POST'])
def view_coworkers():
    return render_template('coworkers.html')


@app.route('/coworkers/<int:id>/view/', methods=['POST'])
def view_coworker(id):
    pass


@app.route('/coworkers/<int:id>/edit/', methods=['POST'])
def edit_coworker(id):
    pass


@app.route('/songs', methods=['POST'])
@app.route('/songs')  # there are two paths to here.
def view_songs():
    all_songs = song_db.all()
    return render_template('songs.html', all_songs=all_songs)


@app.route('/songs/add', methods=['POST'])
def new_song():
    data = dict()
    eid = song_db.insert(data)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/save', methods=['POST'])
def save_song():
    data = {k: hzc.toTraditional(v) for k, v in request.form.items()}
    try:
        assert data['name'] is not '' and data['source'] is not ''
        song_db.insert(data)
    except AssertionError:
        # We silently pass if 'name' and 'source' are not filled in.
        pass
    return redirect('/songs')



def update_song_info(eid, exclude_id=None):
    # Validation
    data = {k: v for k, v in request.form.items()}

    l = Lyrics()
    for k, v in data.items():
        if 'section' not in k or 'lyrics' not in k:
            song_db.update({k: hzc.toTraditional(v)}, eids=[eid])
        # This conditional checks that we have sections that we want to keep.
        if 'section' in k and int(k.split('-')[-1]) is not exclude_id:
            l.add_section(request.form[k],
                          request.form[f'lyrics-{k.split("-")[-1]}'])
    song_db.update({'lyrics': l.sections}, eids=[eid])


@app.route('/songs/<int:eid>/update/', methods=['POST'])
def update_song(eid):
    update_song_info(eid)
    return redirect('/songs')


@app.route('/songs/<int:eid>/add_lyrics_section/', methods=['POST'])
def add_lyrics_section(eid):
    """
    Adds a lyrics section to the song.
    """
    update_song_info(eid)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=True)


@app.route('/songs/<int:eid>/remove_lyrics_section/<int:section_id>',
           methods=['POST'])
def remove_lyrics_section(eid, section_id):
    """
    Removes a lyric section from the song.
    """
    print(eid, section_id)
    update_song_info(eid, exclude_id=section_id)
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/<int:eid>/remove/', methods=['POST'])
def delete_song(eid):
    song_db.remove(eids=[eid])
    return redirect('/songs')


@app.route('/songs/<int:eid>/view/')
@app.route('/songs/<int:eid>/')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song, add_section=False)


@app.route('/songs/<int:eid>/edit/')
def edit_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


if __name__ == '__main__':
    app.run(debug=True, port=5678)
