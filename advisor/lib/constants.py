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

class Constants:
    def __init__(self, oConfig):
        self.sBasePath = oConfig.sDir

        # путь до файла
        self.DB_PATH = oConfig.get_config_value('PATH', 'db_path')
        # путь до каталога с документами
        self.DOC_PATH = oConfig.get_config_value('PATH', 'doc_path')

        # каталог для базы данных работает, если не указан путь до неё
        self.DBDIR = oConfig.get_config_value('DB', 'db_dir')
        # имя базы данных работает, если не указан путь до неё
        self.DBFILE = oConfig.get_config_value('DB', 'db_file')

        # цвета для раскраски значений столбца
        sColorYield = oConfig.get_config_value('COLORS', 'coloryield')
        self.COLORYIELD = [item.strip() for item in sColorYield.split(',')]

        # цвета для визуализации периода
        sColorMatDate = oConfig.get_config_value('COLORS', 'colormatdate')
        self.COLORMATDATE = [item.strip() for item in sColorMatDate.split(',')]

        # количество дней в году
        self.DAYS = int(oConfig.get_config_value('TIME', 'days'))
        # формат даты и время
        self.DATETIME_FORMAT = \
            oConfig.get_config_value('TIME', 'datetime_format')
        # формат даты
        self.DATE_FORMAT = oConfig.get_config_value('TIME', 'date_format')

        # полное название месяцев
        sMonthNameRuFull = oConfig.get_config_value('TIME', 'month_name_full')
        self.MONTHNAMESRUFULL = \
            [item.strip() for item in sMonthNameRuFull.split(',')]

        # сокращение названий месяцев
        sMonthNameRuShort = (
            oConfig.get_config_value('TIME', 'month_name_short'))
        self.MONTHNAMESRUSHORT = \
            [item.strip() for item in sMonthNameRuShort.split(',')]

        # сбор биржи
        self.BIRGAFEE = float(oConfig.get_config_value('FEE', 'birgafee'))
        # сбор брокера
        self.BROKERFEE = float(oConfig.get_config_value('FEE', 'brokerfee'))
        # налоговый сбор
        TAX = float(oConfig.get_config_value('FEE', 'taxfee'))

        # значение свободных средств для расчета эффективной доходности
        self.TEMPPORTFILIO = (
            int(oConfig.get_config_value('SERVICE', 'tempportfolio')))
        # Переменная для задержки API запросов, лимит в 50 запросов в минуту
        self.API_DELAY = (
            float(oConfig.get_config_value('SERVICE', 'api_delay')))


if __name__ == '__main__':
    pass
