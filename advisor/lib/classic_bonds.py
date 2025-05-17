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

""" Доходность по облигациям """


def bond_yield(dBayPrice, dCouponYield):
    bound = ClassicBonds(dBayPrice, dCouponYield)
    return (f'Цена покупки: {bound.fBayPrice}\n'
            f'Бескупонная доходность: {bound.noncupon_bond_yield()}\n'
            f'Текущая купонная доходность: '
            f'{round(bound.current_coupon_yield(), 2)}\n'
            f'Модифицированная купонная доходность: '
            f'{round(bound.modified_current_coupon_yield(182), 2)}\n'
            f'Простая доходность к погашению: '
            f'{round(bound.redemption_yield(182), 2)}\n'
            f'Эффективная доходность к погашению: '
            f'{round(bound.bonds_effective_yield(182), 2)}\n'
            f'реальная доходность к погашению: '
            f'{round(bound.real_yield(182), 2)}\n')


class ClassicBonds:
    def __init__(self, fBayPrice, fCouponYield=0, fSalePrice=1000.0,
                 fRedemptionPrice=1000.0, fBrokerageFee=0.003,
                 fBirgaFee=0.0003, fTax=0.13):
        """ Инициализация

        :param fBayPrice: Цена акции в процентах от номинала
        :param fCouponYield: цена купона в валюте
        :param fSalePrice: цена продажи акции
        :param fRedemptionPrice: Номинал акции
        :param fBrokerageFee: вознаграждение брокера за операцию
        :param fBirgaFee: вознаграждение биржи за операцию
        :param fTax: НДФЛ
        """
        self.fSalePrice = fSalePrice
        self.fCouponYield = fCouponYield
        self.fRedemptionPrice = fRedemptionPrice
        self.fBayPrice = self.bay_price(fBayPrice)
        self.fBrokerageFee = self.fBayPrice * fBrokerageFee
        self.fBirgaFee = self.fBayPrice * fBirgaFee
        self.fTax = fTax

    def bay_price(self, fBayPrice):
        """ Считает цену облигации в валюте """
        return self.fRedemptionPrice * (fBayPrice / 100)

    def noncupon_bond_yield(self):
        """ Доходность бескупонной облигации

        Д = (Н − Ц) / Ц * 100%, где:

        Д — доходность дисконтной облигации;
        Н — номинальная цена (цена погашения);
        Ц — цена покупки.
        """
        return ((self.fRedemptionPrice - self.fBayPrice)
                / self.fRedemptionPrice * 100)

    def pure_noncupon_bond_yield(self):
        """ Доходность бескупонной облигации с учетом издержек """
        dOdds = self.fRedemptionPrice - self.fBayPrice
        dTaxFee = dOdds * self.fTax
        dPureOdds = dOdds - dTaxFee - self.fBrokerageFee - self.fBirgaFee
        return dPureOdds / self.fRedemptionPrice * 100

    def current_coupon_yield(self):
        """ Текущая купонная доходность

        Д = К / Ц * 100%, где:

        К — сумма купонных выплат за период;
        Ц — текущая рыночная цена облигации.
        """
        return self.fCouponYield / self.fRedemptionPrice * 100

    def modified_current_coupon_yield(self, iDays):
        """ Модифицированная текущая купонная доходность

        Д = К / (Ц + НКД) * 100%, где:

        К — сумма купонных выплат за период;
        Ц — текущая рыночная цена облигации;
        НКД — накопленный купонный доход.
        """
        dAccumCouponIncome = self.accumulated_coupon_income(iDays)
        return self.fCouponYield / (self.fBayPrice + dAccumCouponIncome) * 100

    def accumulated_coupon_income(self, iDays):
        """ Накопленный купонный доход

         НКД = К * t / 365, где

        К — сумма купонных выплат за год;
        t — число дней от начала купонного периода."""
        return self.fCouponYield / 365 * iDays

    def redemption_yield(self, iDays):
        """ Простая доходность к погашению

        Д = ((Н − Ц) + К) / Ц * 365 / t * 100%, где:

        Н — номинальная цена облигации (или цена ее продажи);
        Ц — рыночная цена бумаги при покупке;
        К — сумма купонных платежей за весь период владения бумагой;
        t — количество дней до погашения (продажи)
        """
        dOdds = self.fRedemptionPrice - self.fBayPrice + self.fCouponYield
        return dOdds / self.fBayPrice * 365 / iDays * 100

    def bonds_effective_yield(self, iDays):
        """Эффективная доходность к погашению
        Эффективная доходность к погашению также учитывает реинвестирование
        полученных купонов. Формула будет выглядеть следующим образом:

        Д= ((Н − Ц) + К) / Ц * 365 / t * 100% + ∑ИК, где

        Н — номинальная цена облигации (или цена ее продажи);
        Ц — рыночная цена бумаги при покупке;
        К — сумма купонных платежей за весь период владения бумагой;
        t — количество дней до погашения (продажи);
        ∑ИК — доход от реинвестирования купонных выплат.
        """
        dCosts = self.fBayPrice + self.fBrokerageFee
        dTax = self.fCouponYield * self.fTax
        dOdds = (self.fRedemptionPrice - dCosts + self.fCouponYield - dTax)
        return dOdds / dCosts * 365 / iDays * 100

    def real_yield(self, iDays):
        """ Реальная доходность к погашению за вычетом налога,
        брокерской и комиссии биржи.

        Д = (Н + (К - К*ПН) - (Ц + НКД + БК + БрК) - НДФЛ) / Н * 100%
        или, что, то же самое
        Д = (Н + К - Ц - НДК - БК - БрК - НДФЛ) / Н * 100%

        :param iDays: Количество дней с последней выплаты купона
        :type iDays: int
        :return: процентную доходность
        :rtype: float
        """
        # Считаем НКД
        fCouponDebt = self.accumulated_coupon_income(iDays)
        # реальная стоимость облигации
        fCosts = (self.fBayPrice + self.fBrokerageFee +
                  self.fBirgaFee + fCouponDebt)
        # остаток купона
        fCouponYield = self.fCouponYield - fCouponDebt
        # Сумма налога
        fTax = self.fCouponYield * self.fTax
        # чистая прибыль
        iYield = self.fRedemptionPrice - fCosts + fCouponYield - fTax

        return iYield / self.fRedemptionPrice * 100


if __name__ == '__main__':
    bound = ClassicBonds(94, 78)
    print(bond_yield(94, 78))
