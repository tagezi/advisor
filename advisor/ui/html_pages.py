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
from PyQt6.QtWidgets import QTextBrowser

from advisor.lib.bond_analysis import BondAnalysis
from advisor.lib.constants import BONDFIELDSDICT, BONDFIELDSLIST
from advisor.lib.math import price_normalization
from advisor.lib.str import str_by_locale


class HTMLDoc:
    """ Класс содержит методы разбора и составления строк для формирования
        HTML документа

        **Члены класса**

        *lDoc*: Список строк для документа

        *dLinks*: словарь возможных ссылок на сторонние ресурсы
        """

    def __init__(self):
        self.lDoc = []
        self.lLink = []
        self.set_header()

    def set_header(self):
        self.lDoc.append('<!DOCTYPE html>')
        self.lDoc.append('<html><head>')
        self.set_style()
        self.lDoc.append('</head><body>')

    def set_style(self):
        self.lDoc.append('<style>')
        self.lDoc.append('h2 {margin-top: 20px;margin-bottom: 10px;}'
                         'table, th, td {'
                         'border: 1px solid white;'
                         'border-collapse: collapse;'
                         'font-size: 15px;'
                         'margin-top: 10px;'
                         '}'
                         '.center { text-align: center; }'
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

    def set_dict_to_table(self, dRows, lHeader=None):
        self.lDoc.append('<table>')
        if lHeader:
            self.set_table_header(lHeader)
        self.set_dict_to_table_row(dRows)
        self.lDoc.append('</table>')

    def set_table_header(self, lHeader):
        self.lDoc.append('<tr>')
        for sCell in lHeader:
            self.lDoc.append(f'<th>{sCell}</th>')
        self.lDoc.append('</tr>')

    def set_dict_to_table_row(self, dRows):
        for sKey in dRows:
            if dRows[sKey] and dRows[sKey] != '0000-00-00':
                self.lDoc.append('<tr>')
                self.lDoc.append(f'<td>{BONDFIELDSDICT[sKey]}: </td>')
                self.lDoc.append(f'<td> {dRows[sKey]}</td>')
                self.lDoc.append('</tr>')

    @staticmethod
    def set_df_to_table(oDF, lColumns):
        for column in oDF:
            oDF[column] = (oDF[column].apply(lambda x: str_by_locale(x)))
        oDF.columns = lColumns
        sHTML = oDF.to_html(index=False)
        sHTML = sHTML.replace(' style="text-align: right;"', '')
        sHTML = sHTML.replace('<td>', '<td class="center">')

        return sHTML

    def set_link(self, sLink):
        self.lDoc.append(f' {sLink} ')

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

    def _doc(self, sSECID):
        lBond = self.oConnector.get_bond_by_value(sSECID)
        self.oHTML.set_title_doc(f'Облигация {lBond[1]}')
        dBonds = dict(zip(BONDFIELDSLIST, lBond))
        iFaceValue = int
        for sKey in dBonds:
            if sKey == 'FACEVALUE':
                iFaceValue = dBonds[sKey]

            if (sKey == 'PREVWAPRICE' or sKey == 'PREVLEGALCLOSEPRICE'
                    or sKey == 'WAPRICE' or sKey == 'PREVPRICE'):
                dBonds[sKey] = price_normalization(float(dBonds[sKey]),
                                                   iFaceValue)

            if sKey == 'FACEUNIT' or sKey == 'CURRENCYID':
                dBonds[sKey] = 'рубли'

            if (sKey != 'LOTSIZE' and sKey != 'DECIMALS'
                    and sKey != 'MINSTEP' and sKey != 'LISTLEVEL'
                    and sKey != 'ISQUALIFIEDINVESTORS'):
                dBonds[sKey] = str_by_locale(dBonds[sKey])

            if (sKey == 'ISSUESIZE' or sKey == 'ISSUESIZEPLACED'
                    or sKey == 'COUPONPERIOD' or sKey == 'DURATION'
                    or sKey == 'DURATIONWAPRICE'):
                dBonds[sKey] = dBonds[sKey].split(',')[0]

        self.oHTML.set_dict_to_table(dBonds)

        self.oHTML.set_title_doc('Будущие купоны', 3)
        oBond = BondAnalysis(self.oConnector, oPD=pd)
        oFutureCoupons = oBond.get_future(sSECID, 'coupons')
        lColumns = ['Дата купона', 'Текущий номинал',
                    'Номинал купона', 'Процент купона']
        sFutureCoupons = self.oHTML.set_df_to_table(oFutureCoupons, lColumns)
        self.oHTML.set_string(sFutureCoupons)

        self.oHTML.set_title_doc('Амортизация', 3)
        oFutureAmort = oBond.get_future(sSECID, 'amort')
        lColumns = ['Дата амортизации', 'Текущий номинал',
                    'Процент от наминала', 'Сумма в единицах номинала']
        sFutureAmort = self.oHTML.set_df_to_table(oFutureAmort, lColumns)
        self.oHTML.set_string(sFutureAmort)

        self.oHTML.set_title_doc('Страницы облигации', 3)
        sLink = f'https://www.moex.com/ru/issue.aspx?code={sSECID}'
        self.oHTML.set_link(f'<a href="{sLink}">ММВБ</a>')
        sLink = f'https://smart-lab.ru/q/bonds/{sSECID}/'
        self.oHTML.set_link(f'<a href="{sLink}">Smart-Lab</a>')

        self.oHTML.set_title_doc('Новости об эмитенте', 3)
        sQuery = dBonds['EMITTER'].replace('"', '')
        sLink = (f'https://www.google.com/search?q={sQuery}'
                 '&num=10&newwindow=1&channel=fs&tbm=nws&sclient=gws-wiz-news')
        self.oHTML.set_link(f'<a href="{sLink}">Google</a>')
        sLink = (f'https://www.vedomosti.ru/search?query={sQuery}&sort=date'
                 '&doc_types=materials,press_releases'
                 '&material_types=news,articles')
        self.oHTML.set_link(f'<a href="{sLink}">Ведомости</a>')
        sLink = (f'https://tass.ru/search?text={sQuery}'
                 '&rubrics=v-strane,ekonomika,politika,nacionalnye-proekty,'
                 'mezhdunarodnaya-panorama,nedvizhimost,moskva,'
                 'moskovskaya-oblast,spb-news,ural-news,sibir-news,'
                 'arktika-segodnya')
        self.oHTML.set_link(f'<a href="{sLink}">TACC</a>')

        self.setText(self.oHTML.get_doc())


class InfoIssuer(HTMLPage):
    def __init__(self, oConnector, sSECID):
        super().__init__(oConnector, sSECID)


if __name__ == '__main__':
    pass
