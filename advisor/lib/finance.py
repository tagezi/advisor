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

from datetime import datetime
import pandas as pd

from advisor.lib.constants import FILE_DB
from advisor.lib.sql import SQL


class Inflation:
    def __init__(self, oConnector):
        self.oInflation = None
        self.oConnector = oConnector
        self.get_inflation_list()

    def get_inflation_list(self):
        """
        Возвращает инфляцию за все годы наблюдения в виде DataFrame
        """
        qAnswer = self.oConnector.sql_get_all('Inflation', 'year, inflation')
        self.oInflation = pd.DataFrame(qAnswer)
        self.oInflation.columns = ['year', 'inflation']

        return self.oInflation

    def set_inflation_value(self):
        """ Вносит новое значение наблюдения (пока ничего не делает)

        :return:
        """
        pass

    def inflation_for_5(self):
        """ Средне арифметическая инфляция за 5 лет

        :rtype: float
        """
        oInflationFor5 = self.inflation_for_per(5)

        return round(oInflationFor5['inflation'].mean(), 4)

    def inflation_for_10(self):
        """ Средне арифметическая инфляция за 10 лет

        :rtype: float
        """
        oInflationFor10 = self.inflation_for_per(10)

        return round(oInflationFor10['inflation'].mean(), 4)

    def inflation_median_for_5(self):
        """ Медианная инфляция за 5 лет

        :rtype: float
        """
        oInflationFor5 = self.inflation_for_per(5)
        return round(oInflationFor5['inflation'].median(), 4)

    def inflation_median_for_10(self):
        """ Медианная инфляция за 10 лет

        :rtype: float
        """
        oInflationFor10 = self.inflation_for_per(10)

        return round(oInflationFor10['inflation'].median(), 4)

    def inflation_for_per(self, iYears):
        """ Возвращает срез DataFrame с данными последние нескольких лет
        (iYears), если были наблюдения, иначе возвращает весь массив

        :param iYears: Количество лет
        :type iYears: int
        :return: срез DataFrame
        """
        iYear = int(datetime.today().strftime('%Y'))
        oInflation = self.oInflation

        if self.oInflation['year'].min() <= (iYear - iYears):
            oInflation = self.oInflation.loc[(self.oInflation['year']
                                              > (iYear - iYears))]
        return oInflation


if __name__ == '__main__':
    pass
    # oConn = SQL(FILE_DB)
    # inf = Inflation(oConn)
    # print(inf.get_inflation_list())
    # print(inf.inflation_for_5())
    # print(inf.inflation_for_10())
    # print(inf.inflation_median_for_5())
    # print(inf.inflation_median_for_10())
    # print(inf.inflation_for_per(12))
