#!/bin/python
# traveldb.py
# Database voor travel

import json
import os
import datetime
import json_serializer


version = '1.0'


class DatumError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        repr(self.value)


def validate_datum(datum):
    '''valideert en vult een datum aan.
    als dag of maand-dag wordt gegeven,
    wordt het aangevuld met de huidige datum

    keyword arguments:
    datum: string in formaat YYYY-MM-DD, MM-DD, DD

    return date
    '''
    td = datetime.date.today()
    if datum == '':
        # Geen input dus vandaag returnen
        return td
    datumList = [int(x) for x in datum.split('-')]
    if len(datumList) == 1:
        return td.replace(day=datumList[0])
    elif len(datumList) == 2:
        return td.replace(day=datumList[1],
                          month=datumList[0])
    elif len(datumList) == 3:
        return td.replace(day=datumList[2],
                          month=datumList[1],
                          year=datumList[0])
    else:
        raise DatumError('DatumError: Verkeerd datumformaat. \ 
                Correcte input is: YYYY-[M]M-[D]D, [M]M-[]DD, [D]D')


def new_tour(name):
    ''' Creeert een nieuwe database.
    
    keyword arguments:
    name: str: naam vd tour (en basename voor file)
    
    fields:
    start_datum: date
    eind_datum: date
    omschrijving: str
    budget: float
    nieuw_record: date  datum van volgend record.
    version: str        versie van travel die db maakt.

    return: dict: tourinfo
    '''
    while not name:
        name = input('Geef een naam voor de nieuwe tour: ')
    print(':: Maak tour {}'.format(name))
    tourData = {'naam': name}
    tourData['version'] = version
    tourData['omschrijving'] = input('Korte omschrijving: ')
    # Startdatum moet altijd een waarde hebben.
    try:
        start = validate_datum(input('Start datum YYYY-MM-DD [vandaag]*: '))
    except DatumError as e:
        print(e)
    tourData['start_datum'] = start
    # Key van de eerstvolgende nieuwe record
    tourData['nieuw_record'] = start
    print(start)
    dt = input('Eind datum. YYYY-MM-DD: ')
    # Einddatum mag leeg zijn
    if dt:
        try:
            eind  = validate_datum(dt)
        except DatumError as e:
            print(e)
        tourData['eind_datum'] = eind
        print(eind)
        print('Aantal dagen: {}'.format((eind-start).days+1))
    else:
        dagen = int(input('Hoeveel dagen duurt deze tour: '))
        tourData['eind_datum'] = start + datetime.timedelta(days=dagen - 1)
        print(tourData['eind_datum'])
    budget = input('Wat is het budget? [0.00] € ')
    if budget:
        tourData['budget'] = float(budget)
    else:
        tourData['budget'] = 0.0
    return tourData


class TravelDB():
    # Database, dict met datum als key.
    
    def __init__(self, tour, datadir):
        '''Initialisatie opent de database en leest config.

        keyword arguments:
        tour: string; naam van de tour om te openen.
        datadir: string; directory waar de tours zijn opgeslagen.

        returns None
        '''
        self.datadir = datadir
        self.tourname = tour
        try:
            with open(os.path.join(datadir, tour + '.json'), 'r', encoding='utf-8') as infile:
                self.data = json.load(infile, object_hook=json_serializer.from_json)
        except FileNotFoundError:
            # tour bestaat niet
            if not os.path.exists(datadir):
                os.mkdir(datadir)
            self.data = new_tour(tour)

    def save(self):
    '''Schrijft de database naar disk.
    
    keyword arguments:

    returns None
    '''
    if input('Wijzigingen opslaan? J/n: ').lower() in ('j',''):
        with open(os.path.join(self.datadir, self.tourname + '.json'), 'w', encoding='utf-8') as outfile:
            json.dump(self.data, outfile, default=json_serializer.to_json)
            print(': Tour: {} is opgeslagen.'.format(db['tour']['naam']))
    else:
        print(': Er is niets opgeslagen!')
    

if __name__ == '__main__':

