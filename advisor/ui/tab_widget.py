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

from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout


class TabWidget(QTabWidget):
    def __init__(self, oParent):
        super(TabWidget, self).__init__(oParent)
        self.oTab = None

        self.setMovable(True)
        self.setTabPosition(QTabWidget.tabPosition(self).South)
        self.setTabShape(QTabWidget.tabShape(self).Triangular)
        self.setTabsClosable(True)

        self.connect_actions()

    def connect_actions(self):
        self.tabCloseRequested.connect(self.onCloseTab)

    def add_tab(self, oWidget=None, sName=''):
        # Initialize tab screen
        self.oTab = QWidget()

        # Add tabs
        self.addTab(self.oTab, sName)

        # Create tab content
        if oWidget:
            self.oTab.layout = QVBoxLayout(self)
            self.oTab.layout.addWidget(oWidget)
            self.oTab.setLayout(self.oTab.layout)

        iIndexTab = self.count() - 1
        self.update_tab_name(iIndexTab, sName)
        self.setCurrentIndex(iIndexTab)

    def onCloseTab(self, index):
        if self.count() < 2:
            return
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()

    def update_tab_name(self, iTabIndex=0, sTabName='Table 1'):
        self.setTabText(iTabIndex, sTabName)


if __name__ == '__main__':
    pass
