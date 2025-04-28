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

from pathlib import Path

import pandas as pd
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow
from dateutil.utils import today

from advisor.lib.bond_analysis import BondAnalysis
from advisor.lib.finance import Inflation
from advisor.lib.moex import MOEXUpdate
from advisor.lib.portfolio import Portfolio
from advisor.ui.help_dialog import About
from advisor.ui.setting_dialog import SettingDialog
from advisor.ui.tab_widget import TabWidget
from advisor.ui.table_widget import TableWidget

from advisor.lib.config import ConfigProgram
from advisor.lib.math import ofz_bond_profit, ofz_bond_profit_percent, \
    percent_year, by_inflation, price_normalization, face_value_inflation
from advisor.lib.sql import SQL, check_connect_db
from advisor.lib.str import str_get_file_patch
from advisor.ui.tool_dialogs import SelectBondsDialog


class MainWindow(QMainWindow):
    def __init__(self, sPath):
        """

        :type sPath: str
        """
        super().__init__()

        self.oExportToCSV = None
        self.oOFZBondAnalysis = None
        self.oBondAnalysis = None
        self.oStockAnalysis = None
        self.BondAnalysis = None
        self.BondYieldTable = None
        self.AccProfitability = None
        self.OfferCost = None
        self.OfferAsset = None
        self.oImportStock = None
        self.oRecalcAsset = None
        self.oAbout = None
        self.oOpenHelp = None
        self.oExitAct = None
        self.oSetting = None
        self.oOpenDB = None
        self.oFind = None
        self.oTableDataOFZ = pd.DataFrame()
        self.sPathApp = sPath
        oConfigProgram = ConfigProgram(self.sPathApp)
        sBasePath = oConfigProgram.sDir
        sDBPath = oConfigProgram.get_config_value('DB', 'db_path')
        sDBDir = oConfigProgram.get_config_value('DB', 'db_dir')
        if not sDBPath:
            sDBFile = oConfigProgram.get_config_value('DB', 'db_file')
            sDBPath = str_get_file_patch(sBasePath, sDBDir)
            sDBPath = str_get_file_patch(sDBPath, sDBFile)

        self.oConnector = SQL(sDBPath)
        check_connect_db(self.oConnector, sBasePath, sDBDir, sDBFile)
        self.setWindowTitle('Advisor')
        self.oCentralWidget = TabWidget(self)
        self.onPortfolio()
        self.create_actions()
        self.connect_actions()
        self.set_menu_bar()
        self.setCentralWidget(self.oCentralWidget)
        self.onSetStatusBarMessage()
        self.showMaximized()

    def create_actions(self):
        """ Method collect all actions which can do from GUI of program. """
        # File menu
        self.oOpenDB = QAction('Открыть базу данных...', self)
        self.oImportStock = QAction('Обновить базу данных онлайн', self)
        self.oExportToCSV = QAction('Экспортировать в CSV', self)
        self.oSetting = QAction('Настройка...')
        self.oExitAct = QAction(QIcon.fromTheme('SP_exit'), 'Выход', self)
        self.oExitAct.setShortcut('Ctrl+Q')
        self.oExitAct.setStatusTip('Закрыть приложение')

        # Edit
        self.oFind = QAction('Искать...', self)
        self.oFind.setShortcut('Ctrl+F')

        # Tools
        self.oStockAnalysis = QAction('Таблица акций')
        self.oBondAnalysis = QAction('Таблица облигаций')
        self.oOFZBondAnalysis = QAction('Таблица ОФЗ')

        # Help
        self.oOpenHelp = QAction('Справка....', self)
        self.oAbout = QAction('О программе...', self)

    # Setters
    def set_menu_bar(self):
        """ Method create Menu Bar on main window of program GUI. """
        oMenuBar = self.menuBar()

        # Create file menu
        oFileMenu = oMenuBar.addMenu('&Файл')
        oFileMenu.addAction(self.oOpenDB)
        oFileMenu.addAction(self.oImportStock)
        oFileMenu.addAction(self.oExportToCSV)
        oFileMenu.addAction(self.oSetting)
        oFileMenu.addSeparator()
        oFileMenu.addAction(self.oExitAct)

        # Create Edit menu
        oEdit = oMenuBar.addMenu('&Правка')
        oEdit.addAction(self.oFind)

        # Create Tool menu
        oTools = oMenuBar.addMenu('&Инструменты')
        oTools.addAction(self.oStockAnalysis)
        oFileMenu.addSeparator()
        oTools.addAction(self.oBondAnalysis)
        oTools.addAction(self.oOFZBondAnalysis)

        # Create Help menu
        oHelpMenu = oMenuBar.addMenu('&Справка')
        oHelpMenu.addAction(self.oOpenHelp)
        oHelpMenu.addAction(self.oAbout)

    def onPortfolio(self):
        oPortfolio = Portfolio(self.oConnector)

        dTableData = oPortfolio.portfolio_data()
        oTableWidget = TableWidget(dTableData)

        self.oCentralWidget.add_tab(oTableWidget, 'Портфель')

    def connect_actions(self):
        """ It is PyQt6 slots or other words is connecting from GUI element to
        method or function in program. """
        # Menu File
        self.oOpenDB.triggered.connect(self.onOpenDB)
        self.oImportStock.triggered.connect(self.onImportStock)
        self.oExportToCSV.triggered.connect(self.onExportToCSV)
        self.oSetting.triggered.connect(self.onOpenSetting)
        self.oExitAct.triggered.connect(QApplication.quit)

        # Menu Edit

        # Tool menu
        self.oBondAnalysis.triggered.connect(self.onBoundSelect)
        self.oOFZBondAnalysis.triggered.connect(self.onOFZBondAnalysis)

        # Menu Help
        self.oAbout.triggered.connect(self.onDisplayAbout)

    @staticmethod
    def get_data(oTableData, sSECID):
        # Выбираем строку и подготавливаем её
        oRowData = oTableData.loc[oTableData['SECID'] == sSECID]
        oRowData = oRowData.set_index('SECID')
        # Текущий номинал
        iFaceValue = oRowData.loc[sSECID, 'FACEVALUE']
        # Цена предыдущего дня
        fPrice = oRowData.loc[sSECID, 'PREVPRICE']
        # НКД
        fACC = oRowData.loc[sSECID, 'ACCRUEDINT']
        # Дата погашения
        sMatDate = oRowData.loc[sSECID, 'MATDATE']
        # переводим цену из процентов в валюту номинала
        fPrice = price_normalization(fPrice, iFaceValue)

        return fPrice, fACC, sMatDate

    def bond_analysis(self, dTableData, oTableData,
                      fInflMedian5, fInflMedian10,
                      iMinPeriod=30, iMaxPeriod=181):
        """

        :param dTableData:
        :param oTableData:
        :type oTableData: pd.DataFrame
        :param fInflMedian5: медианная инфляция за 5 лет
        :type fInflMedian5: float
        :param fInflMedian10: медианная инфляция за 10 лет
        :type fInflMedian10: float
        :return:
        :rtype: pd.DataFrame
        """
        # IAPPY - Inflation-adjusted profit as a percentage in year
        lIAPPY5Tax, lIAPPY10Tax = [], []
        for sSECID in oTableData['SECID']:
            bAmort = dTableData.get_check_amort(sSECID=sSECID)
            if bAmort:
                oTableData.drop(
                    oTableData[
                        oTableData['SECID'] == sSECID].index, inplace=True
                )
                continue

            fPrice, fACC, sMatDate = self.get_data(oTableData, sSECID)
            oUpCoupons = dTableData.get_future_coupons(sSECID=sSECID)
            # высчитываем значения и купоны с учетом инфляции
            fFaceValue5 = face_value_inflation(fInflMedian5, oUpCoupons)
            lInflUpCoupons5 = by_inflation(fInflMedian5, oUpCoupons)
            fFaceValue10 = face_value_inflation(fInflMedian10, oUpCoupons)
            lInflUpCoupons10 = by_inflation(fInflMedian10, oUpCoupons)
            # находим сумму купонов
            fInfSumValue5 = sum(lInflUpCoupons5)
            fInfSumValue10 = sum(lInflUpCoupons10)
            # высчитываем прибыль с учетом комиссий и налога
            fProfitInfl5Tax = ofz_bond_profit(fInfSumValue5, fACC, fFaceValue5,
                                              fPrice, sDate=sMatDate,
                                              bTax=True)
            fProfitInfl10Tax = ofz_bond_profit(fInfSumValue10, fACC,
                                               fFaceValue10, fPrice,
                                               sDate=sMatDate, bTax=True)
            # Считаем доход в процентах
            fIAPP5Tax = ofz_bond_profit_percent(fProfitInfl5Tax, fPrice)
            fIAPP10Tax = ofz_bond_profit_percent(fProfitInfl10Tax, fPrice)
            # считаем доход в процентах в год
            lIAPPY5Tax.append(percent_year(fIAPP5Tax, sMatDate))
            lIAPPY10Tax.append(percent_year(fIAPP10Tax, sMatDate))
        # формируем новую таблицу
        oTableData.insert(7, 'Процент (инфл 5) в год, %', lIAPPY5Tax)
        oTableData.insert(8, 'Процент (инфл 10) в год, %', lIAPPY10Tax)
        oTableData = oTableData.drop(columns=['ISIN', 'FACEUNIT'])

        oTableData.columns = ['ID', 'Имя', 'Дата погашения', 'Цена, %',
                              'Доходность, %', 'Эффективная, %',
                              '% в год при сред. инфл. за 5л)',
                              '% в год при сред. инфл за 10л)',
                              'Процент купона', 'Значение купона, руб', 'НКД',
                              'Следующий купон', 'Период купона',
                              'Начальный номинал', 'Текущий номинал',
                              'Уровень листинга', 'Эмитент']
        oTableData = oTableData[
            oTableData['% в год при сред. инфл. за 5л)'] > 0]

        return oTableData

    def onBondAnalysis(self, iMinPeriod=30, iMaxPeriod=181):
        # Инфляция
        oInflation = Inflation(self.oConnector)
        fInflMedian5 = oInflation.inflation_median_for_5()
        fInflMedian10 = oInflation.inflation_average_for_10()
        # Отбираем список облигаций
        dTableData = BondAnalysis(self.oConnector)
        oTableData = dTableData.get_bond_by_values(iMinPeriod=iMinPeriod,
                                                   iMaxPeriod=iMaxPeriod)
        oTableData = self.bond_analysis(dTableData,
                                        oTableData,
                                        fInflMedian5,
                                        fInflMedian10)
        oTableData = oTableData.dropna()

        # запускаем всю эту херь
        oTableWidget = TableWidget(oTableData, True)
        self.oCentralWidget.add_tab(oTableWidget, 'Список облигаций')

    def get_period_list(self):
        tList = self.oConnector.get_period_list()

        return [str(tRow[0]) for tRow in tList]

    def onBoundSelect(self):
        oSelectBondsDialog = SelectBondsDialog(self.oConnector)
        oSelectBondsDialog.exec()
        oSelectBondsDialog.GetValue()
        lPeriods = oSelectBondsDialog.GetValue()
        self.onBondAnalysis(lPeriods[0], lPeriods[1])

    def onOFZBondAnalysis(self):
        # Инфляция
        oInflation = Inflation(self.oConnector)
        fInflMedian5 = oInflation.inflation_median_for_5()
        fInflMedian10 = oInflation.inflation_average_for_10()
        # Отбираем список облигаций
        dTableData = BondAnalysis(self.oConnector)
        oTableData = dTableData.get_bond_by_values(bOFZ=True)

        oTableData = self.bond_analysis(dTableData,
                                        oTableData,
                                        fInflMedian5,
                                        fInflMedian10)

        # запускаем всю эту херь
        oTableWidget = TableWidget(oTableData, True)

        self.oCentralWidget.add_tab(oTableWidget, 'Список ОФЗ')

    def onDisplayAbout(self):
        """ Method open dialog window with information about the program. """
        oAbout = About(self)
        oAbout.exec()

    def onImportStock(self):
        aMOEX = MOEXUpdate(self.oConnector)
        # обновляет облигации
        aMOEX.get_collection(sType='ОФЗ', iLevel=0)
        aMOEX.get_collection(sType='Корпоративные', iLevel=0)
        aMOEX.get_collection(sType='Муниципальные', iLevel=0)
        aMOEX.get_collection(sType='Биржевые', iLevel=0)
        aMOEX.get_collection(sType='Субъектов РФ', iLevel=0)
        aMOEX.get_markets_bonds()
        # обновляем акции
        aMOEX.get_collection(sGroup='stock_shares_tplus',
                             sCollectionName='stock_shares_one')
        aMOEX.get_collection(sGroup='stock_shares_tplus',
                             sCollectionName='stock_shares_two')

    def onExportToCSV(self):
        iIndex = self.oCentralWidget.currentIndex()
        oTable = self.oCentralWidget.findChildren(TableWidget)
        oData = today().strftime('%Y%m%d')
        filepath = Path(f'')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        oTable[iIndex].dTableData.to_csv(filepath, decimal=',',
                                         date_format='%Y.%m.%d')

    def onOpenDB(self):
        pass

    def onOpenSetting(self):
        oSettingDialog = SettingDialog(self.oConnector, self.sPathApp, self)
        oSettingDialog.exec()

    def onSetStatusBarMessage(self, sMassage='Ready'):
        """ Method create Status Bar on main window of program GUI. """
        self.statusBar().showMessage(sMassage)
