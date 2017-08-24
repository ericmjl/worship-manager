from flask import Blueprint, redirect, render_template, request

from .__init__ import convert, coworker_db

from ..datamodels import Coworker

from ..static import fellowships, genders, service

from ..utils import search_coworkers_db, update_coworker_info

mod = Blueprint('coworkers', __name__, url_prefix='/coworkers')


@mod.route('/', methods=['POST'])
@mod.route('/')
def view_all():
    all_coworkers = coworker_db.all()
    return render_template('coworkers.html.j2',
                           all_coworkers=all_coworkers,
                           service=service())


@mod.route('/add', methods=['POST'])
@mod.route('/add')
def new():
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
    update_coworker_info(request=request, eid=eid, coworker_db=coworker_db)
    return redirect('/coworkers')


@mod.route('/<int:eid>/view', methods=['POST'])
@mod.route('/<int:eid>/view')
@mod.route('/<int:eid>/edit', methods=['POST'])
@mod.route('/<int:eid>/edit')
def view(eid):
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
    coworker_db.remove(eids=[eid])
    return redirect('/coworkers/')
