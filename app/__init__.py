from flask import Flask, render_template

from .views import songs

app = Flask(__name__)
app.register_blueprint(songs.mod)
# Register other blueprints later.


@app.route('/')
def home():
    return render_template('index.html.j2')
