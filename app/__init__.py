import os.path as osp

from flask import Flask, render_template

from tinydb import TinyDB

from .utils import makedir

from .views import coworkers, programs, songs

app = Flask(__name__)
app.register_blueprint(songs.mod)
app.register_blueprint(coworkers.mod)
app.register_blueprint(programs.mod)

datafolder = 'data/'

app.config['UPLOAD_FOLDER'] = osp.join(datafolder,
                                       'files/')
makedir(app.config['UPLOAD_FOLDER'])
dbfolder = osp.join(datafolder, 'database')
makedir(dbfolder)

song_db = TinyDB(osp.join(dbfolder, 'song.db'))


@app.route('/')
def home():
    return render_template('index.html.j2')
