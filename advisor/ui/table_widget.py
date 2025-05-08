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

import webbrowser

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableView

from advisor.lib.constants import COLORYIELD, COLODMATDATE
from advisor.lib.math import bring_number_into_range, years


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, DataFrame, bColor=False, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._DataFrame = DataFrame
        self.bColor = bColor

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._DataFrame)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._DataFrame.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._DataFrame.iloc[index.row(), index.column()])

        if self.bColor:
            if role == Qt.ItemDataRole.BackgroundRole:
                fValue = self._DataFrame.iloc[index.row(), index.column()]
                if isinstance(fValue, int) or isinstance(fValue, float):
                    lColor = COLORYIELD.copy()
                    if (self._DataFrame.columns[index.column()] == 'Цена, %' or
                            self._DataFrame.columns[index.column()] == 'НКД'):
                        lColor.reverse()
                    fMin = self._DataFrame.iloc[:, index.column()].min()
                    fMax = self._DataFrame.iloc[:, index.column()].max()
                    fMedian = self._DataFrame.iloc[:, index.column()].median()
                    if fValue < fMedian:
                        iValue = bring_number_into_range(fValue, fMin,
                                                         fMedian,
                                                         max_dest=19)
                    else:
                        iValue = bring_number_into_range(fValue, fMedian,
                                                         fMax, min_dest=20)

                    return QColor(lColor[iValue])

                if self._DataFrame.columns[index.column()] == 'Дата погашения':
                    lColor = COLODMATDATE.copy()
                    fYears = years(self._DataFrame.iloc[
                                       index.row(), index.column()
                                   ])
                    if fYears < 1:
                        return QColor(lColor[0])
                    elif 1 < fYears < 3:
                        return QColor(lColor[1])
                    elif 3 <= fYears < 7:
                        return QColor(lColor[2])

                    return QColor(lColor[3])

        return None

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role: Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as
        horizontal header data.
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._DataFrame.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._DataFrame.index[section])

        return None


class TableWidget(QTableView):
    def __init__(self, data, bColor=False):
        super().__init__()
        self.dTableData = data
        self.bColor = bColor
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.actions_connect()

    def actions_connect(self):
        self.doubleClicked.connect(self.onOpenSESID)

    def onOpenSESID(self, item):
        sItem = item.data()
        if (item.column() == 0 or item.column() == 1
                and sItem != 'Акции' and sItem != 'Облигации'
                and sItem != 'Имя'):
            self.window().onBondInfo(sItem)
        if item.column() == 16:
            webbrowser.open_new_tab(
                f'https://www.google.com/search?q={item.data()}')

    def setData(self):
        oModel = PandasModel(self.dTableData, self.bColor)
        self.setModel(oModel)


if __name__ == '__main__':
    pass
