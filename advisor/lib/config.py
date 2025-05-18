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

""" The module provides an interface for reading and editing the configuration
file.

*Classes*:
    ConfigProgram(sFilePath='config.ini')

*Using*:

    There are two ways to use the class.

    .. code-block::

        Foo = ConfigProgram()

    or

    .. code-block::

        Foo = ConfigProgram('my_config.ini')

    Now you can read parameters from configfile and save to it.

    .. code-block::

        Parameter = Foo.get_config_value(Section, Option)
"""

import sys
from configparser import ConfigParser, NoSectionError

from advisor.lib.str import str_get_file_patch


class ConfigProgram(ConfigParser):
    """ A class for working with a configuration file. Allows you to read from
    the configuration file and write there.

    *Using*:
        ::

            Foo = ConfigProgram()

            # For reading.
            Section = 'bar'
            Options = 'baz'
            Value = Foo.get_config_value(Section, Option)

            # For writing.
            Value = 'some_string'
            Foo.set_config_value (Section, Option, Value)

        If you only need to create a Section and an Option, you omit the Value.
    """
    def __init__(self, sPathApp, sFilePath='config.ini'):
        """ Object initialization.

        :param sFilePath: Configuration file name.
        :type sFilePath: str
        """
        super().__init__()

        self.sDir = sys.path[0]

        self.sFilePath = str_get_file_patch(self.sDir, sFilePath)
        self.read(self.sFilePath)
        self.lSections = self.sections()

    def get_config_value(self, sSection, sOption):
        """ The method allows reading from a configuration file.

        :param sSection: The section in the configuration file to read from.
        :type sSection: str
        :param sOption: The option in the configuration file to need reading.
        :type sOption: str
        :return: The value of the specified parameter in the section.
        :rtype: str
        """
        return self.get(sSection, sOption)

    def set_config_value(self, sSection, sOption, sValue=''):
        """ The method allows writing into a configuration file.

        :param sSection: The section in the configuration file to write to.
        :type sSection: str
        :param sOption: The option in the configuration file to write to.
        :type sOption: str
        :param sValue: The value to write.
        :type sValue: str
        """
        try:
            self.set(sSection, sOption, sValue)
        except NoSectionError:
            self.add_section(sSection)
            self.set(sSection, sOption, sValue)

        with open(self.sFilePath, 'w') as fConfigFile:
            self.write(fConfigFile)


if __name__ == '__main__':
    pass
