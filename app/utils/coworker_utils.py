from tinydb import Query

from ..views import convert


def search_coworkers_db(term, db):
    """
    Searches the coworkers database.

    :param term: Search term for the database.
    :type term: str

    :param db: The database object containing the coworkers database.
    :type db: `tinydb.TinyDB` object.

    :returns: `filtered_coworkers` or `all_coworkers`, an iterable of
              dictionaries, in which each dictionary is one entry in the
              database.
    :rtype: `iterable(dict)`
    """
    filtered_coworkers = list()
    all_coworkers = db.all()
    if term:
        for coworker in all_coworkers:
            for k, v in coworker.items():
                # print(k, v)
                if k == 'service':
                    for srvc in v:
                        if (srvc
                                and term in srvc
                                and coworker not in filtered_coworkers):
                            filtered_coworkers.append(coworker)
                else:
                    if (v
                            and hasattr(v, '__iter__')
                            and term in v
                            and coworker not in filtered_coworkers):
                        filtered_coworkers.append(coworker)
        return filtered_coworkers
    else:
        return all_coworkers


def get_grouped_coworkers(coworker_db):
    """
    Gets coworkers grouped together by their type.

    .. note:: This is a very hacky function. If the coworkers' datamodel
              changes, this needs to be updated as well.

    :param coworker_db: The coworker database.
    :type coworker_db: `tinydb.TinyDB()`

    :returns: `coworkers` (`dict`)
    """
    p = Query()
    coworkers = dict()
    coworkers['presiders'] = coworker_db.search(p.service.any(['presider']))
    coworkers['vocalists'] = coworker_db.search(p.service.any(['vocalist']))
    coworkers['pianists'] = coworker_db.search(p.service.any(['pianist']))
    coworkers['speakers'] = coworker_db.search(p.service.any(['speaker']))
    coworkers['audios'] = coworker_db.search(p.service.any(['audio']))
    coworkers['powerpoints'] = coworker_db.search(p.service.any(['powerpoint']))  # noqa
    coworkers['guitarists'] = coworker_db.search(p.service.any(['guitarist']))
    coworkers['drummers'] = coworker_db.search(p.service.any(['drummer']))

    return coworkers


def update_coworker_info(request, eid, coworker_db):
    """
    Updates coworker information in database.

    :param request: `request` object from the Flask app.
    :type request: `flask.request` object, `dict`-like.

    :param eid: the eid of the coworker to be updated in the database.
    :type eid: `int`
    """
    data = {k: convert(v) for k, v in request.form.items() if k != 'service'}
    data['service'] = []
    data['pinyin'] = pinyin.get(data['name'], format="strip", delimiter=" ")
    # print(request.form.getlist('service'))
    for serv in request.form.getlist('service'):
        data['service'].append(serv)
    coworker_db.update(data, eids=[eid])
