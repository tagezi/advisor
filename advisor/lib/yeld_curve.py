#     This code is a part of program Advisor
#     Copyright (C) 2025 contributors Advisor
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
import numpy as np
from dateutil.utils import today
from datetime import datetime

from advisor.lib.constants import DAYS
from advisor.lib.math import get_KBD_in_year_precent
from advisor.lib.math import F_0_T_eff

class YeldCurve:
    def __init__(self, oConnector, oPD=pd):
        self.oPD = oPD
        self.oConnector = oConnector
        lQuery = oConnector.execute_query('SELECT * '
                                          'FROM YieldCurve '
                                          'ORDER BY tradedate DESC '
                                          'LIMIT 1;').fetchone()

        # Временные точки для расчета (например, от 0 до 30 лет)
        self.lTempVal = np.linspace(0.01, 20, 1500)
        # Значения КБД для расчета
        self.fBeta0 = lQuery[3]
        self.fBeta1 = lQuery[4]
        self.fBeta2 = lQuery[5]
        self.fTau = lQuery[6]
        self.lGValues = lQuery[7:]

    def get_KBD_values(self):
        """

        :return:
        """
        return get_KBD_in_year_precent(self.lTempVal,
                                       self.fBeta0, self.fBeta1, self.fBeta2,
                                       self.fTau,
                                       self.lGValues
                                       )

    def get_ofz_yeld(self):
        """

        :return:
        """
        oQuery = self.oConnector.get_bonds_by_value(pd=self.oPD, bOFZ=True)
        lMatData = oQuery['MATDATE'].tolist()
        lYield = oQuery['YIELDATPREVWAPRICE'].tolist()

        lDate = []
        for sDate in lMatData:
            oDate = datetime.strptime(sDate, "%Y-%m-%d")
            lDate.append(((oDate - today()).days / DAYS))

        return lDate, lYield

    def get_forwards_val(self):
        """

        :return:
        """
        return F_0_T_eff(self.lTempVal,
                         self.fBeta0, self.fBeta1, self.fBeta2,
                         self.fTau,
                         self.lGValues, dt=1e-4
                         )
