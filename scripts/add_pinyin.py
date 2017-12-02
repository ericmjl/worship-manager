"""
This file automatically adds the pinyin field to each el in the database.
"""
import click
import os
import os.path as osp
import logging

import pinyin
from tinydb import TinyDB

@click.command()
@click.option('--db', help="The database to add pinyin.", type=click.Choice(['coworker', 'song']))
def main(db):
    filepath = os.path.dirname(os.path.realpath(__file__))
    data_folder = osp.join(
        os.environ['HOME'], '.worship-manager', 'data', 'database')
    db_path = f'{data_folder}/{db}.db'
    db = TinyDB(db_path)
    els = db.all()  # els = "elements"
    
    for el in els:
        eid = el.eid
        name = el['name']
        py = pinyin.get(name, format='strip', delimiter='')
        db.update({'pinyin': py}, eids=[eid])

    print(db.all())


if __name__ == '__main__':
    main()
