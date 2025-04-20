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

import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.utils import today

from advisor.lib.constants import DAYS, BIRGAFEE, BROKERFEE, TAX


def black_scholes(S0=100., K=105., T=1.0, r=0.05, sigma=0.2, i=100000):
    """ Формула расчета стоимости опциона """
    np.random.seed(1000)
    z = np.random.standard_normal(i)
    ST = S0 * np.exp((r - sigma ** 2 / 2) * T + sigma * math.sqrt(T) * z)
    hT = np.maximum(ST - K, 0)
    C0 = math.exp(-r * T) * np.mean(hT)
    print(f'Стоимость европейского колл-опциона: {C0}')
    return C0


def bring_number_into_range(value, min_src, max_src, min_dest=0, max_dest=40):
    """ Приводит значения к множеству заданных значений

    :param value: значение, которое нужно привести
    :type value: float
    :param min_src: начало старого множества
    :type min_src: float
    :param max_src: конец старого множества
    :type max_src: float
    :param min_dest: начало нового множества
    :type min_dest: float
    :param max_dest: конец нового множества
    :type max_dest: float
    :return: возвращает значение в рамках множества нового множества
    :rtype: int
    """
    if max_src == min_src:
        return 0
    elif value == min_src:
        return min_dest
    elif value == max_src:
        return max_dest
    else:
        new_value = (((value - min_src) /
                     (max_src - min_src)) *
                     (max_dest - min_dest) + min_dest) + 1
        return int(new_value)


def by_inflation(fInfl, oUpCoupon, sColumn='coupon_value'):
    """ Пересчитывает с учетом инфляции

    :param fInfl: Значение инфляции
    :type fInfl: float
    :param oUpCoupon: DataFrame с пересчитываемыми значениями
    :type oUpCoupon: pd.DataFrame
    :param sColumn: Столбец, в котором нужно пересчитывать
    :type sColumn: str
    :return: список пересчитанных значений
    :rtype: list
    """
    lData = []
    for iRowNum, k in oUpCoupon.iterrows():
        oDate = datetime.strptime(k['coupon_date'], '%Y-%m-%d')
        fPower = -1 * ((oDate - today()).days / DAYS)
        lData.append(discounting(k[sColumn], fInfl, fPower))

    return lData


def face_value_inflation(fInfl, oUpCoupon):
    """ Пересчитывает с учетом инфляции

    :param fInfl: Значение инфляции
    :type fInfl: float
    :param oUpCoupon: DataFrame с пересчитываемыми значениями
    :type oUpCoupon: pd.DataFrame
    :return: список пересчитанных значений
    :rtype: int
    """
    sDate = oUpCoupon['coupon_date'].iloc[-1]
    oDate = datetime.strptime(sDate, '%Y-%m-%d')
    fPower = -1 * ((oDate - today()).days / DAYS)
    iFaceValue = oUpCoupon['face_value'].iloc[-1]
    iInflFaceValue = discounting(iFaceValue, fInfl, fPower)

    return iInflFaceValue


def discounting(fSumm, fDiscountRate, fPower=-1):
    return fSumm * (1 + fDiscountRate) ** fPower


def effective_yield(fPrice, fFaceValue, oUpCoupon, iCouponFrequency):
    """ Пересчитывает купон, номинал и цену с учетом реинвестирования.

    Не соответствует расчетам ММВБ. Выведено самостоятельно. Предполагается,
    что значения уже прошли поправку на инфляцию. Коэффициентом
    реинвестирования является процентная ставка поделённая на количество
    купонов для каждого купона. Неприменимо для облигаций имеющих только одну
    выплату.

    :param fPrice: Цена облигации
    :type fPrice: float
    :param fFaceValue: Номинал облигации
    :type fFaceValue: float
    :param oUpCoupon: DataFrame будущие купоны и процентные ставки
    :type oUpCoupon: pd.DataFrame
    :param iCouponFrequency: Количество выплат в год
    :type iCouponFrequency: int
    :return:
    :rtype: list
    """

    lCouponValue = []
    iPower = 0
    for iRowNum, k in oUpCoupon.iterrows():
        iPower = iPower + 1
        fInterestRate = k['valueprc'] / iCouponFrequency / 100
        lCouponValue.append(k['infl_coupon'] * (1 + fInterestRate) ** iPower)
        fFaceValue = fFaceValue * (1 + fInterestRate) ** iPower
        fPrice = fPrice * (1 + fInterestRate) ** iPower

    return fFaceValue, lCouponValue, fPrice


def nominal_coupon_yield(iSum, iFaceValue):
    """ Номинальная купонная доходность без вычета амортизации """
    return iSum / iFaceValue * 100


""" Рассчитывается по формуле: доход инвестора 
(номинал - цена + купонный доход / цена облигации) / цена покупки * 100%
"""


def ofz_bond_profit(fSumCoupon, dACC, iFaceValue, fPrice, sDate,
                    bBirgaFee=False, bBrokerFee=False, bTax=False):
    """ Возвращает прибыль за сделку до погашения облигации без учета
    амортизации, налогов

    :param bBirgaFee:
    :param fSumCoupon: сумма всех предстоящих купонных выплат
    :type fSumCoupon: float
    :param dACC: скопленный купон
    :type dACC: float
    :param iFaceValue: тукущая цена погашения
    :type iFaceValue: int
    :param fPrice: цена покупки облигации
    :type fPrice: float
    :param sDate: Год погашения облигации
    :type sDate: str
    :param bBirgaFee: учитывать ли комиссию биржи
    :type bBirgaFee: bool
    :param bBrokerFee: учитывать ли комиссию брокера
    :type bBrokerFee: bool
    :param bTax: учитывать ли налог
    :type bTax: bool
    :return: прибыль за сделку
    :rtype: float
    """
    if bBirgaFee:
        fPrice = fPrice * (1 - BIRGAFEE)
    if bBrokerFee:
        fPrice = fPrice * (1 - BIRGAFEE)

    fProfit = iFaceValue - fPrice
    if bTax:
        fSumCoupon = fSumCoupon * (1 - TAX)
        oDate = datetime.strptime(sDate, '%Y-%m-%d')
        if ((oDate - today()).days / DAYS) < 3:
            fProfit = fProfit * (1 - TAX)

    return round(fSumCoupon - dACC + fProfit, 2)


def ofz_bond_profit_percent(fProfit, fPrice):
    return round(fProfit / fPrice * 100, 2)


def percent_year(fProfitPercent, sDate):
    """

    :param fProfitPercent:
    :param sDate:
    :return:
    """
    oDate = datetime.strptime(sDate, '%Y-%m-%d')
    fYears = (oDate - today()).days / DAYS

    return round((fProfitPercent / fYears), 2)


def price_normalization(fPrice, iFaceValue):
    """ Возвращает цену облигации

    :param fPrice: цена покупки
    :param iFaceValue: номинальная стоимость облигации
    :return:
    """
    return round(iFaceValue / 100 * fPrice, 2)


def sum_pandas(dataframe):
    return dataframe.groupby(
        'tool_code', as_index=False).agg({'buying_count': 'sum'})


def weighted_average_pandas(dataframe):
    k = ''
    oSeries = pd.Series()
    for x in dataframe['tool_code']:
        if x == k:
            continue
        k = x
        df = dataframe.loc[dataframe['tool_code'] == x]
        val = df['buying_price']
        wt = df['buying_count']
        oSeries = pd.concat([oSeries, pd.Series(
            ((val * wt).sum() / wt.sum())
        )])

    return oSeries


if __name__ == '__main__':
    df = pd.DataFrame()
    print(effective_yield(900, 1000, df, 2))
