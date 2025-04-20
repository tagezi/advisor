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

import csv
import pandas as pd

from advisor.lib.sql import SQL

fFile = ""
sName = 'LKOH'
sFileDB = ''
oConn = SQL(sFileDB)


def import_csv_reports(sFile=fFile, sCompanyName=sName, oConnector=oConn):
    dfTable = pd.read_csv(sFile)
    lReportIndexes = dfTable['1'].to_list()
    dfTable.drop(labels=['1'], axis=1, inplace=True)
    df = dfTable.transpose()
    df.insert(loc=0, column='Company',
              value=[sCompanyName for i in range(df.shape[0])])
    Llist = df.values.tolist()

    new_column = ['Company']
    for sIndexRu in lReportIndexes:
        lSearchIndexRu = sIndexRu.rsplit(',', 2)
        sSearchIndexRu = lSearchIndexRu[0]
        sQuery = oConnector.sql_get_values('EmitterDict',
                                           'field_index',
                                           'field_index_ru',
                                           (sSearchIndexRu,))
        sIndexEn = sQuery[0][0].replace(' ', '_').replace('/', '_')
        sIndexEn = sIndexEn.replace('&', '').replace('.', '')
        new_column.append(sIndexEn)

    sColumns = ', '.join(new_column)
    for tValues in Llist:
        oConnector.insert_row('Emitter', sColumns, tValues)


def update_emitter():
    fFile = "/home/lera/Документы/Финансы/Privilege_17.04.2025.csv"
    with open(fFile, newline='') as csvfile:
        CSV = csv.reader(csvfile, delimiter=';')
        for row in CSV:
            bAnswer = oConn.check_value('BondDescription', 'SECID',
                                        'SECID', row[0],)
            if bAnswer:
                oConn.update('BondDescription', 'EMITTER',
                             'SECID', (row[1], row[0]))


if __name__ == '__main__':
    update_emitter()
