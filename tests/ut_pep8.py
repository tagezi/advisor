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

import os
import pycodestyle
import unittest


class TestPEP8(unittest.TestCase):

    def test_submodules_pep8_style(self):
        """ Test that lib and unittest modules conform to PEP8. """
        oStyle = pycodestyle.StyleGuide()
        result = oStyle.check_files(['./',
                                     '../advisor/'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_main_module_pep8_style(self):
        """ Test that main module conform to PEP8. """
        for sFile in os.listdir('../../advisor/'):
            sTestFile = sFile.endswith('.py')
            if sTestFile:
                oStyle = pycodestyle.StyleGuide()
                oResult = oStyle.check_files(['../' + sFile])
                self.assertEqual(oResult.total_errors, 0,
                                 "Found code style errors (and warnings).")


if __name__ == '__main__':
    unittest.main()
