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

""" Сложные проценты """
"""
https://iss.moex.com//iss/engines/stock/markets/bonds/index.json
https://iss.moex.com//iss/engines/stock/markets/bonds/securities.json
https://iss.moex.com//iss/engines/stock/markets/bonds/securities/SU25084RMFS3.json

/iss/statistics/engines/stock/currentprices
/iss/statistics/engines/stock/markets/bonds/monthendaccints
/iss/statistics/engines/stock/markets/index/analytics/columns
# blockname = 'securities'
# data = [{str.lower(k): r[i] for i, k in enumerate(j[blockname]['columns'])} for
#         r in j[blockname]['data']]
#
# df = pd.json_normalize(data)
# pd.set_option('display.max_column', 13)
# df['name'] = df['name'].str.lower()
# df.to_csv('out2.csv')
"""


class CCI:
    def __init__(self, cash, interest_rate, frequency, period):
        if frequency == 'month':
            self.frequency = 12
        if frequency == 'year':
            self.frequency = 1
        if frequency == 'day':
            self.frequency = 360

        self.cash = cash
        self.interest_rate = interest_rate
        self.period = period

    def compound_interest(self):
        return (self.cash *
                (1 + self.interest_rate / (self.frequency * 100)) ** (
                        self.frequency * self.period))

    def rir(self):
        return round(((self.compound_interest() / self.cash - 1) * 100), 2)


if __name__ == '__main__':
    pass
