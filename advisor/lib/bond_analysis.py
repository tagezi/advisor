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

from advisor.lib.moex import MOEX
from advisor.lib.sql import SQL
from advisor.lib.constants import FILE_DB


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

    def get_future_coupons(self, sSECID):
        """

        :param sSECID:
        :type sSECID: str
        :return:DataFrame
        """
        oCoupons = self.check_is_in_db(sSECID, 'coupons')
        oFuturesCoupons = oCoupons.loc[(oCoupons['coupon_date'] > self.sTime)]

        return oFuturesCoupons


if __name__ == '__main__':
    oConn = SQL(FILE_DB)
    s = BondAnalysis(oConn, pd)
    s.get_future_coupons('SU26229RMFS3')
