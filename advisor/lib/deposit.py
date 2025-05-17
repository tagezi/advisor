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

class Deposit:
    def __init__(self,
                 fAmount=10000,
                 fInterestRate=0.06,
                 iTimeYears=0,
                 iTimeMonth=0,
                 iPaymentNumber=1):
        """

        :param fAmount: Сумма депозита
        :type fAmount: float
        :param fInterestRate: Процент по депозиту
        :type fInterestRate: float
        :param iTimeYears: Количество лет вклада
        :type iTimeYears: int
        :param iTimeMonth: Количество месяцев вклада
        :type iTimeMonth: int
        :param iPaymentNumber: Количество капитализаций
        :type iTimeMonth: int
        """
        self.fAmount = fAmount
        self.fInterestRate = fInterestRate
        self.iTimeYears = iTimeYears
        self.iTimeMonth = iTimeMonth
        self.iPaymentNumber = iPaymentNumber

    def set_amount(self, fAmount):
        self.fAmount = fAmount

    def set_interest_rate(self, fInterestRate):
        self.fInterestRate = fInterestRate

    def set_payment_number(self, iPaymentNumber):
        self.iPaymentNumber = iPaymentNumber

    def interest(self):
        """ Итоговая сумма инвестиций при простом проценте

        B(T+k/p) = B0*(1+k/p*T*i/p)

        - B0 - начальная сумма на депозите
        - B(T+k/p) - сумма через Т периодов и дробную часть периода
        - T - количество лет (периодов)
        - k - дробная честь года (периода)
        - p - количество выплат в году (за период)
        - i - процент по депозиту на год (период)

        :return: Сумму на счете в конце периода
        """
        # Количество выплат за все время
        iPayNumAll = self.iPaymentNumber * self.iTimeYears
        # Процент на одну выплату
        fInterestRateForOnePer = self.fInterestRate / self.iPaymentNumber
        return self.fAmount * (1 + iPayNumAll * fInterestRateForOnePer)

    def compound_interest(self):
        """ Итоговая сумма инвестиций при сложном проценте

        B(T+k/p)(p) = B0*(1+i/p)^(p*(T+k/p))

        B0 - начальная сумма на депозите
        B(T+k/p) - сумма через Т лет (периодов) и дробную часть года (периода)
        T - количество лет (периодов)
        k - дробная честь года (периода)
        p - количество выплат в году (за период)
        i - процент по депозиту на год (период)

        :return: Сумму на счете в конце периода
        """
        fInterestRateForPer = self.fInterestRate / self.iPaymentNumber
        y = 1 + fInterestRateForPer
        if self.iTimeMonth:
            fTimeDeposit = (self.iTimeYears +
                            self.iTimeMonth / self.iPaymentNumber)
        else:
            fTimeDeposit = self.iTimeYears

        iPayNumAll = self.iPaymentNumber * fTimeDeposit
        fPow = pow(y, iPayNumAll)
        return round(self.fAmount * fPow, 2)

    def real_interest_rate(self):
        """ Разница в процентах

        :return: количество процентов
        """
        return (self.compound_interest() / self.interest() - 1) * 100


if __name__ == '__main__':
    depo = Deposit(130000, 0.10, 1)
    i = 12
    k = 1

    while k < i:
        k = k + 1
        depo.set_payment_number(k)
        print(depo.compound_interest())
