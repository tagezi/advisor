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

""" Забираем информацию с МосБиржи """
import json
import pandas as pd
from datetime import date, datetime
from io import StringIO
from dateutil.utils import today

from advisor.lib.connect import connect
from advisor.lib.constants import FILE_DB
from advisor.lib.sql import SQL


"""
https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities.json
https://iss.moex.com/iss/securitygroups/stock_bonds/collections
https://iss.moex.com/iss/securitygroups/stock_bonds/collections/stock_bonds_corp_one/securities
https://iss.moex.com/iss/securitygroups/stock_bonds/collections/stock_bonds_one/securities?start=0&limit=100
"""
"""
url = (
                f"https://iss.moex.com/iss/engines/stock/markets/bonds/boardgroups/{t}/securities.json?iss.dp=comma&iss.meta=off&iss.only=securities,marketdata&"
                "securities.columns=SECID,SECNAME,PREVLEGALCLOSEPRICE&marketdata.columns=SECID,YIELD,DURATION"
            )

url = (
            f"https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/{board_id}/securities/{security_id}.json?"
            f"iss.meta=off&iss.only=history&history.columns=SECID,TRADEDATE,VOLUME,NUMTRADES&limit=20&from={date_request_previous}"
        )

url = f"https://iss.moex.com/iss/securities/{security_id}.json?iss.meta=off&iss.only=boards&boards.columns=secid,boardid,is_primary"

url = f"https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization/{security_id}.json?iss.meta=off&iss.only=coupons&start=0&limit=100"

url = f"https://iss.moex.com/iss/securities/{security_id}.json?iss.meta=off&iss.only=description&description.columns=name,title,value"

url = f"https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization/{ID}.json?iss.meta=off"

url = f"https://iss.moex.com/iss/securities.json?q={ticker}&iss.meta=off"
            
nkd_url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{security_code}.json?iss.meta=off&iss.only=securities&lang=ru"

price_url = f"https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQCB/securities/{security_code}.json?iss.meta=off&iss.json=extended&callback=JSON_CALLBACK&lang=ru&from={date_str}"
"""


class MOEX:
    def __init__(self, oConnect=None):
        self.oConnect = oConnect
        if not oConnect:
            self.oConnect = SQL(FILE_DB)
        self.sDomaine = 'https://iss.moex.com/'
        self.sFaild = 'iss/'

    def get_master_data(self):
        """ Возвращает ссылку на справочник Московской биржи

        :return: Ссылку на справочник
        :rtype: str
        """
        return f'{self.sDomaine}iss.json'

    def get_boards(self, sBoards):
        return

    def get_boardgroups(self, sBoardGroups):
        return

    def get_collections(self, sCollections):
        return

    def get_engines(self, sEngines):
        return

    def get_markets(self, sMarkets):
        return

    def get_securitygroups(self, sSecurityGroups):
        return

    def get_bound_info(self, sSECID):
        """

        :type sSECID: str
        :rtype: str
        """
        return (f'{self.sDomaine}{self.sFaild}securities/{sSECID}.json'
                f'?iss.meta=off'
                )

    def get_bound_dates(self, sSECID, sField='coupons', oPD=pd):
        """

        :param sField: поле, которое нужно вернуть: coupons или amortizations
        :type sField: str
        :param oPD: pandas
        :type oPD: pandas
        :param sSECID: Код ценной бумаги
        :type sSECID: str
        :return: DataFrame
        :rtype: DataFrame
        """
        # формируем URL для получения амортизации или суммы купона
        sURL = f'{self.sDomaine}{self.sFaild}statistics/engines/stock/' \
               f'markets/bonds/bondization/{sSECID}.json'

        jJSON = connect(sURL, sField, 0, 100)
        oDatesAndCouponList = oPD.read_json(StringIO(json.dumps(
            jJSON.get(sField).get('data'))), orient='columns')
        oDatesAndCouponList.columns = jJSON.get(sField).get('columns')

        # удаляем лишние столбцы
        if sField == 'coupons':
            oDatesAndCouponList.drop(['name', 'issuevalue', 'recorddate',
                                      'startdate', 'secid', 'primary_boardid',
                                      'value_rub', 'faceunit',
                                      'initialfacevalue', 'isin'],
                                     axis=1, inplace=True)
        else:
            oDatesAndCouponList.drop(['isin', 'name', 'secid',
                                      'primary_boardid', 'value_rub',
                                      'data_source', 'issuevalue',
                                      'initialfacevalue', 'faceunit'],
                                     axis=1, inplace=True)

        return oDatesAndCouponList


class MOEXUpdate:
    def __init__(self, oConnect=None):
        self.oConnect = oConnect
        if not oConnect:
            self.oConnect = SQL(FILE_DB)
        if not self.check_update():
            self.update_master_data()

    def get_markets_bonds(self):
        """ Получает таблицу инструментов торговой сессии по рынку облигаций
        """
        sURL = ('https://iss.moex.com/'
                'iss/engines/stock/markets/bonds/securities.json')
        jJSON = connect(sURL)

        # Bord Securities
        self.update_markets_bonds(jJSON=jJSON,
                                  sField='securities',
                                  sTable='BordSecurities')

        # Market Data Yields
        self.update_markets_bonds(jJSON=jJSON,
                                  sField='marketdata_yields',
                                  sTable='MarketDataYields')

    def get_markets_shares(self):
        """ Получает таблицу инструментов торговой сессии по рынку акций
        """
        sURL = ('https://iss.moex.com/'
                'iss/engines/stock/markets/shares/securities.json')
        jJSON = connect(sURL)

        # Bord Securities
        self.update_markets_bonds(jJSON=jJSON,
                                  sField='securities',
                                  sTable='SharesSecurities')

        # Market Data Yields
        self.update_markets_bonds(jJSON=jJSON,
                                  sField='marketdata_yields',
                                  sTable='MarketDataYields')

    def update_markets_bonds(self, jJSON, sField, sTable):

        sColumns = ', '.join(jJSON[sField]['columns'])
        lAllData = jJSON[sField]['data']
        for lData in lAllData:
            bIsSECID = self.oConnect.check_value(sTable=sTable,
                                                 sGet='SECID',
                                                 sWhere='SECID',
                                                 aValue=lData[0])
            if not bIsSECID:
                self.insert_rows(sTable, sColumns, lData)

            bNotUpdated = self.oConnect.check_update(sTable=sTable,
                                                     sColumns=sColumns,
                                                     sWhere='SECID',
                                                     lValues=lData)
            if not bNotUpdated:
                lData.append(lData[0])
                lData.pop(0)
                self.oConnect.update(sTable=sTable,
                                     sSetUpdate=sColumns[6:],
                                     sWhereUpdate='SECID',
                                     tValues=lData)

    def get_bond_description(self, sSECID=''):
        lSECIDList = []
        if not sSECID:
            lSECIDList = (
                self.oConnect.sql_get_values('BordSecurities',
                                             'SECID',
                                             'MATDATE>',
                                             (today().strftime("%Y-%m-%d"),))
            )

            for sSECID in lSECIDList:
                bSECID = self.oConnect.check_value('BondDescription',
                                                   'SECID',
                                                   'SECID',
                                                   sSECID[0])
                if not bSECID:
                    sURL = f'https://iss.moex.com/iss/securities/{sSECID[0]}.json'
                    jJSON = connect(sURL,
                                    only='description',
                                    parameter='description.columns',
                                    values='name,title,value')

                    oJSON = pd.DataFrame(jJSON['description']['data'],
                                         columns=jJSON['description'][
                                             'columns'])

                    lCondition = ['SECID', 'ISIN', 'INITIALFACEVALUE',
                                  'FACEUNIT', 'LISTLEVEL', 'FACEVALUE',
                                  'ISQUALIFIEDINVESTORS', 'EMITTER_ID']
                    oJSON = oJSON[oJSON['name'].isin(lCondition)]

                    sColumns = ', '.join(oJSON['name'])
                    lValues = oJSON['value'].tolist()
                    self.oConnect.insert_row('BondDescription',
                                             sColumns,
                                             lValues)

        else:
            sURL = f'https://iss.moex.com/iss/securities/{sSECID}.json'
            jJSON = connect(sURL)

    def get_collection(self, sType='', iLevel=0, sGroup='stock_bonds',
                       sCollectionName=''):
        """ Забирает данные с MOEX и сохраняет их в базе данных для дальнейшей
        обработки.

        :param sCollectionName:
        :param sType: Тип бумаги (например, ОФЗ или коммерческие)
        :type sType: str
        :param iLevel: Уровень рейтинга бумаги (0 - все уровни)
        :type iLevel: int
        :param sGroup: Группа бумаг (например, облигации, акции)
        :return:
        """
        if sCollectionName == '':
            lCollectionName = self.return_collection_name(sType, iLevel)
            sCollectionName = lCollectionName[0]
        sURL = (f'https://iss.moex.com/iss/securitygroups/{sGroup}'
                f'/collections/{sCollectionName}/securities.json')

        iStart = 0
        iTotal = 100
        sTable = ''
        if sGroup == 'stock_bonds':
            sTable = 'BondsCollections'
        elif sGroup == 'stock_shares_tplus':
            sTable = 'SharesCollections'

        while iStart < iTotal:
            print(f'обновляем: {iStart} из {iTotal}')
            jJSON = connect(sURL, iStart, 100)

            if 'securities.cursor' in jJSON:
                iTotal = jJSON['securities.cursor']['data'][0][1]
                iStart = iStart + 100
            else:
                iStart = iTotal

            sWhereColumn = 'ISIN'
            sColumns = ', '.join(jJSON['securities']['columns'])
            lAllData = jJSON['securities']['data']
            for lData in lAllData:
                if not self.oConnect.check_value(sTable,
                                                 'ISIN',
                                                 sWhereColumn,
                                                 lData[5]):
                    if 'ISIN' not in sColumns:
                        sColumns = sColumns.replace('REGNUMBER,',
                                                    'REGNUMBER, ISIN,')
                    if lData[5] is not None:
                        self.insert_rows(sTable, sColumns, lData)
                else:
                    sColumns = sColumns.replace(', ISIN', '')
                    sISIN = lData[5]
                    del lData[5]
                    lData.append(sISIN)
                    self.update_row(sTable, sColumns, sWhereColumn, lData)
        print(f'{sType} обновились.')

    def return_collection_name(self, sType, iLevel):
        """ Возвращает имя уровня облигации

        ** SecurityCollections **

        - `stock_bonds_all`	             **Все**
        - `stock_bonds_one` 	         **Все уровень 1**
        - `stock_bonds_two` 	         **Все уровень 2**
        - `stock_bonds_three` 	         **Все уровень 3**
        - `stock_bonds_corp_all` 	     **Все корпоративные**
        - `stock_bonds_corp_one` 	     **Корпоративные уровень 1**
        - `stock_bonds_corp_two` 	     **Корпоративные уровень 2**
        - `stock_bonds_corp_three` 	     **Корпоративные уровень 3**
        - `stock_bonds_exchange_all` 	 **Все биржевые**
        - `stock_exchange_corp_one` 	 **Биржевые уровень 1**
        - `stock_bonds_exchange_two` 	 **Биржевые уровень 2**
        - `stock_bonds_exchange_three` 	 **Биржевые уровень 3**
        - `stock_bonds_municipal_all`    **Все муниципальные**
        - `stock_bonds_municipal_one` 	 **Муниципальные уровень 1**
        - `stock_bonds_municipal_two` 	 **Муниципальные уровень 2**
        - `stock_bonds_municipal_three`  **Муниципальные уровень 3**
        - `stock_bonds_subfederal_all` 	 **Все субъектов РФ**
        - `stock_bonds_subfederal_one` 	 **Субъектов РФ уровень 1**
        - `stock_bonds_subfederal_two` 	 **Субъектов РФ уровень 2**
        - `stock_bonds_subfederal_three` **Субъектов РФ уровень 3**
        - `stock_bonds_ofz_all` 	     **Все ОФЗ**
        - `stock_bonds_cb_all` 	         **Все Банка России**
        - `stock_bonds_ifi_all` 	     **Все иностранных эмитентов**
        - `stock_bonds_ifi_one` 	     **Иностранных эмитентов уровень 1**
        - `stock_bonds_ifi_two` 	     **Иностранных эмитентов уровень 2**
        - `stock_bonds_ifi_three` 	     **Иностранных эмитентов уровень 3**
        - `offboard_bonds_all` 	         **Все Коммерческие**

        :param sType: Тип облигаций
        :type sType: str
        :param iLevel: Уровень рейтинга бумаги (0 - все уровни)
        :type iLevel: int
        :return: Имя коллекции
        :rtype: str
        """
        sString = sType
        if iLevel == 0:
            if sString != 'ОФЗ' and sString != 'Все':
                sString = "%s%s" % (sType[0].lower(), sType[1:])
            elif sString == 'Все':
                sString = ''
            sValue = f'Все {sString}'.rstrip()
        else:
            sString = "%s%s" % (sType[0].upper(), sType[1:])
            sValue = f'{sString} уровень {iLevel}'

        sQuery = self.oConnect.select(sTable='SecurityCollections',
                                      sGet='name',
                                      sWhere='title',
                                      tValues=(sValue,))

        return sQuery.fetchone()

    def check_update(self):
        """ Проверяет дату последнего обновления базы данных

        :return: возвращает значение обновления
        :rtype: bool
        """
        lDataUpdate = self.oConnect.sql_get_all('UpdateData')
        if lDataUpdate:
            dataUpdate = datetime.strptime(lDataUpdate[0][0],
                                           '%Y-%m-%d').date()
            if dataUpdate == date.today():
                return True

        return False

    def insert_rows(self, sTable, sColumns, lData):
        """

        :param sTable:
        :param sColumns:
        :param lData:
        :return:
        """
        self.oConnect.insert_row(sTable, sColumns, lData)

    def update_row(self, sTable, sSetUpdate, sWhereUpdate, tValues):
        self.oConnect.update(sTable, sSetUpdate, sWhereUpdate, tValues)

    def update_master_data(self):
        jJSON = connect('http://iss.moex.com/iss.json', start=-1)

        self.oConnect.sql_table_clean(['Engines', 'Markets', 'Boards',
                                       'Boardgroups', 'Durations',
                                       'SecurityTypes', 'SecurityGroups',
                                       'SecurityCollections'])

        # Engines
        sColumns = 'engine_id, engine_name, engine_title'
        for lData in jJSON['engines']['data']:
            self.insert_rows('Engines', sColumns, lData)

        # Markets
        sColumns = ('id, engine_id, market_id, market_name, market_title, '
                    'market_place, is_otc, has_history_files, '
                    'has_history_trades_files, has_trades, has_history, '
                    'has_candles, has_orderbook, has_tradingsession, '
                    'has_extra_yields, has_delay')
        for lData in jJSON['markets']['data']:
            tData = (lData[0], lData[1], lData[4], lData[5], lData[6],
                     lData[7], lData[8], lData[9], lData[10], lData[11],
                     lData[12], lData[13], lData[14], lData[15], lData[16],
                     lData[17],)
            self.insert_rows('Markets', sColumns, tData)

        # Boardgroups
        sColumns = ('id, engine_id, market_id, name, title, is_default, '
                    'board_group_id, is_traded, is_order_driven, category_id')
        for lData in jJSON['boardgroups']['data']:
            tData = (lData[0], lData[1], lData[4], lData[6], lData[7],
                     lData[8], lData[9], lData[10], lData[11], lData[12],)
            self.insert_rows('Boardgroups', sColumns, tData)

        # Boards
        sColumns = ('id, board_group_id, engine_id, market_id, board_id, '
                    'board_title, is_traded, has_candles, is_primary')
        for lData in jJSON['boards']['data']:
            self.insert_rows('Boards', sColumns, lData)

        # Durations
        sColumns = 'interval, duration, days, title, hint'
        for lData in jJSON['durations']['data']:
            self.insert_rows('Durations', sColumns, lData)

        # SecurityGroups
        sColumns = 'groups_id, name, title, is_hidden'
        for lData in jJSON['securitygroups']['data']:
            self.insert_rows('SecurityGroups', sColumns, lData)

        # SecurityTypes
        sColumns = ('id, engine_id, security_type_name, security_type_title, '
                    'security_group_name, stock_type')
        for lData in jJSON['securitytypes']['data']:
            tData = (lData[0], lData[1], lData[4], lData[5], lData[6],
                     lData[7],)
            self.oConnect.insert_row('SecurityTypes', sColumns, tData)

        # SecurityCollections
        sColumns = 'collections_id, name, title, security_group_id'
        for lData in jJSON['securitycollections']['data']:
            self.insert_rows('SecurityCollections', sColumns, lData)

        # Обновление даты обновления
        self.oConnect.update('UpdateData', 'date',
                             'id', (date.today(), 1))


if __name__ == '__main__':
    m = MOEXUpdate()
    m.get_bond_description()
