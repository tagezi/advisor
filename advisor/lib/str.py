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

"""
The module contains a collection of functions for solving routine tasks with
strings.
"""
import locale
from os.path import join, normcase

locale.setlocale(locale.LC_ALL, '')


def str_by_locale(aNumber=1000):
    """

    :param aNumber: число, которое нужно привести к финансовому виду
    :type aNumber: any
    :return: строку с числом в финансовом виде
    :rtype: str
    """
    try:
        return locale.format_string('%.2f', aNumber, grouping=True, monetary=True)
    except TypeError:
        return aNumber


def str_get_file_patch(sDir, sFile):
    """ Concatenates file path and file name based on OS rules.

        :param sDir: String with a patch to a file.
        :param sFile: String with a filename.
        :return: Patch to file based on OS rules.
        """
    return normcase(join(sDir, sFile))


if __name__ == '__main__':
    pass
