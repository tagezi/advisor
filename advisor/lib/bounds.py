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

from datetime import date
from advisor.lib.constants import DAYS


def number_payments_in_year(iNPayments):
    """ Количество выплат в год """
    return round(DAYS / iNPayments)


class Bounds:
    """ Класс для структуризации и обработки основных данных об облигации

    Атрибуты класса:

    - :class:`float` **fBayPrice**: Цена акции в процентах от номинала
    - :class:`float` **fRedemptionPrice**: Номинал акции
    - :class:`float` **fCoupon**: цена купона в валюте
    - :class:`float` **fACI**: накопленный купонный доход
    - :class:`int` **iCouponDuration**: количество дней до выплаты купона
    - :class:`int` **iNumberPayments**: количество выплат в год
    - :class:`str` **sForeignCurrency**: валюта облигации
    - :class:`datetime` **sCouponDate**: дата выплаты купона
    - :class:`datetime` **sRedemptionDate**: дата погашения облигации
    - :class:`datetime` **sOfferDate**: дата оферты
    - :class:`float` **fBrokerageFee**: вознаграждение брокера в рублях
    - :class:`float` **fBirgaFee**: вознаграждение биржи за операцию  в рублях
    - :class:`float` **fTaxBody**: НДФЛ за разницу в покупке в рублях
    - :class:`float` **fTaxBody**: НДФЛ за купон в рублях
    """
    def __init__(self, fBayPrice, fRedemptionPrice=1000.0, fCoupon=0.0,
                 fACI=0.0, iCouponDuration=182, sForeignCurrency='',
                 sCouponDate='', sRedemptionDate='', sOfferDate='',
                 fBrokerageFee=0.003, fBirgaFee=0.0003, fTax=0.13,
                 fFounds=30000):
        """ Инициализация

        :param fBayPrice: Цена акции в процентах от номинала
        :type fBayPrice: float
        :param fRedemptionPrice: Номинал акции
        :param fCoupon: цена купона в валюте
        :param fACI: накопленный купонный доход
        :param iCouponDuration: количество дней до выплаты купона
        :param sForeignCurrency: валюта облигации
        :param sCouponDate: дата выплаты купона
        :param sRedemptionDate: дата погашения облигации
        :param sOfferDate: дата оферты
        :param fBrokerageFee: вознаграждение брокера за операцию в процентах
        :param fBirgaFee: вознаграждение биржи за операцию в процентах
        :param fTax: НДФЛ в процентах
        """
        self.fRedemptionPrice = fRedemptionPrice
        self.fBayPrice = self.bay_price(fBayPrice)
        self.fCoupon = fCoupon
        self.fACI = fACI
        self.sForeignCurrency = sForeignCurrency
        self.iCouponDuration = iCouponDuration
        self.iNPayments = number_payments_in_year(iCouponDuration)
        self.CouponDate = date.fromisoformat(sCouponDate)
        self.RedemptionDate = date.fromisoformat(sRedemptionDate)
        self.OfferDate = date.fromisoformat(sOfferDate)
        self.fBrokerageFee = self.brokerage_fee(fBrokerageFee)
        self.fBirgaFee = self.birga_fee(fBirgaFee)
        self.fTaxBody = self.tax_body(fTax)
        self.fTaxCoupon = self.tax_coupon(fTax)
        self.fFounds = fFounds
        self.iQuantityOfBonds = self.quantity_of_bonds()
        self.fPurchaseAmount = self.fBayPrice * self.iQuantityOfBonds

    def bay_price(self, fBayPrice):
        """ Считает цену облигации в валюте """
        return self.fRedemptionPrice * fBayPrice / 100

    def brokerage_fee(self, fBrokerageFee):
        """ Вознаграждение брокера за операцию """
        return self.fBayPrice * fBrokerageFee

    def birga_fee(self, fBirgaFee):
        """ Вознаграждение биржи за операцию """
        return self.fBayPrice * fBirgaFee

    def tax_body(self, fTax):
        """ Налог с разницы куплипродажи, если цена ниже погашения """
        if self.fBayPrice < self.fRedemptionPrice:
            return (self.fRedemptionPrice - self.fBayPrice) * fTax

        return 0

    def tax_coupon(self, fTax):
        """ Налог с купона, вычитается со всего тела купона без учета НКД """
        return self.fCoupon * fTax

    def coupon_without_aci(self):
        """
        ( ДнДоПог / 365 * КолВып * К ) + К - НДК
        :return:
        """
        NDay = self.RedemptionDate - date.today()
        iNYears = NDay.days // DAYS
        fFullCoupon = self.iNPayments * self.fCoupon
        return iNYears * fFullCoupon + self.fCoupon - self.fACI

    def coupon_without_fee(self):
        """ Купонный доход за вычетом налога и сборов брокера и биржи"""
        return self.coupon_without_aci() - self.fTaxCoupon

    def quantity_of_bonds(self):
        """ Количество покупаемых облигаций """
        return self.fFounds // (self.fBayPrice + self.fACI + self.fBrokerageFee)

    def income(self):
        """ Доход с купленных облигаций """
        k = (self.fRedemptionPrice - self.fBayPrice - self.fTaxBody
                + self.coupon_without_fee()) * self.quantity_of_bonds()
        return k

    def profitability(self):
        """ Доходность облигаций за период владения """
        return self.income() / self.fPurchaseAmount


if __name__ == '__main__':
    bonds = Bounds(fBayPrice=90.21, fRedemptionPrice=1000.0, fCoupon=38.64, fACI=0.2,
                   iCouponDuration=182, sForeignCurrency='SUB',
                   sCouponDate='2023-10-18', sRedemptionDate='2026-09-16',
                   sOfferDate='2023-10-18', fBrokerageFee=0.00003,
                   fBirgaFee=0.000003, fTax=0.13, fFounds=30000)
    print(f'Цена облигации в процентах от номинала: {bonds.fBayPrice} руб.\n'
          f'Номинал облигации: {bonds.fRedemptionPrice} руб.\n'
          f'Цена купона в валюте: {bonds.fCoupon} руб.\n'
          f'Накопленный купонный доход: {bonds.fACI} руб.\n'
          f'Количество дней до выплаты купона: {bonds.iCouponDuration} дней\n'
          f'Валюта облигации: {bonds.sForeignCurrency}\n'
          f'Дата выплаты купона: {bonds.CouponDate}\n'
          f'Дата погашения облигации: {bonds.RedemptionDate}\n'
          f'Дата оферты: {bonds.OfferDate}\n'
          f'Вознаграждение брокера: {bonds.fBrokerageFee} руб.\n'
          f'Вознаграждение биржи: {bonds.fBirgaFee} руб.\n'
          f'НДФЛ за покупку: {bonds.fTaxBody} руб.\n'
          f'НДФЛ за купонный доход: {bonds.fTaxCoupon} руб.\n'
          f'Выплаты купона без НКД и сборов: {bonds.coupon_without_aci()}\n'
          f'Сумма инвестиции: {bonds.fPurchaseAmount}\n'
          f'Количество облигаций: {bonds.iQuantityOfBonds}\n'
          f'Прибыль: {bonds.income()}\n'
          f'доходность: {round(bonds.profitability()*100, 2)}\n')
