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


def years(sDate):
    oDate = datetime.strptime(sDate, '%Y-%m-%d')
    fYears = (oDate - today()).days / DAYS
    return fYears


def weighted_average_pandas(dataframe):
    k = ''
    oSeries = pd.Series()
    for x in dataframe['tool_code']:
        if x == k:
            continue
        k = x
        df = dataframe.loc[dataframe['tool_code'] == x]
        val = df['tool_price']
        wt = df['tool_count']
        if not oSeries.empty:
            if wt.sum() != 0:
                oSeries = pd.concat([oSeries, pd.Series(
                    ((val * wt).sum() / wt.sum())
                )], ignore_index=True)
            else:
                oSeries = pd.concat([oSeries, pd.Series(
                   np.nan
                )], ignore_index=True)
        else:
            if wt.sum() != 0:
                oSeries = pd.Series(((val * wt).sum() / wt.sum()))
            else:
                oSeries = np.nan

    return oSeries

""" 
    Функция для расчета бескупонной доходности по методу Нельсона-Сигеля 
"""
# Непрерывная доходность
def GT(t, beta0, beta1, beta2, tau, g_values):
    # Основные члены модели
    term1 = beta0 + beta1 * tau * (1 - np.exp(-t / tau)) / t
    term2 = beta2 * ((1 - np.exp(-t / tau)) * tau / t - np.exp(-t / tau))

    # Инициализация параметров a_i и b_i
    a_values = np.zeros(9)
    b_values = np.zeros(9)

    # Инициализация первых значений
    a_values[0] = 0  # a_1 = 0
    a_values[1] = 0.6  # a_2 = 0.6
    b_values[0] = a_values[1]  # b_1 = a_2

    k = 1.6  # параметр для рекуррентного расчета

    # Рекуррентное вычисление a_i и b_i
    for i in range(2, 9):
        a_values[i] = a_values[i - 1] + k ** (i - 1)
        b_values[i - 1] = b_values[i - 2] * k

    # Расчет суммы по экспоненциальным членам
    term3 = 0
    for i in range(9):
        if b_values[i] != 0:  # Добавляем проверку на нулевые значения b_i
            term3 += g_values[i] * np.exp(
                -((t - a_values[i]) ** 2) / (b_values[i] ** 2))

    GT = term1 + term2 + term3

    return GT / 10000

# Кривая бескупонной доходности в % годовых
def get_KBD_in_year_precent(t, beta0, beta1, beta2, tau, g_values):
    YT = 100 * (np.exp(GT(t, beta0, beta1, beta2, tau, g_values)) - 1)
    return YT

"""
    Построение графиков спотовой и форвардной кривой
"""

# Функция для расчета цены бескупонной облигации P(0,T) на основе данных Мосбиржи
def P_0_T(beta0, beta1, beta2, tau, g_values, T):
    R_T = GT(T, beta0, beta1, beta2, tau, g_values)  # Бескупонная непрерывно начисляемая ставка
    return np.exp(-R_T * T)

# Форвардная ставка F(0,T)
def F_0_T(T, beta0, beta1, beta2, tau, g_values, dt=1e-4):
    P_T_plus_dt = P_0_T(beta0, beta1, beta2, tau, g_values, T + dt)
    P_T = P_0_T(beta0, beta1, beta2, tau, g_values, T)
    F_0_T = -(np.log(P_T_plus_dt) - np.log(P_T)) / dt
    return F_0_T

# форвардная ставка при годовом (эффективном) начислении, в % годовых
def F_0_T_eff(T, beta0, beta1, beta2, tau, g_values, dt=1e-4):
    FT = 100*(np.exp(F_0_T(T, beta0, beta1, beta2, tau, g_values, dt=1e-4)) - 1)
    return FT


if __name__ == '__main__':
    pass
