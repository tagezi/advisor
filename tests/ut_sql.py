#     This code is a part of program Advisor
#     Copyright (C) 2022 contributors Advisor
#     The full list is available at the link
#     https://github.com/tagezi/advisor/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from unittest import TestCase

from advisor.lib.sql import *
from advisor.lib.str import str_get_file_patch


def type_connector():
    """ Creates temporal object of sqlite3.Connection and return its type.

        :return: The type sqlite3.Connection.
        """
    oConnector = sqlite3.connect(":memory:")
    return type(oConnector)


def suite():
    oSuite = unittest.TestSuite()
    oSuite.addTest(TestSQLite('test_sql_get_columns'))
    oSuite.addTest(TestSQLite('test_sql__init__'))
    oSuite.addTest(TestSQLite('test_sql_execute'))
    oSuite.addTest(TestSQLite('test_sql_insert_row'))
    oSuite.addTest(TestSQLite('test_sql_select'))
    oSuite.addTest(TestSQLite('test_sql_sql_count'))
    oSuite.addTest(TestSQLite('test_sql_delete_row'))
    oSuite.addTest(TestSQLite('test_sql_sql_get_all'))
    oSuite.addTest(TestSQLite('test_sql_sql_get_id'))
    oSuite.addTest(TestSQLite('test_sql_sql_table_clean'))
    oSuite.addTest(TestSQLite('test_sql_export_db'))
    oSuite.addTest(TestSQLite('test_sql_update'))
    oSuite.addTest(TestSQLite('test_sql_get_values'))
    oSuite.addTest(TestSQLite('test_sql_check_value'))
    oSuite.addTest(TestSQLite('test_sql_get_id'))

    return oSuite


class TestSQLite(TestCase):
    def setUp(self):
        """ Creates temporal object of sqlite3.Connection for test. """
        file_script = str_get_file_patch('../../advisor/db',
                                         'db_structure.sql')
        self.oConnector = SQL(":memory:")
        sSQL = ''
        with open(file_script, "r") as f:
            for s in f:
                sSQL = sSQL + s

        self.oConnector.execute_script(sSQL)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        del self.oConnector

    def test_sql_get_columns(self):
        """ Check if the function of separating column work. """
        sString = get_columns('check, check, check')
        sAnswer = 'check=? AND check=? AND check=?'
        self.assertEqual(sString, sAnswer)

        sString = get_columns('check')
        sAnswer = 'check=?'
        self.assertEqual(sString, sAnswer)

    def test_sql__init__(self):
        """ Check if the object being created has an instance of
            the sqlite3.Connection class.
            """
        oInstanceSQL = SQL(":memory:")
        self.assertEqual(type(oInstanceSQL.oConnector), type_connector(), )
        del oInstanceSQL

    def test_sql_execute(self):
        """ Check if execute_script and execute_query work. """
        oCursor = self.oConnector.execute_query('SELECT account_type '
                                                'FROM AccountTypes '
                                                'WHERE account_type=?',
                                                ('брокерский счет',))
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 'брокерский счет')

    def test_sql_insert_row(self):
        """ Check if insert_row work correctly. """
        bIns = self.oConnector.insert_row('AccountTypes',
                                          'account_type',
                                          ('check',))
        self.assertTrue(bIns)

        oCursor = self.oConnector.execute_query('SELECT account_type '
                                                'FROM AccountTypes '
                                                'WHERE account_type="check"'
                                                )
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 'check')

        bIns = self.oConnector.insert_row('AccountTypes',
                                          'account_type',
                                          ('check_too', 1, 2,))
        self.assertFalse(bIns)

    def test_sql_select(self):
        """ Check if select work correctly. """
        self.oConnector.insert_row('AccountTypes',
                                   'account_type',
                                   ('check',))
        oCursor = self.oConnector.select('AccountTypes', 'account_type',
                                         'account_type', ('check',))
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 'check')

        oCursor = self.oConnector.select('Portfolio',
                                         'tool_code, date, price')
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 'SU26219RMFS4')
        self.assertEqual(lRows[0][1], '2025-03-20')
        self.assertEqual(lRows[0][2], 902.42)

        oCursor = self.oConnector.select('Portfolio', '*', sFunc='Count')
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 36)

        self.oConnector.insert_row('Portfolio', 'tool_code', ('check',))
        oCursor = self.oConnector.select('Portfolio',
                                         'tool_code', sFunc='DISTINCT')
        lRows = oCursor.fetchall()
        self.assertEqual(lRows[0][0], 'SU26219RMFS4')
        self.assertEqual(lRows[1][0], 'LKOH')
        self.assertEqual(lRows[2][0], 'X5')

    def test_sql_delete_row(self):
        """ Check if delete_row work correctly. """
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        iDel = self.oConnector.delete_row('AccountTypes',
                                          'account_type',
                                          ('check',))
        self.assertTrue(iDel)
        oCursor = self.oConnector.select('AccountTypes', 'account_type',
                                         'account_type', ('check',))
        lRows = oCursor.fetchall()
        self.assertFalse(lRows)
        oCursor = self.oConnector.select('AccountTypes', 'account_type',
                                         'account_type', ('брокерский счет',))
        lRows = oCursor.fetchall()
        self.assertTrue(lRows)

    def test_sql_export_db(self):
        """ Check if export_db work correctly. """
        pass

    def test_sql_sql_count(self):
        """ Check if sql_count work correctly. """
        oCursor = self.oConnector.select('AccountTypes', '*', sFunc='Count')
        lRowsLow = oCursor.fetchall()
        lRowsAverage = self.oConnector.sql_count('AccountTypes')
        self.assertEqual(lRowsLow[0][0], lRowsAverage)

    def test_sql_sql_get_all(self):
        """ Check if sql_get_all work correctly. """
        oCursor = self.oConnector.select('AccountTypes', '*')
        lRowsLow = oCursor.fetchall()
        lRowsAverage = self.oConnector.sql_get_all('AccountTypes')
        self.assertEqual(lRowsLow[0][0], lRowsAverage[0][0])
        self.assertEqual(lRowsLow[1][0], lRowsAverage[1][0])

        lRows = self.oConnector.sql_get_all('Mistake')
        self.assertFalse(lRows)

    def test_sql_sql_get_id(self):
        """ Check if sql_get_id work correctly. """
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        oCursor = self.oConnector.select('AccountTypes', 'account_type_id',
                                         'account_type', ('check',))
        lRowsLow = oCursor.fetchall()
        lRowsAverage = self.oConnector.sql_get_id('AccountTypes',
                                                  'account_type_id',
                                                  'account_type',
                                                  ('check',))
        self.assertEqual(lRowsLow[0][0], lRowsAverage)

        lRow = self.oConnector.sql_get_id('Mistake', 'account_type_id',
                                          'account_type', ('check',))
        self.assertEqual(lRow, 0)

    def test_sql_sql_table_clean(self):
        """ Check if delete_row work correctly. """
        self.oConnector.insert_row('SECID', 'SECID', ('check',))
        iDel = self.oConnector.delete_row('SECID')
        self.assertTrue(iDel)
        lRows = self.oConnector.sql_count('SECID')
        self.assertEqual(lRows, 0)

        iDel = self.oConnector.delete_row('Mistake')
        self.assertFalse(iDel)

    def test_sql_update(self):
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        iUpd = self.oConnector.update('AccountTypes',
                                      'account_type',
                                      'account_type_id',
                                      ('check_too', 5))
        self.assertTrue(iUpd)

        oCursor = self.oConnector.select('AccountTypes', 'account_type_id',
                                         'account_type', ('check_too',))
        lRowsLow = oCursor.fetchall()
        self.assertEqual(lRowsLow[0][0], 5)

    def test_sql_get_values(self):
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        sValue = self.oConnector.sql_get_values('AccountTypes',
                                                'account_type_id',
                                                'account_type',
                                                ('check',))
        self.assertEqual(sValue[0][0], 5)

        sValue = self.oConnector.sql_get_values('AccountEvents',
                                                'acc_events_id',
                                                'tool_code, tool_price',
                                                ('SBER', 325.78,),
                                                'AND')
        self.assertEqual(sValue[0][0], 5)

    def test_sql_check_value(self):
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        bAnswer = self.oConnector.check_value('AccountTypes',
                                              'account_type',
                                              'account_type',
                                              'check')
        self.assertTrue(bAnswer)

        bAnswer = self.oConnector.check_value('AccountTypes',
                                              'account_type',
                                              'account_type',
                                              'check1')
        self.assertFalse(bAnswer)

    def test_sql_get_id(self):
        self.oConnector.insert_row('AccountTypes', 'account_type', ('check',))
        iValue = self.oConnector.sql_get_id('AccountTypes',
                                            'account_type_id',
                                            'account_type',
                                            ('check',))
        self.assertEqual(iValue, 5)

        bAnswer = self.oConnector.sql_get_id('AccountTypes',
                                             'account_type_id',
                                             'account_type',
                                             ('check1',))
        self.assertFalse(bAnswer)

        iValue = self.oConnector.sql_get_id('AccountEvents',
                                            'acc_events_id',
                                            'tool_code, tool_price',
                                            ('SBER', 325.78,),
                                            'AND')
        self.assertEqual(iValue, 5)

    def test_check_update(self):
        oAnswer = self.oConnector.select('BondsSecurities', '*',
                                         'SECID', ('SU26207RMFS9',))
        oValue = oAnswer.fetchone()
        sNames = ', '.join(list(map(lambda x: x[0], oAnswer.description)))
        self.oConnector.check_update('BondsSecurities',
                                     sNames,
                                     'SECID',
                                     oValue[1])


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
