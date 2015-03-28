#!/bin/python
#travel_util.py: utilities for travel.py

import datetime
import json
import travel
import os.path


def convert_db_to_23(tour_path):
    ''' Convert db versions lower than 2.3 to new format

    keyword arguments:
    tour: str: complete path to db

    returns None
    '''
    with open(tour_path, 'r', encoding='utf-8') as f:
        tourData = json.load(f)

    tour = tourData['tour']
    tour['start_datum'] = datetime.date.fromordinal(int(tour['start_datum']))
    tour['eind_datum'] = datetime.date.fromordinal(int(tour['eind_datum'])) 
    if tour['nieuw_record']:
        tour['nieuw_record'] = datetime.date.fromordinal(int(tour['nieuw_record'])) 
    tour['version'] = '2.3'

    travel.save_tour(tourData, os.path.dirname(tour_path))

