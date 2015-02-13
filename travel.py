#!/bin/python
# travel.py
# database van tours per dag.
# database is een dict met datums als key
# en record dicts als values

version = '2.1'

import os
import json
import datetime
import argparse
import locale
locale.setlocale(locale.LC_ALL, '')

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
        return td.replace(day=datumList[1], month=datumList[0])
    elif len(datumList) == 3:
        return td.replace(day=datumList[2], month=datumList[1], year=datumList[0])
    else:
        raise DatumError('DatumError: Verkeerd datumformaat. Correcte input is: YYYY-[M]M-[D]D, [M]M-[]DD, [D]D')


def open_config(cFile):
    ''' Open configuratiebestand of maak een nieuwe.

    keyword arguments:
    cFile: string: pad en naam configuratie bestand

    returns dict
    '''
    try:
        with open(cFile) as outfile:
            return json.load(outfile)
    except FileNotFoundError:
        # geen configfile, dus first run
        if not os.path.exists(os.path.join(os.path.expanduser('~'), '.config')):
            os.mkdir(os.path.join(os.path.expanduser('~'), '.config'))
        return {'last-used' : '',
                'config_dir' : os.path.join(os.path.expanduser('~'), '.config'),
                'data_dir' : os.path.join(os.path.expanduser('~'), 'traveldata')
                }


def save_config(confData, confFile):
    ''' Save het configuratiebestand.

    keyword arguments:
    confFile: string: pad en naam van configuratie bestand.
    confData : dict: config data

    returns None
    '''
    with open(confFile, 'w') as outfile:
        json.dump(confData, outfile, indent=4)
    print(': Configuratie opgeslagen.')


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
    

def open_tour(name, traveldir):
    ''' Open de tour database.
    
    keyword arguments:
    name: string: naam vd tour
    traveldir: string: dir waar db's zijn opgeslagen.
    
    returns: dict: de tour data of None als er geen data is.
    '''
    while not name:
        input('Geef een naam voor de nieuwe tour: ')
    # creeer filenaam waar db in opgeslagen is.
    fname = os.path.join(traveldir, name + '.json')
    try:
        with open(fname) as infile:
            tourData = json.load(infile)
            # restore de date objects
            tourData['tour']['start_datum'] = datetime.date.fromordinal(int(tourData['tour']['start_datum']))
            tourData['tour']['eind_datum'] = datetime.date.fromordinal(int(tourData['tour']['eind_datum'])) 
            if tourData['tour']['nieuw_record']:
                tourData['tour']['nieuw_record'] = datetime.date.fromordinal(int(tourData['tour']['nieuw_record'])) 
    except FileNotFoundError:
        # tour bestaat niet
        jn = input('Tour < {} > Nieuw aanmaken? J/n'.format(name))
        if jn in ('j', 'J', ''):
            if not os.path.exists(traveldir):
                os.mkdir(traveldir)
            save_tour({'tour' : new_tour(name)}, conf['data_dir'])
            tourData = open_tour(name, conf['data_dir'])
        else:
            tourData = None
    return tourData
    

def save_tour(db, traveldir):
    '''Schrijft de database naar disk.
    
    keyword arguments:
    db; dict: De tour database
    traveldir: string: datadir

    returns None
    '''
    # JSON kan geen date objects serializen
    db['tour']['start_datum'] = db['tour']['start_datum'].toordinal()
    db['tour']['eind_datum'] = db['tour']['eind_datum'].toordinal()
    if db['tour']['nieuw_record']:
        db['tour']['nieuw_record'] = db['tour']['nieuw_record'].toordinal()
    with open(os.path.join(traveldir, db['tour']['naam'] + '.json'), 'w') as outfile:
        json.dump(db, outfile)
    print(': Tour: {} is opgeslagen.'.format(db['tour']['naam']))
    

def geld(waarde):
    ''' Rekent geld waarden om naar euro als waarde eindigt met 3 letter geld aanduiding

    keyword arguments:
    waarde: string: geld hoeveelheid
    conf: dict: configuratie waar omreken waardes in staan

    returns float: de waarde in euro's
    '''
    if waarde[-1].isalpha():
        return conf[waarde[-3:].upper()] * float(waarde[:-3])
    else:
        return float(waarde)


def new_record(default={}):
    ''' Maakt een nieuw record aan.
    
    keyword arguments.
    default: dict: record met default waarden

    returns: dict
    '''
    record = {}
    fields = (('naar', str), ('afstand', int), ('eten', geld), ('hotel', geld), ('anders', geld), ('opmerkingen', str))
    for label, validate in fields:
        fieldValue = input('{} [{}]: '.format(label, default.get(label)))
        if fieldValue == '' and default.get(label):
            record[label] = default[label]
        elif fieldValue:
            record[label] = validate(fieldValue)
    return record


def get_field_total(db, field):
    ''' Berekent het totaal van een numeriek veld.

    keyword arguments:
    db: dict: de open database
    field: string: veld naam

    returns float:
    '''
    if field == 'afstand':
        # integer
        total = 0
        default = 0
    else:
        # float
        total = 0.0
        default = 0.0
    for rec in db:
        total += db[rec].get(field, default)
    return total


def view_record(db, recordKey=None):
    ''' Print een record, of alle, op het scherm.

    keyword_arguments:
    db: dict: de open database.
    record_key: date: datum van te printen record. None = alle records.

    returns None
    '''
    # print header
    labels = ['Datum', 'Naar', 'Afstand', 'Eten', 'Hotel', 'Anders', 'Opmerkingen']
    print('{0[0]:-^10} {0[1]:-^28} {0[2]:-^12} {0[3]:-^11} {0[4]:-^11} {0[5]:-^11} {0[6]}'.format(labels))
    recordLine = '{:10} {:28} {:9} km {:10.2f} €{:10.2f} €{:10.2f} € {}'
    if recordKey:
        print(recordLine.format(recordKey, db[recordKey].get('naar', ''),
                                           db[recordKey].get('afstand', 0),
                                           db[recordKey].get('eten', 0),
                                           db[recordKey].get('hotel', 0),
                                           db[recordKey].get('anders', 0),
                                           db[recordKey].get('opmerkingen', '')))
    else:
        # laatse key (tour) is geen record
        for key in sorted(db.keys())[:-1]:
            print(recordLine.format(key, db[key].get('naar', ''),
                                         db[key].get('afstand', 0),
                                         db[key].get('eten', 0),
                                         db[key].get('hotel', 0),
                                         db[key].get('anders', 0),
                                         db[key].get('opmerkingen', '')))
        totalLine = '{:40}{:9} km  {:9.2f} € {:9.2f} € {:9.2f} € '
        print('{0:39} {0:-<12} {0:-<12} {0:-<11} {0:-<11}'.format(''))
        print(totalLine.format('',get_field_total(db, 'afstand'), get_field_total(db, 'eten'), get_field_total(db, 'hotel'), get_field_total(db, 'anders'), ''))
        print('{0:39} {0:-<49}'.format(''))
    

def print_stats(data):
    ''' Print statistieken over de tour.

    keyword arguments:
    data: dict: de database

    returns None
    '''
    info = data['tour']
    tourDagen = len(data) - 1
    maxDagen = (info['eind_datum'] - info['start_datum']).days + 1
    restDagen = (maxDagen - tourDagen)
    if restDagen == 0:
        restDagen = 1
    afstandTotal = get_field_total(data, 'afstand')
    kosten = [get_field_total(data, 'eten'), get_field_total(data, 'hotel'), get_field_total(data, 'anders')]
    restBudget = info['budget'] - sum(kosten)

    print('Dag {} van {} | Afgelegde afstand: {} km | daggemiddelde: {} km'.format(tourDagen, maxDagen, afstandTotal, int(afstandTotal / tourDagen)))
    print('Uitgaven')
    print('{:10}{:>12}{:>12}{:>12}{:>12}'.format('', 'Eten €', 'Hotel €', 'Anders €', 'Totaal €'))
    print('{0:>10}{1[0]:12.2f}{1[1]:12.2f}{1[2]:12.2f}{2:12.2f}'.format('totaal :', kosten, sum(kosten)))
    print('{0:>10}{1[0]:12.2f}{1[1]:12.2f}{1[2]:12.2f}{2:12.2f}'.format('per dag :', [x / tourDagen for x in kosten], sum([x / tourDagen for x in kosten])))
    print()
    print('Budget resterend: € {:.2f}, per dag: € {:.2f}'.format(restBudget, (restBudget / restDagen)))


if __name__ == '__main__':
    confFile = os.path.join(os.path.expanduser('~'), '.config', 'travel.conf')
    conf = open_config(confFile)
    dataDir = conf['data_dir'] 

    parser = argparse.ArgumentParser(description='beheer tour databases.')
    parser.add_argument('--add_currency', action='store_true', help='Voegt een nieuwe 3-letter afkorting aan conf toe.')
    parser.add_argument('-p', '--print', action='store_true', help='Print de database op het scherm')
    parser.add_argument('-e', '--edit', nargs='?', const='', help='Bewerk een record met datum EDIT.')
    parser.add_argument('tour', nargs='?', default=conf['last-used'], help='Naam van de tour die gebruikt moet worden.')
    parser.add_argument('--version', action='version', version='%(prog)s '+version)
    args = parser.parse_args()
    if args.add_currency:
        curr = input('Geef 3-letter afkorting voor de buitenlsndse munt: ')
        if curr.isalpha() and len(curr) == 3:
           conf[curr.upper()] = float(input('Wat is de omrekenfactor naar euro? '))
           save_config(conf, confFile)
        else:
            print(': error: geef precies 3 letters voor de geld afkorting.')
            
    data = open_tour(args.tour, dataDir)        
    if data:
        print('Tour: {} (v.{}) | {} - {}'.format(data['tour']['naam'], data['tour']['version'], data['tour']['start_datum'].strftime("%d %B %Y"), data['tour']['eind_datum'].strftime("%d %B %Y")))
        if conf['last-used'] != data['tour']['naam']:
            conf['last-used'] = data['tour']['naam']
            save_config(conf, confFile)
        if args.print:
            print('* {} *'.format(data['tour']['omschrijving']))
            print()
            view_record(data)
            print_stats(data)
        else:
            if args.edit == None:
                # Toevoegen
                if data['tour']['nieuw_record']:
                    print('Nieuw record voor {}'.format(data['tour']['nieuw_record'].strftime('%A %d %B %Y')))
                    if (input('Record toevoegen ? J/n ') in ('j','J','')):
                        data[data['tour']['nieuw_record'].isoformat()] = new_record()
                        # Zet key voor nieuw record, None als laatste dag in tour voorbij is.
                        if data['tour']['nieuw_record'] == data['tour']['eind_datum']:
                            data['tour']['nieuw_record'] = None
                        else:
                            data['tour']['nieuw_record'] = data['tour']['nieuw_record'] + datetime.timedelta(days=1)
                        print(': Record toegevoegd.\n')
                        print_stats(data)
                        # Save de data
                        if input('Wijzigingen opslaan? J/n: ') in ('J','j',''):
                            save_tour(data, dataDir)
                        else:
                            print(': Er is niets opgeslagen!')
                else:
                    print('Helaas is deze tour al klaar. Je kunt nog wel bewrken met --edit.')
            else:
                # Bewerken
                datum = validate_datum(args.edit)
                print('Bewerk record voor {}'.format(datum.strftime('%A %d %B %Y')))
                if data['tour']['start_datum'] <= datum <= data['tour']['eind_datum']:
                    data[datum.isoformat()] = new_record(data[datum.isoformat()])
                    print(': Record is vervangen.\n')
                    print_stats(data)
                    # Save de data
                    if input('Wijzigingen opslaan? J/n: ') in ('J','j',''):
                        save_tour(data, dataDir)
                    else:
                        print(': Er is niets opgeslagen!')
                else:
                    raise DatumError('Deze dag is niet in de database!')
    else:
        print(': Geen tour database geopend. Sluiten...')

