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

import pandas as pd

from advisor.lib.math import weighted_average_pandas


class Portfolio:
    def __init__(self, oConnector):
        self.oConnector = oConnector

    def portfolio_data(self):
        # все преобразования проходят в DataFrame Pandas, если не указано иное
        oPortfolio = self.oConnector.portfolio(pd)
        oPortfolio = oPortfolio.sort_values(['title', 'tool_code'])
        # суммируем количество по коду инструмента
        oSumByTool = oPortfolio.groupby('tool_code', as_index=False).agg(
            {'buying_count': 'sum'})

        # находим средневзвешенную цену (PWA - Price Weighted Average)
        oSeriesPWA = weighted_average_pandas(oPortfolio)

        oPortfolio = oPortfolio.groupby('tool_code', as_index=False).agg(
            {'title': 'min', 'SHORTNAME': 'min'})
        oPortfolio = oPortfolio.sort_values(by=['title', 'tool_code'])
        # перемещаем столбец в начало
        type_tool = oPortfolio['title']
        oPortfolio.drop(labels=['title'], axis=1, inplace=True)
        oPortfolio.insert(0, 'title', type_tool)

        # объединяем таблицы
        oPortfolio['buying_price'] = oSeriesPWA.values.round(2)
        oPortfolio.insert(4, 'buying_count', oSumByTool['buying_count'])

        oPortfolio.insert(5, 'sum',
                          (oPortfolio['buying_price'] *
                           oPortfolio['buying_count']).round(2))

        oPortfolio.columns = ['Тип актива', 'Код актива', 'Имя актива',
                              'Средняя цена покупки', 'Количество', 'Сумма']

        return oPortfolio


if __name__ == '__main__':
    pass
