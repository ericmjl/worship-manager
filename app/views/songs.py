from flask.blueprints import Blueprint
from sqlalchemy.dialects.postgresql import JSON


songs = Blueprint("songs", __name__, url_prefix="/songs")
