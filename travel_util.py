#!/bin/python
# travel_util.py: utilities for travel.py

import datetime
import json
import travel
import os.path
import shutil


def convert_db_to_23(tour_path):
    ''' Convert db versions lower than 2.3 to new format

    keyword arguments:
    tour: str: complete path to db

    returns None
    '''
    with open(tour_path, 'r', encoding='utf-8') as f:
        tourData = json.load(f)

    tour = tourData['tour']
    if float(tour['version']) < 2.3:
        # Make a backup of databasefile
        shutil.copy(tour_path, tour_path + '.old')
        print(':: Originele database file opgeslagen als {}'.format(tour_path + '.old'))
        print(':: Converteren...')
        tour['start_datum'] = datetime.date.fromordinal(int(tour['start_datum']))
        tour['eind_datum'] = datetime.date.fromordinal(int(tour['eind_datum']))
        if tour['nieuw_record']:
            tour['nieuw_record'] = datetime.date.fromordinal( \
                    int(tour['nieuw_record']))
        tour['version'] = '2.3'
        travel.save_tour(tourData, os.path.dirname(tour_path))
    else:
        print(':: Deze database is versie {} en heeft dus geen conversie naar \
               2.3 nodig.'.format(tour['version']))


if __name__ == '__main__':
    conf = travel.open_config('/home/jerry/.config/travel.conf')
    dbName = input('Naam van de te converteren database \
                    (als in --show-tours): ') + '.json'
    dbPath = os.path.join(conf['data_dir'], dbName)
    convert_db_to_23(dbPath)
