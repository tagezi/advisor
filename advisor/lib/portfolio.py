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

        # удаляем проданные бумаги
        oPortfolio.loc[oPortfolio['event_id'] == 5, 'tool_count'] =\
            oPortfolio.loc[oPortfolio['event_id'] == 5, 'tool_count'] * -1

        oPortfolio = oPortfolio.sort_values(['tool_type', 'tool_code'])
        # суммируем количество по коду инструмента
        oSumByTool = oPortfolio.groupby('tool_code', as_index=False).agg(
            {'tool_count': 'sum'})
        oSumByTool['tool_count'] = oSumByTool['tool_count'].astype(int)

        # находим средневзвешенную цену (PWA - Price Weighted Average)
        oSeriesPWA = weighted_average_pandas(oPortfolio)

        oPortfolio = oPortfolio.groupby('tool_code', as_index=False).agg(
            {'tool_type': 'min', 'SHORTNAME': 'min'})
        oPortfolio = oPortfolio.sort_values(by=['tool_type', 'tool_code'])
        # перемещаем столбец в начало
        type_tool = oPortfolio['tool_type']
        oPortfolio.drop(labels=['tool_type'], axis=1, inplace=True)
        oPortfolio.insert(0, 'tool_type', type_tool)

        # объединяем таблицы
        oPortfolio['tool_price'] = oSeriesPWA.values.round(2)
        oPortfolio.insert(4, 'tool_count', oSumByTool['tool_count'])

        oPortfolio.insert(5, 'sum',
                          (oPortfolio['tool_price'] *
                           oPortfolio['tool_count']).round(2))

        oPortfolio.columns = ['Тип актива', 'Код актива', 'Имя актива',
                              'Средняя цена покупки', 'Количество', 'Сумма']

        return oPortfolio


if __name__ == '__main__':
    pass
