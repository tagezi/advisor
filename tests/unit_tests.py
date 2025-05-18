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

""" The main module for UnitTest. Runs all tests for the program. """
import unittest

from ut_pep8 import TestPEP8
from ut_sql import TestSQLite
from ut_str import TestStr


def suite():
    """ Collects all tests from other modules for them running here.

    :return: Object of TestSuit class
    """
    oSuite = unittest.TestSuite()
    oSuite.addTest(TestPEP8('test_submodules_pep8_style'))
    oSuite.addTest(TestPEP8('test_main_module_pep8_style'))
    oSuite.addTest(TestStr('test_str_str_by_locale'))
    oSuite.addTest(TestStr('test_str_str_get_file_patch'))
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

    return oSuite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
