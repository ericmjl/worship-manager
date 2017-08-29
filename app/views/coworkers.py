from flask import Blueprint, redirect, render_template, request

from .__init__ import convert, coworker_db

from ..datamodels import Coworker

from ..static import fellowships, genders, service

from ..utils.coworker_utils import search_coworkers_db, update_coworker_info

mod = Blueprint('coworkers', __name__, url_prefix='/coworkers')


@mod.route('/', methods=['POST'])
@mod.route('/')
def view_all():
    """
    Master view for all coworkers in the database.

    :returns: Renders an HTML table of all coworkers.
    """
    all_coworkers = coworker_db.all()
    return render_template('coworkers.html.j2',
                           all_coworkers=all_coworkers,
                           service=service())


@mod.route('/add', methods=['POST'])
@mod.route('/add')
def new():
    """
    Adds a new coworker to the database. To ensure that the coworker is entered
    into the database, we first create the coworker in the db, and then return
    the empty information to Jinja, including the eid. In this way, we are
    guaranteed an eid for the `/save` function (below).
    """
    data = Coworker().to_dict()
    eid = coworker_db.insert(data)
    coworker = coworker_db.get(eid=eid)
    return render_template('coworker.html.j2',
                           coworker=coworker,
                           fellowships=fellowships(),
                           service=service(),
                           genders=genders())


@mod.route('/<int:eid>/save', methods=['POST'])
@mod.route('/<int:eid>/save')
def save(eid):
    """
    Saves the coworker to the database. This function calls on the
    `app.utils.update_coworker_info` function.

    :param eid: The `eid` of the song to be saved.
    :type eid: int

    :returns: Redirects to the `/coworkers/` page (master table).
    """
    update_coworker_info(request=request, eid=eid, coworker_db=coworker_db)
    return redirect('/coworkers')


@mod.route('/<int:eid>/view', methods=['POST'])
@mod.route('/<int:eid>/view')
@mod.route('/<int:eid>/edit', methods=['POST'])
@mod.route('/<int:eid>/edit')
@mod.route('/<int:eid>')
def view(eid):
    """
    Displays a page to view a particular coworker. The view page doubles up as
    the edit page as well.

    :param eid: The eid of the coworker in the database.
    :type eid: int
    """
    coworker = coworker_db.get(eid=eid)
    return render_template('coworker.html.j2',
                           coworker=coworker,
                           fellowships=fellowships(),
                           service=service(),
                           genders=genders())


@mod.route('/search', methods=['POST'])
@mod.route('/search')
@mod.route('/search/<term>')
def search(term=None):
    """
    Search function for songs in the database. Performs a strict substring
    search by calling on `app.utils.search_coworkers_db`.

    :param term: The search term.
    :type term: str

    :returns: Renders an HTML table of coworkers.
    """
    if term:
        pass
    elif request.form['search']:
        term = convert(request.form['search'])
    # Perform a search of all key/value pairs in the database.
    filtered_coworkers = search_coworkers_db(term, coworker_db)
    return render_template('coworkers.html.j2',
                           all_coworkers=filtered_coworkers,
                           term=term,
                           service=service())


@mod.route('/<int:eid>/remove', methods=['POST'])
@mod.route('/<int:eid>/remove')
def remove(eid):
    """
    Removes a song from the database.

    :param eid: The eid of the song to be removed.
    :type eid: int
    """
    coworker_db.remove(eids=[eid])
    return redirect('/coworkers/')
