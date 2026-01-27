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

import numpy as np
import pandas as pd
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow
from dateutil.utils import today

from advisor.lib.bond_analysis import bond_analysis_without, bond_analysis_ofz
from advisor.lib.constants import Constants
from advisor.lib.moex import MOEXUpdate
from advisor.lib.portfolio import Portfolio
from advisor.ui.help_dialog import About
from advisor.ui.html_pages import InfoBonds
from advisor.ui.plots import MplCanvas
from advisor.ui.setting_dialog import SettingDialog
from advisor.ui.tab_widget import TabWidget
from advisor.ui.table_widget import TableWidget

from advisor.lib.config import ConfigProgram
from advisor.lib.sql import SQL, check_connect_db
from advisor.lib.str import str_get_file_patch
from advisor.ui.tool_dialogs import SelectBondsDialog
from advisor.lib.yeld_curve import YeldCurve


class MainWindow(QMainWindow):
    def __init__(self, sPath, oConfig):
        """

        :param sPath:
        :type sPath: str
        """
        super().__init__()

        self.oYieldCurve = None
        self.oForwardRate = None
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
        self.oConstants = Constants(oConfig)
        sDBFile = None
        sBasePath = self.oConstants.sBasePath
        sDBPath = self.oConstants.DB_PATH
        sDBDir = self.oConstants.DBDIR
        if not sDBPath:
            sDBFile = self.oConstants.DBFILE
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

        # Plots
        self.oYieldCurve = QAction('Кривая бескупонной доходности')
        self.oForwardRate = QAction('Форвардная кривая')
        self.oTrandLine = QAction('Тренд')

        # Info
        self.oBoundInfo = QAction('Облигация')
        self.oShareInfo = QAction('Акция')
        self.oIssuerInfo = QAction('Эмитент')

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
        oEditMenu = oMenuBar.addMenu('&Правка')
        oEditMenu.addAction(self.oFind)

        # Create Tool menu
        oToolsMenu = oMenuBar.addMenu('&Инструменты')
        oToolsMenu.addAction(self.oStockAnalysis)
        oToolsMenu.addSeparator()
        oToolsMenu.addAction(self.oBondAnalysis)
        oToolsMenu.addAction(self.oOFZBondAnalysis)

        # Create Plots
        oPlotsMenu = oMenuBar.addMenu('&Диаграммы')
        oPlotsMenu.addAction(self.oYieldCurve)
        oPlotsMenu.addAction(self.oForwardRate)
        oPlotsMenu.addAction(self.oTrandLine)

        # Create Info menu
        oInfoMenu = oMenuBar.addMenu('&Данные')
        oInfoMenu.addAction(self.oBoundInfo)
        oInfoMenu.addAction(self.oShareInfo)
        oInfoMenu.addAction(self.oIssuerInfo)

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

        # Plots Menu
        self.oYieldCurve.triggered.connect(self.onYieldCurvePlots)
        self.oForwardRate.triggered.connect(self.onForwardRatePlots)
        self.oTrandLine.triggered.connect(self.onTrandLinePlots)

        # Menu Help
        self.oAbout.triggered.connect(self.onDisplayAbout)

    def onTrandLinePlots(self):
        """

        """
        oCanvas = MplCanvas(self)
        oYeldCurve = YeldCurve(self.oConnector)
        lTempVal = oYeldCurve.lTempVal
        lKBDValues = oYeldCurve.get_KBD_values()
        lDate, lYield = oYeldCurve.get_ofz_yeld(self.oConstants.DAYS)
        lCoefs = np.polyfit(lDate, lYield, deg=2)
        lXs = np.linspace(min(lDate), max(lDate), 100)
        oP = np.poly1d(lCoefs)
        lYs = oP(lXs)
        oCanvas.ax.plot(lXs, lYs, color='green', label='Линия тренда')
        oCanvas.ax.plot(lTempVal, lKBDValues, label='КБД Мосбиржи',
                        linestyle='-', color='red')
        fMin = min(min(lKBDValues), min(lYield))
        fMax = max(max(lKBDValues), max(lYield))
        oCanvas.ax.set_ylim(fMin - fMin * 0.04, fMax + fMax * 0.04)
        oCanvas.ax.scatter(lDate, lYield, label='Доходность ОФЗ', color='blue')
        oCanvas.ax.set_xlabel('Срок до погашения, лет', fontsize=14)
        oCanvas.ax.set_ylabel('Доходность, %', fontsize=14)
        sTitle = "Доходность ОФЗ, кривая доходности и лирия тренда"
        oCanvas.ax.set_title(sTitle, fontsize=22)
        oCanvas.ax.grid(linestyle='--', color='gray', linewidth=0.8, alpha=0.7)
        oCanvas.ax.legend(fontsize=14)
        self.oCentralWidget.add_tab(oCanvas, sTitle)

    def onYieldCurvePlots(self):
        """

        """
        oCanvas = MplCanvas(self)
        oYeldCurve = YeldCurve(self.oConnector)
        lTempVal = oYeldCurve.lTempVal
        lKBDValues = oYeldCurve.get_KBD_values()
        lDate, lYield = oYeldCurve.get_ofz_yeld()
        oCanvas.ax.plot(lTempVal, lKBDValues, label='КБД Мосбиржи',
                        linestyle='-', color='red')
        fMin = min(min(lKBDValues), min(lYield))
        fMax = max(max(lKBDValues), max(lYield))
        oCanvas.ax.set_ylim(fMin - fMin * 0.04, fMax + fMax * 0.04)
        oCanvas.ax.scatter(lDate, lYield, label='Доходность ОФЗ', color='blue')
        oCanvas.ax.set_xlabel('Срок до погашения, лет', fontsize=14)
        oCanvas.ax.set_ylabel('Доходность, %', fontsize=14)
        sTitle = 'Кривая бескупонной доходности ОФЗ'
        oCanvas.ax.set_title(sTitle, fontsize=22)
        oCanvas.ax.grid(linestyle='--', color='gray', linewidth=0.8, alpha=0.7)
        oCanvas.ax.legend(fontsize=14)
        self.oCentralWidget.add_tab(oCanvas, sTitle)

    def onForwardRatePlots(self):
        """

        """
        oCanvas = MplCanvas(self)
        oYeldCurve = YeldCurve(self.oConnector)
        lTempVal = oYeldCurve.lTempVal
        lKBDValues = oYeldCurve.get_KBD_values()
        lForwardVal = oYeldCurve.get_forwards_val()
        fMin = min(min(lKBDValues), min(lForwardVal))
        fMax = max(max(lKBDValues), max(lForwardVal))
        oCanvas.ax.set_ylim(fMin - fMin * 0.04, fMax + fMax * 0.04)
        oCanvas.ax.plot(lTempVal, lKBDValues, label='Спотовая кривая',
                        linestyle='-', color='red')
        oCanvas.ax.plot(lTempVal, lForwardVal, label='Форвардная кривая',
                        linestyle='-', color='green')
        oCanvas.ax.set_xlabel('Срок до погашения, лет', fontsize=14)
        oCanvas.ax.set_ylabel('Доходность, %', fontsize=14)
        sTitle = 'Спотовая и форвардная кривые'
        oCanvas.ax.set_title(sTitle, fontsize=22)
        oCanvas.ax.grid(linestyle='--', color='gray', linewidth=0.8, alpha=0.7)
        oCanvas.ax.legend(fontsize=14)
        self.oCentralWidget.add_tab(oCanvas, sTitle)

    def onBondAnalysis(self, iMinPeriod=30, iMaxPeriod=181, fPercent=1):
        oTableData = bond_analysis_without(self.oConnector,
                                           iMinPeriod,
                                           iMaxPeriod,
                                           fPercent)

        # запускаем всю эту херь
        oTableWidget = TableWidget(oTableData, bColor=True,
                                   lColorYield=self.oConstants.COLORYIELD,
                                   lColorMatDate=self.oConstants.COLORMATDATE)
        self.oCentralWidget.add_tab(oTableWidget, 'Список облигаций')

    def onBondInfo(self, sSECID):
        oBondInfo = InfoBonds(self.oConnector, sSECID)
        self.oCentralWidget.add_tab(oBondInfo, sSECID)

    def onBoundSelect(self):
        oSelectBondsDialog = SelectBondsDialog(self.oConnector)
        oSelectBondsDialog.exec()
        lData = oSelectBondsDialog.GetValue()
        self.onBondAnalysis(lData[0], lData[1], lData[2])

    def onDisplayAbout(self):
        """ Method open dialog window with information about the program. """
        oAbout = About(self)
        oAbout.exec()

    def onImportStock(self):
        aMOEX = MOEXUpdate(self.oConnector)
        # обновляет данные для Кривой бескупонной доходности
        aMOEX.get_kbd()
        # обновляет облигации
        aMOEX.get_collection(sType='ОФЗ', iLevel=0)
        aMOEX.get_collection(sType='Корпоративные', iLevel=0)
        aMOEX.get_collection(sType='Муниципальные', iLevel=0)
        aMOEX.get_collection(sType='Биржевые', iLevel=0)
        aMOEX.get_collection(sType='Субъектов РФ', iLevel=0)
        aMOEX.get_markets_bonds()
        aMOEX.get_bond_description()
        # обновляем акции
        aMOEX.get_collection(sGroup='stock_shares_tplus',
                             sCollectionName='stock_shares_one')
        aMOEX.get_collection(sGroup='stock_shares_tplus',
                             sCollectionName='stock_shares_two')
        aMOEX.get_markets_shares()

    def onExportToCSV(self):
        iIndex = self.oCentralWidget.currentIndex()
        oTable = self.oCentralWidget.findChildren(TableWidget)
        oData = today().strftime('%Y%m%d')
        filepath = Path(f'~/{oData}.csv')
        filepath.parent.mkdir(parents=True, exist_ok=True)
        oTable[iIndex].dTableData.to_csv(filepath, decimal=',',
                                         date_format='%Y.%m.%d')

    def onOFZBondAnalysis(self):
        oTableData = bond_analysis_ofz(self.oConnector)

        # запускаем всю эту херь
        oTableWidget = TableWidget(oTableData, bColor=True,
                                   lColorYield=self.oConstants.COLORYIELD,
                                   lColorMatDate=self.oConstants.COLORMATDATE)
        self.oCentralWidget.add_tab(oTableWidget, 'Список ОФЗ')

    def onOpenDB(self):
        pass

    def onOpenSetting(self):
        oSettingDialog = SettingDialog(self.oConnector, self.sPathApp, self)
        oSettingDialog.exec()

    def onSetStatusBarMessage(self, sMassage='Ready'):
        """ Method create Status Bar on main window of program GUI. """
        self.statusBar().showMessage(sMassage)
