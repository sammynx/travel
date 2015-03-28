#!/bin/python
# json_serializer.py: serializes objects which can not be serialized by json.

import datetime

def to_json(python_object):
    ''' Change objects not serializable by json to serializable.

    keyword arguments:
    python_object: object

    returns object
    '''
    if isinstance(python_object, datetime.date):
        return {'__class__': 'datetime.date',
                '__value__': datetime.date.toordinal(python_object)}
    raise TypeError(repr(python_object) + 'is not JSON serializable!')


def from_json(json_object):
    ''' Convert json objects made by to_json back to python objects

    keyword arguments:
    json_object: dict: made by to_json

    returns json object
    '''
    if '__class__' in json_object:
        if json_object['__class__'] == 'datetime.date':
            return datetime.date.fromordinal(int(json_object['__value__']))
    return json_object


if __name__ == '__main__':
    import json

    d = datetime.date.today()
    print('Today: {}'.format(d))
    jsonObject = json.dumps(d, default=to_json)
    d2 = json.loads(jsonObject, object_hook=from_json)
    print('Today (after json serializing): {}'.format(d2))

