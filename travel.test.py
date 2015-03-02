#!/bin/python
# travel.test.py
# Testcases tbv travel.py

import unittest
import travel

class TestTravel(unittest.TestCase):
    # fietsdagen: 3
    # rustdagen: 1
    # afstand: 250
    # eten: 30
    # hotel: 25
    # anders: 31.55
    data = {'2015-01-01': {'naar': 'amsterdam', 'afstand': 100, 'eten': 10},
          '2015-01-02': {'afstand': 50, 'hotel': 25, 'anders': 10, 'opmerkingen': 'xxx'},
          '2015-01-03': {'naar': 'Bangkok', 'eten': 10, 'anders': 1.55},
          '2015-01-04': {'naar': 'huis', 'afstand': 100, 'eten': 10, 'anders': 20}
          }

    def test_fiets_dagen(self):
        dagen = 3
        result = travel.fiets_dagen(self.data)
        self.assertEqual(dagen, result)

    def test_nul_fietsdagen(self):
        db = self.data
        del(db['2015-01-01']['afstand'])
        del(db['2015-01-02']['afstand'])
        del(db['2015-01-04']['afstand'])
        result = travel.fiets_dagen(db)
        self.assertEqual(0, result)

    def test_get_field_total(self):
        afstand = 250
        result = travel.get_field_total(self.data, 'afstand')
        self.assertEqual(afstand, result)

    def test_get_field_total_nul(self):
        result = travel.get_field_total(self.data, 'not_existing_field')
        self.assertEqual(0, result)

    def test_get_field_total_float(self):
        result = travel.get_field_total(self.data, 'anders')
        self.assertAlmostEqual(31.55, result)


if __name__ == '__main__':
    unittest.main()

