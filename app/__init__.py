from flask import Flask, render_template

from .views import coworkers, programs, songs

app = Flask(__name__)
app.register_blueprint(songs.mod)
app.register_blueprint(coworkers.mod)
app.register_blueprint(programs.mod)


@app.route('/')
def home():
    return render_template('index.html.j2')
