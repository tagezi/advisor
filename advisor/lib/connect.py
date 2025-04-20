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

import time
import requests

from advisor.lib.constants import API_DELAY


def connect(url, only=None, start=-1, limit=100, parameter=None, values=''):
    """ Забирает информацию в виде запроса JSON возвращает словарь

    :param only: указывает, какое/какие поля вернуть
    :param url: URL API MOEX
    :type url: str
    :param start:
    :type start: int
    :param limit:
    :type limit: int
    :param parameter:
    :type parameter: str
    :param values:
    :type values: str
    :return: словарь ответа
    :rtype: dict
    """
    time.sleep(API_DELAY)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0)'
                      ' Gecko/20100101 Firefox/116.0',
        "Content-Type": "application/json; charset=utf-8",
        'Method': 'GET'}

    param = {'iss.meta': 'off'}

    if only:
        param['iss.only'] = only
    if parameter:
        param[parameter] = values
    if start != -1:
        param['start'] = start
        param['limit'] = limit

    r = requests.get(url, headers=headers, params=param)
    r.encoding = 'utf-8'

    return r.json()


if __name__ == '__main__':
    pass
