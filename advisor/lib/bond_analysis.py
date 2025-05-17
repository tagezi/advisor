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
from advisor.lib.sql import SQL
from advisor.lib.constants import FILE_DB


def get_data(oTableData, sSECID):
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


def bond_analysis(dTableData, oTableData,
                  fInflMedian5, fInflMedian10,
                  iMinPeriod=30, iMaxPeriod=181):
    """

    :param iMaxPeriod:
    :param iMinPeriod:
    :param dTableData:
    :param oTableData:
    :type oTableData: pd.DataFrame
    :param fInflMedian5: медианная инфляция за 5 лет
    :type fInflMedian5: float
    :param fInflMedian10: медианная инфляция за 10 лет
    :type fInflMedian10: float
    :return:
    :rtype: pd.DataFrame
    """
    # IAPPY - Inflation-adjusted profit as a percentage in year
    lIAPPY5Tax, lIAPPY10Tax = [], []
    for sSECID in oTableData['SECID']:
        bAmort = dTableData.get_check_amort(sSECID=sSECID)
        if bAmort:
            oTableData.drop(
                oTableData[
                    oTableData['SECID'] == sSECID].index, inplace=True
            )
            continue

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
        # считаем доход в процентах в год
        lIAPPY5Tax.append(percent_year(fIAPP5Tax, sMatDate))
        lIAPPY10Tax.append(percent_year(fIAPP10Tax, sMatDate))
    # формируем новую таблицу
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
    oTableData = oTableData[
        oTableData['% в год при сред. инфл. за 5л)'] > 0]

    return oTableData


def bond_analysis_without(oConnector,
                          iMinPeriod=30,
                          iMaxPeriod=181,
                          fPercent=1):
    # Инфляция
    oInflation = Inflation(oConnector)
    fInflMedian5 = oInflation.inflation_median_for_5()
    fInflMedian10 = oInflation.inflation_average_for_10()
    # Отбираем список облигаций
    dTableData = BondAnalysis(oConnector)
    oTableData = dTableData.get_bond_by_values(iMinPeriod=iMinPeriod,
                                               iMaxPeriod=iMaxPeriod,
                                               fPercent=fPercent)
    oTableData = bond_analysis(dTableData,
                               oTableData,
                               fInflMedian5,
                               fInflMedian10)

    return oTableData.dropna()


def bond_analysis_ofz(oConnector):
    # Инфляция
    oInflation = Inflation(oConnector)
    fInflMedian5 = oInflation.inflation_median_for_5()
    fInflMedian10 = oInflation.inflation_average_for_10()
    # Отбираем список облигаций
    dTableData = BondAnalysis(oConnector)
    oTableData = dTableData.get_bond_by_values(bOFZ=True)

    oTableData = bond_analysis(dTableData,
                               oTableData,
                               fInflMedian5,
                               fInflMedian10)

    return oTableData


class BondAnalysis:
    def __init__(self, oConnector, oPD=pd):
        self.oConnector = oConnector
        self.oPD = oPD
        self.oQuery = MOEX(self.oConnector)
        self.sTime = datetime.today().strftime('%Y-%m-%d')

    def check_is_in_db(self, sSECID, sProperty):
        """

        :param sProperty:
        :param sSECID:
        :return:
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
        oQuery = self.oConnector.get_bonds_by_value(self.oPD,
                                                    iInitialFaceValue,
                                                    sFaceUnit,
                                                    bOFZ=bOFZ,
                                                    iMinPeriod=iMinPeriod,
                                                    iMaxPeriod=iMaxPeriod,
                                                    fPercent=fPercent
                                                    )
        return oQuery

    def get_bond_info(self, sSECID):
        return self.oQuery.get_bound_info(sSECID)

    def get_check_amort(self, sSECID, bExcludeAmor=True):
        """

        :param bExcludeAmor:
        :param sSECID:
        :type sSECID: str
        :return:DataFrame
        """
        oAmort = self.check_is_in_db(sSECID, 'amort')

        if bExcludeAmor:
            if len(oAmort.index) > 1:
                return True

        return False

    def get_future(self, sSECID, sWhat='coupons'):
        """

        :param sSECID:
        :type sSECID: str
        :return:DataFrame
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
