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

DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

# цвета для раскраски значений столбца
COLORYIELD = ['#ff0d05', '#ff0000', '#ff190a', '#ff260f', '#ff3314', '#ff401a',
              '#ff4d1f', '#ff5924', '#ff6629', '#ff732e', '#ff8033', '#ff8c38',
              '#ff993d', '#ffa642', '#ffb247', '#ffbf4c', '#ffcc52', '#ffd957',
              '#ffe65c', '#fff261', '#ffff66', '#f2fa61', '#e6f55c', '#d9f057',
              '#cceb52', '#bfe64c', '#b2e047', '#a6db42', '#99d63d', '#8cd138',
              '#80cc33', '#73c72e', '#66c229', '#59bd24', '#4cb81f', '#40b21a',
              '#33ad14', '#26a80f', '#1aa30a', '#0d9e05', '#009900']

# цвета для визуализации периода
COLODMATDATE = ["#FA8072", "#FFE4B5", "#b2e047", "#808080"]

DAYS = 364
BIRGAFEE = 0.00003
BROKERFEE = 0.0003
TAX = 0.13
# значение свободных средств для расчета эффективной доходности
TEMPPORTFILIO = 12000000

MONTH_NAMES_RU_FULL = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]
MONTH_NAMES_RU_SHORT = [
    "янв",
    "фев",
    "мар",
    "апр",
    "май",
    "июн",
    "июл",
    "авг",
    "сен",
    "окт",
    "ноя",
    "дек",
]

FILE_DB = ''
# Переменная для задержки API запросов, лимит в 50 запросов в минуту
API_DELAY = 1.2


if __name__ == '__main__':
    pass
