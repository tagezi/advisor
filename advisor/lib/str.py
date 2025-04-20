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
import re
from os.path import splitext, join, normcase, split
from time import localtime, strftime
from urllib.parse import urlparse, quote, urlunparse


def str_get_file_patch(sDir, sFile):
    """ Concatenates file path and file name based on OS rules.

        :param sDir: String with a patch to a file.
        :param sFile: String with a filename.
        :return: Patch to file based on OS rules.
        """
    return normcase(join(sDir, sFile))


def str_get_path(sFullFile):
    """ Splits a path to path and file name.

    :param sFullFile: Path with filename.
    :type sFullFile: str
    :return: The path to file.
    :rtype: str
    """
    i = split(sFullFile)[1]
    return split(sFullFile)[0]


def get_values(sString):
    """ Parses string by dividing it by signs: comma,
        semicolon, and word 'and'.

    :param sString: A String which need to divide and create list.
    :return: List of strings.
    """
    if not sString:
        return

    sString = sString.replace(" and ", ",")
    sString = sString.replace("and ", ",")
    sString = sString.replace("; ", ", ")
    sString = sString.replace(";", ",")
    sString = sString.replace(",,", ",")
    sString = sString.replace("  ", " ")
    sString = sString.replace(", ", ",")

    return sString.split(",")


def str_to_list(sString):
    """ Separates string by comma or/and semicolon.
        It can be needed than you process keywords sString bibtex or json.

        :param sString: A string that you want to separate by
            comma or/and semicolon.
        :type sString: str
        :return: A list of separated values.
        :rtype: list
        """

    if not sString:
        return None

    sString = sString.replace("; ", ", ")
    sString = sString.replace(";", ",")
    sString = sString.replace(",,", ",")
    sString = sString.replace("  ", " ")
    sString = sString.replace(", ", ",")

    return sString.split(",")


def clean_list_values(lString):
    """ Cleans all values of list form non-breaking space (\xa0) and spaces in
        the start and the end of string.

        :param lString: A list of values which you need to clean.
        :type lString: list
        :return: The list is cleaned form non-breaking space (\xa0) and spaces
            in the start and the end of string.
        :rtype: list
        """
    lReturnedList = []
    if lString == str or not lString:
        # foolproof
        lReturnedList.append(clean_string(lString))
    else:
        for sString in lString:
            lReturnedList.append(clean_string(sString))

    return lReturnedList


def lower_list_values(lString):
    """ Converts all values in the list to lowercase

        :param lString: A list of values which you need to make lower.
        :type lString: list[str, str] or str
        :return: It is list with lower case values.
            in the start and the end of string.
        :rtype: list
        """
    lReturnedList = []
    if type(lString) == str:
        # foolproof
        lReturnedList.append(clean_spaces(lString).lower())
    else:
        for sString in lString:
            lReturnedList.append(sString.lower())

    return lReturnedList


def clean_spaces(sString):
    """ Returns a string of non-breaking space (\xa0) and spaces in the start
        and the end of string.

        :param sString: Any string.
        :type sString: str
        :return: the string of non-breaking space (\xa0) and spaces in
                 the start and the end of string.
        :rtype: str
        """
    if not sString:
        return

    return sString.replace("\xa0", " ").strip()


def clean_parens(sString):
    """ Removes parentheses with their contents and removes spaces at
        the beginning and end of the string.

    :param sString: a String in which need to remove parentheses.
    :type sString: can be string or int types.
    :return: the string without brackets.
    :rtype: string.
    """
    if type(sString) == int:
        sString = str(sString)
    if not sString:
        return sString

    return re.sub(r"[\(\[].*?[\)\]]", "", sString)


def clean_string(sString):
    return clean_spaces(clean_parens(sString))


def iri_to_uri(iri):
    """ The function replaces all non-ascii characters to the corresponding
        unicode values and removes end of line.


    :param iri: A string with url.
    :return: url converted to ascii.
    ..:note::: This function does not provide converting for url
               with additional parameters.
    """
    iri = re.sub(r'\n|\s+$', '', iri)

    if len(iri) != len(iri.encode()):
        parts = urlparse(iri)
        partUri = quote(parts[2], safe='/')
        listParamUri = (
            parts[0], parts[1], partUri, parts[3], parts[4], parts[5])
        try:
            uri = urlunparse(listParamUri)
        except ValueError as e:
            print(f'An error has occurred: {e}')
            return None

        return uri

    return iri


def get_filename_time(sFileName):
    """ Adds into name of file current date and time.

        :param sFileName: a string, which contain patch to file and its name.
        :return: the patch to file and file name of the kind
                 patch/filename_YYYYMMDDhhmmss.csv.
                 OS rules are used for the path.
        """
    oTime = localtime()
    sTime = strftime("%Y%m%d%H%M%S", oTime)
    lDirAndFile = splitext(sFileName)

    return f'{lDirAndFile[0]}_{sTime}{lDirAndFile[-1]}'


def get_file_patch(sDir, sFile):
    """ Concatenates file path and file name based on OS rules.

        :param sDir: String with a patch to a file.
        :param sFile: String with a filename.
        :return: Patch to file based on OS rules.
        """
    return normcase(join(sDir, sFile))


def get_bibtext_author(sString):
    """ Returns a list of authors.

    :param sString: A string with list of authors separated 'and'
    :type sString: str
    :return: List of authors
    :rtype: list
    """
    return sString.split(' and ')


def split_by_and(sString):
    """ Separates string by '&' and 'and'.

    :param sString: A string that need to separate.
    :type sString: str
    :return: List separated by '&' and 'and'.
    ":rtype: list
    """
    if sString.find('&') != -1:
        sString = sString.replace(' & ', ' and ')

    return sString.split(' and ')


def get_wiki_url(sPartURL):
    """ Return a link to wikipedia with ending passed to the function.

        :param sPartURL: Page URL of Wikipedia started by '/'. It is usually
                an internal link in Wikipedia.
        :return: URL link to a Wikipedia page.
        """
    return f'https://en.wikipedia.org{sPartURL}'


def str_to_year(aString):
    """ Chooses a year from the string and translates it to four-digit number.

    :param aString: The string with a containing year.
    :type aString: str
    :return: Year as four-digit number.
    :type: int
    """
    if type(aString) == tuple:
        aString = list(aString)
    if type(aString) == list:
        aString = ''.join(aString)
    if aString:
        sString = clean_spaces(aString)
        iYear = [int(i) for i in re.findall(r'\d\d\d\d', sString)][0]
    else:
        iYear = aString

    return iYear


if __name__ == '__main__':
    pass
