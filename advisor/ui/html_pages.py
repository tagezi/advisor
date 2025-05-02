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

from PyQt6.QtWidgets import QTextBrowser

from advisor.lib.constants import BONDFIELDSDICT, BONDFIELDSLIST


class HTMLDoc:
    """ Класс содержит методы разбора и оставления строк для формирования
        HTML документа

        **Члены класса**

        *lDoc*: Список строк для документа

        *dLinks*: словарь возможных ссылок на сторонние ресурсы
        """

    def __init__(self):
        self.lDoc = []
        self.dLinks = {}
        self.set_header()

    def set_header(self):
        self.lDoc.append('<!DOCTYPE html>')
        self.lDoc.append('<html><head>')
        self.set_style()
        self.lDoc.append('</head><body>')

    def set_style(self):
        self.lDoc.append('<style>')
        self.lDoc.append('table, th, td'
                         '{'
                         ' border: 1px solid white;'
                         ' border-collapse: collapse;'
                         'font-size: 15px;'
                         '}'
                         )
        self.lDoc.append('</style>')

    def set_title_doc(self, sTitle, iLevel=2):
        """ Форматирует заголовок документа из составляющих имени и ранга
         таксона.

        :param iLevel: уровень заголовка
        :type iLevel: int
        :param sTitle: ранг таксона
        :type sTitle: str
        :return: none
        """
        self.lDoc.append(f'<h{iLevel}>{sTitle}</h{iLevel}>')

    def set_string(self, String):
        """ Устанавливает строку и переводит каретку в формате HTML

        :param String: Строка для добавления в список
        :type String: str
        :return: None
        """
        self.lDoc.append(f'{String}<br>')

    def set_table(self, dRows, lHeader=None):
        self.lDoc.append('<table>')
        if lHeader:
            self.set_table_header(lHeader)
        self.set_table_row(dRows)
        self.lDoc.append('</table>')

    def set_table_header(self, lHeader):
        self.lDoc.append('<tr>')
        for sCell in lHeader:
            self.lDoc.append(f'<th>{sCell}</th>')
        self.lDoc.append('</tr>')

    def set_table_row(self, dRows):
        for sKey in dRows:
            if dRows[sKey]:
                self.lDoc.append('<tr>')
                self.lDoc.append(f'<td>{BONDFIELDSDICT[sKey]}: </td>')
                self.lDoc.append(f'<td> {dRows[sKey]}</td>')
                self.lDoc.append('</tr>')

    def set_no_data(self):
        self.lDoc.append('!!! Нет данных!!!')

    def get_doc(self):
        return ''.join(self.lDoc)


class HTMLPage(QTextBrowser):
    def __init__(self, oConnector, sSECID):
        super().__init__()
        self.oConnector = oConnector
        self.sSciName = sSECID
        self.oHTML = HTMLDoc()
        self.dField = {}
        self.setOpenExternalLinks(True)


class InfoBonds(HTMLPage):
    def __init__(self, oConnector, sSECID):
        super().__init__(oConnector, sSECID)
        self._doc(sSECID)
        self.dField = BONDFIELDSDICT

    def _doc(self, sSECID):
        lBond = self.oConnector.get_bond_by_value(sSECID)
        self.oHTML.set_title_doc(f'Облигация {lBond[1]}')
        self.oHTML.set_table(dict(zip(BONDFIELDSLIST, lBond)))
        self.setText(self.oHTML.get_doc())


class InfoIssuer(HTMLPage):
    def __init__(self, oConnector, sSECID):
        super().__init__(oConnector, sSECID)


if __name__ == '__main__':
    pass
