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
from datetime import datetime

from advisor.lib.finance import Inflation
from advisor.lib.math import price_normalization, face_value_inflation, \
    by_inflation, ofz_bond_profit, ofz_bond_profit_percent, percent_year
from advisor.lib.moex import MOEX


def get_data(oTableData, sSECID):
    """ Возвращает цену облигации в валюте номинала, ндк и дату погашения

    :param oTableData: Таблица облигаций в формате DataFrame Pandas
    :type oTableData: pd.DataFrame
    :param sSECID: SECID ценной бумаги на мосбирже
    :type sSECID: str
    :return: Цена облигации, НДК, дата погашения облигации
    :rtype: list[float, float, str]
    """
    # Выбираем строку и подготавливаем её
    oRowData = oTableData.loc[oTableData['SECID'] == sSECID]
    oRowData = oRowData.set_index('SECID')
    # Текущий номинал
    iFaceValue = oRowData.loc[sSECID, 'FACEVALUE']
    # Цена предыдущего дня
    fPrice = oRowData.loc[sSECID, 'PREVPRICE']
    # НКД
    fACC = oRowData.loc[sSECID, 'ACCRUEDINT']
    # Дата погашения
    sMatDate = oRowData.loc[sSECID, 'MATDATE']
    # переводим цену из процентов в валюту номинала
    fPrice = price_normalization(fPrice, iFaceValue)

    return fPrice, fACC, sMatDate


# TODO: Добавить возможность показа доходности с учетом инфляции, комиссий
def bond_analysis(dTableData, oTableData, bInfl, fInflMedian5, fInflMedian10):
    """ Удаляет бумаги с амортизацией и формирует таблицу для показа на вкладке

    :param dTableData:
    :param oTableData: Таблица облигаций в формате DataFrame Pandas
    :type oTableData: pd.DataFrame
    :param bInfl: Показывать ли доходность облигаций с учетом инфляции и др.
    :type bInfl: bool
    :param fInflMedian5: Медиана инфляции за 5 лет
    :type fInflMedian5: float
    :param fInflMedian10: Медиана инфляции за 10 лет
    :type fInflMedian10: float
    :return: Возвращает таблицу облигаций в формате DataFrame Pandas
    :rtype: pd.DataFrame
    """
    # IAPPY - Inflation-adjusted profit as a percentage in year
    lIAPPY5Tax, lIAPPY10Tax = [], []
    # Просматриваем все список и убираем из него бумаги с амортизацией
    for sSECID in oTableData['SECID']:
        bAmort = dTableData.get_check_amort(sSECID=sSECID)
        if bAmort:
            oTableData.drop(
                oTableData[
                    oTableData['SECID'] == sSECID].index, inplace=True
            )
            continue

        if bInfl:
            fIAPP5Tax, fIAPP10Tax, sMatDate = acc_inflation_bond(dTableData,
                                                                 oTableData,
                                                                 sSECID,
                                                                 fInflMedian5,
                                                                 fInflMedian10)
            # считаем доход в процентах в год
            lIAPPY5Tax.append(percent_year(fIAPP5Tax, sMatDate))
            lIAPPY10Tax.append(percent_year(fIAPP10Tax, sMatDate))

    # формируем новую таблицу с учетом показа значений с инфляцией и тд.
    if bInfl:
        oTableData.insert(7, 'Процент (инфл 5) в год, %', lIAPPY5Tax)
        oTableData.insert(8, 'Процент (инфл 10) в год, %', lIAPPY10Tax)
        oTableData = oTableData.drop(columns=['ISIN', 'FACEUNIT'])

        oTableData.columns = ['ID', 'Имя', 'Дата погашения', 'Цена, %',
                              'Доходность, %', 'Эффективная, %',
                              '% в год при сред. инфл. за 5л)',
                              '% в год при сред. инфл за 10л)',
                              'Процент купона', 'Значение купона, руб', 'НКД',
                              'Следующий купон', 'Период купона',
                              'Начальный номинал', 'Текущий номинал',
                              'Уровень листинга', 'Эмитент']
        # оставляем только те бумаги, которые с учетом инфляции на момент
        # погашения имеют положительную доходность
        oTableData = oTableData[
            oTableData['% в год при сред. инфл. за 5л)'] > 0]
    else:
        oTableData = oTableData.drop(columns=['ISIN', 'FACEUNIT'])
        oTableData.columns = ['ID', 'Имя', 'Дата погашения', 'Цена, %',
                              'Доходность, %', 'Эффективная, %',
                              'Процент купона', 'Значение купона, руб', 'НКД',
                              'Следующий купон', 'Период купона',
                              'Начальный номинал', 'Текущий номинал',
                              'Уровень листинга', 'Эмитент']

    return oTableData


def acc_inflation_bond(dTableData, oTableData, sSECID,
                       fInflMedian5, fInflMedian10):
    """ Рассчитывает доходность облигаций с учетом инфляции за 5 и 10 лет

    :param dTableData:
    :param oTableData: Таблица ценных бумаг в формате dataFrame Pandas
    :type oTableData: pd.DataFrame
    :param sSECID: SECID ценной бумаги на мосбирже
    :type sSECID: str
    :param fInflMedian5: медианная инфляция за 5 лет
    :type fInflMedian5: float
    :param fInflMedian10: медианная инфляция за 10 лет
    :type fInflMedian10: float
    :return: Доходность за 5 и 10 лет с учетом инфляции, налога и сборов
    :rtype: list[float, float, str]
    """
    fPrice, fACC, sMatDate = get_data(oTableData, sSECID)
    oUpCoupons = dTableData.get_future(sSECID=sSECID, sWhat='coupons')

    # высчитываем значения и купоны с учетом инфляции
    fFaceValue5 = face_value_inflation(fInflMedian5, oUpCoupons)
    lInflUpCoupons5 = by_inflation(fInflMedian5, oUpCoupons)
    fFaceValue10 = face_value_inflation(fInflMedian10, oUpCoupons)
    lInflUpCoupons10 = by_inflation(fInflMedian10, oUpCoupons)
    # находим сумму купонов
    fInfSumValue5 = sum(lInflUpCoupons5)
    fInfSumValue10 = sum(lInflUpCoupons10)
    # высчитываем прибыль с учетом комиссий и налога
    fProfitInfl5Tax = ofz_bond_profit(fInfSumValue5, fACC, fFaceValue5,
                                      fPrice, sDate=sMatDate,
                                      bTax=True)
    fProfitInfl10Tax = ofz_bond_profit(fInfSumValue10, fACC,
                                       fFaceValue10, fPrice,
                                       sDate=sMatDate, bTax=True)
    # Считаем доход в процентах
    fIAPP5Tax = ofz_bond_profit_percent(fProfitInfl5Tax, fPrice)
    fIAPP10Tax = ofz_bond_profit_percent(fProfitInfl10Tax, fPrice)

    return fIAPP5Tax, fIAPP10Tax, sMatDate


def bond_analysis_without(oConnector,
                          iMinPeriod=30,
                          iMaxPeriod=181,
                          fPercent=1,
                          bInfl=True):
    """

    :param oConnector: Доступ к базе данных и API класса SQL
    :type oConnector: advisor.lib.sql.SQL
    :param iMinPeriod: Минимальный период купона
    :type iMinPeriod: int
    :param iMaxPeriod: Максимальный период купона
    :type iMaxPeriod: int
    :param fPercent:
    :param bInfl: Показывать ли доходность облигаций с учетом инфляции и др.
    :type bInfl: bool
    :return: Возвращает таблицу облигаций в формате DataFrame Pandas
    :rtype: pd.DataFrame
    """
    # Инфляция за 5 и 10 лет соответственно
    fInflMedian5 = 0
    fInflMedian10 = 0
    if bInfl:
        oInflation = Inflation(oConnector)
        fInflMedian5 = oInflation.inflation_median_for_5()
        fInflMedian10 = oInflation.inflation_average_for_10()

    # Отбираем список облигаций
    dTableData = BondAnalysis(oConnector)
    oTableData = dTableData.get_bond_by_values(iMinPeriod=iMinPeriod,
                                               iMaxPeriod=iMaxPeriod,
                                               fPercent=fPercent)
    oTableData = bond_analysis(dTableData=dTableData,
                               oTableData=oTableData,
                               bInfl=bInfl,
                               fInflMedian5=fInflMedian5,
                               fInflMedian10=fInflMedian10)

    return oTableData.dropna()


def bond_analysis_ofz(oConnector, bInfl=False):
    """

    :param oConnector: Доступ к базе данных и API класса SQL
    :type oConnector: advisor.lib.sql.SQL
    :param bInfl: Показывать ли доходность облигаций с учетом инфляции и др.
    :type bInfl bool
    :return: Возвращает таблицу облигаций в формате DataFrame Pandas
    :rtype: pd.DataFrame
    """
    # Инфляция за 5 и 10 лет соответственно
    fInflMedian5 = 0
    fInflMedian10 = 0
    if bInfl:
        oInflation = Inflation(oConnector)
        fInflMedian5 = oInflation.inflation_median_for_5()
        fInflMedian10 = oInflation.inflation_average_for_10()

    # Отбираем список облигаций
    dTableData = BondAnalysis(oConnector)
    oTableData = dTableData.get_bond_by_values(bOFZ=True)

    oTableData = bond_analysis(dTableData=dTableData,
                               oTableData=oTableData,
                               bInfl=bInfl,
                               fInflMedian5=fInflMedian5,
                               fInflMedian10=fInflMedian10)

    return oTableData


class BondAnalysis:
    def __init__(self, oConnector, oPD=pd):
        """

        :param oConnector: Доступ к API базы данных класса SQL.
        :type oConnector: advisor.lib.sql.SQL
        :param oPD:
        :type oPD: pd.DataFrame
        """
        self.oConnector = oConnector
        self.oPD = oPD
        self.oQuery = MOEX(self.oConnector)
        self.sTime = datetime.today().strftime('%Y-%m-%d')

    def check_is_in_db(self, sSECID, sProperty):
        """

        :param sSECID: SECID ценной бумаги на Мосбирже
        :type sSECID: str
        :param sProperty:
        :type sProperty: str
        :return:
        :rtype: pd.DataFrame
        """
        tValues = (sSECID,)
        if sProperty == 'amort':
            sWhere = 'SECID'
            sField = 'amortizations'
            sTable = "BoundAmortizations"
            sColumns = "amort_date, face_value, valueprc, amort_value"
            sColumn = 'amort_date'
        else:
            sWhere = 'SECID'
            sField = 'coupons'
            sTable = "BoundCoupons"
            sColumns = "coupon_date, face_value, coupon_value, valueprc"
            sColumn = 'coupon_date'

        qAnswer = self.oConnector.sql_get_values(sTable, sColumns,
                                                 sWhere, tValues)
        if not qAnswer:
            oData = self.oQuery.get_bound_dates(sSECID, sField, self.oPD)
            oData.columns = sColumns.split(', ')
            lData = oData.values.tolist()
            for lValues in lData:
                self.oConnector.insert_row(sTable,
                                           f'SECID, {sColumns}',
                                           [sSECID] + lValues)
        else:
            oData = pd.DataFrame(qAnswer)
            oData.columns = sColumns.split(', ')

        if oData[sColumn].dtype != 'string':
            oData.to_string(columns=[sColumn])

        return oData

    def get_bond_by_values(self,
                           iInitialFaceValue=1000,
                           sFaceUnit='SUR',
                           bOFZ=False,
                           iMinPeriod=30,
                           iMaxPeriod=182,
                           fPercent=1):
        """ Делает запрос к API базы данных для выборки облигаций.

        Это промежуточная функция созданная для оптимизации кода. Сделать
        выборку облигаций можно напрямую, обратившись к методу
        get_bonds_by_value класс SQL.

        :param iInitialFaceValue: Начальная номинальная стоимость облигации.
        :type iInitialFaceValue: int
        :param sFaceUnit: Валюта облигации (для рублей SUR)
        :type sFaceUnit: str
        :param bOFZ: Флаг, нужно ли отбирать только ОФЗ.
        :type bOFZ: bool
        :param iMinPeriod: Минимальный период для купона в днях.
        :type iMinPeriod: int
        :param iMaxPeriod: Максимальный период для купона в днях.
        :type iMaxPeriod: int
        :param fPercent: Минимальное значение купона в процентах за год.
        :type fPercent: float
        :return: Возвращает таблицу Pandas сос писком облигаций отобранных по
        запросу.
        :rtype: pd.DataFrame
        """
        oQuery = self.oConnector.get_bonds_by_value(
            pd=self.oPD,
            iInitialFaceValue=iInitialFaceValue,
            sFaceUnit=sFaceUnit,
            bOFZ=bOFZ,
            iMinPeriod=iMinPeriod,
            iMaxPeriod=iMaxPeriod,
            fPercent=fPercent
            )

        return oQuery

    def get_bond_info(self, sSECID):
        """

        :param sSECID: SECID ценной бумаги на мосбирже.
        :type sSECID: str
        :return:
        """
        return self.oQuery.get_bound_info(sSECID)

    def get_check_amort(self, sSECID):
        """ Проверяет амортизацию облигации в базе данных.

        Если амортизация больше 1, то облигация с амортизацией. При амортизации
        равной 1 амортизация осуществляется при погашении облигации.

        :param sSECID: SECID ценной бумаги на мосбирже
        :type sSECID: str
        :return: Возвращает значение Истина или Ложь в зависимости от
        амортизации облигации
        :rtype: bool
        """
        oAmort = self.check_is_in_db(sSECID, 'amort')

        if len(oAmort.index) > 1:
            return True

        return False

    def get_future(self, sSECID, sWhat='coupons'):
        """ Возвращает информацию о будущих купонов или амортизации.

        :param sSECID: SECID ценной бумаги на Мосбирже.
        :type sSECID: str
        :param sWhat: Указывает, что искать: даты амортизации или купонов.
        :type sWhat: str
        :return: Возвращает DataFrame Pandas со столбцами **Дата купона**,
        **Номинальная стоимость**, **Величина купона в валюте**,
        **Величина купона в процентах**.
        :rtype: pd.DataFrame
        """
        if sWhat == 'coupons':
            sProperty = 'coupons'
            sField = 'coupon_date'
        else:
            sProperty = 'amort'
            sField = 'amort_date'

        oCoupons = self.check_is_in_db(sSECID, sProperty)
        oFuture = oCoupons.loc[(oCoupons[sField] > self.sTime)]

        return oFuture


if __name__ == '__main__':
    pass
