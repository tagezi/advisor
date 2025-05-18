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

from advisor.lib.str import *


def suite():
    oSuite = unittest.TestSuite()
    oSuite.addTest(TestStr('test_str_str_by_locale'))
    oSuite.addTest(TestStr('test_str_str_get_file_patch'))

    return oSuite


class TestStr(unittest.TestCase):
    def test_str_str_by_locale(self):
        """ Check if str_by_locale work correctly. """
        sTestValue = 1000
        sLocaleValue = str_by_locale(sTestValue)
        self.assertEqual(sLocaleValue, '1\u202f000,00')

        sTestValue = 0.0506
        sLocaleValue = str_by_locale(sTestValue)
        self.assertEqual(sLocaleValue, '0,05')

    def test_str_str_get_file_patch(self):
        sTestDir = '/dir/advisor'
        sTestFile = 'config.ini'
        sTaxon = str_get_file_patch(sTestDir, sTestFile)
        self.assertEqual(sTaxon, '/dir/advisor/config.ini')


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
