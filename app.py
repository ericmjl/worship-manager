from flask import Flask, render_template, request, redirect
from tinydb import TinyDB, Query

app = Flask(__name__)
song_db = TinyDB('song.db')
coworker_db = TinyDB('coworker.db')
calendar_db = TinyDB('calendar.db')


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
    return render_template('song.html')


@app.route('/songs/save', methods=['POST'])
def save_song():
    data = {k: v for k, v in request.form.items()}
    song_db.insert(data)
    return redirect('/songs')


@app.route('/songs/<int:eid>/update/', methods=['POST'])
def update_song(eid):
    for k, v in request.form.items():
        song_db.update({k: v}, eids=[eid])
    return redirect('/songs')


@app.route('/songs/<int:eid>/view/')
def view_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


@app.route('/songs/<int:eid>/edit/')
def edit_song(eid):
    song = song_db.get(eid=eid)
    return render_template('song.html', song=song)


if __name__ == '__main__':
    app.run(debug=True, port=5678)
