#     This code is a part of program Advisor
#     Copyright (C) 2026 contributors Advisor
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

import matplotlib
matplotlib.use('qtagg')
import mplcursors

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from advisor.lib.yeld_curve import YeldCurve

def choice_title(sShowing):
    """ Выбор подписи для вкладки при выводе диаграммы.

    :param sShowing: Код текста: 'forward', 'kbd' или ''
    :type sShowing: str
    :return: Текст подписи
    :rtype: str

    """
    if sShowing == 'forward':
        sTitle = 'Спотовая и форвардная кривые'
    elif sShowing == 'kbd':
        sTitle = 'Кривая бескупонной доходности ОФЗ'
    else:
        sTitle = 'Доходность ОФЗ, кривая доходности и линия тренда'
    
    return sTitle


class MplCanvas(FigureCanvas):
    """
    A custom Matplotlib canvas embedded in a PyQt6 widget.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """ Create a figure and axes.

        :param parent: Родительский виджет в интерфейсе , defaults to None
        :type parent: obj, optional
        :param width: ширина создаваемой фигуры, defaults to 5
        :type width: int, optional
        :param height: высота создаваемой фигуры, defaults to 4
        :type height: int, optional
        :param dpi: Определяет итоговое разрешение холста, defaults to 100
        :type dpi: int, optional

        """
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        
    def create_plots(self, oConnector, iDays, sShowing='full'):
        """ Настройка графика.

        :param oConnector: Доступ к базе данных и API класса SQL
        :type oConnector: advisor.lib.sql.SQL
        :param iDays: Количество дней в году
        :type iDays: int
        :param showing: Тип диаграмы, которая будет показана.
            Возможны значения: forward, kbd, full. По умолчанию, full
        :type showing: str, optional
        :return: Возвращает кортеж из холста и заголовка диаграммы для 
            встраивания в интерфейс 
        :rtype: [matplotlib.backends.backend_qtagg.FigureCanvasQTAgg, str]

        """
        oYeldCurve = YeldCurve(oConnector)

        # выводим линию тренда
        self.lNames, lDate, lYield = oYeldCurve.get_ofz_yeld(iDays)
        lXs = np.linspace(min(lDate), max(lDate), 100)
        lCoefs = np.polyfit(lDate, lYield, deg=2)
        oP = np.poly1d(lCoefs)
        lYs = oP(lXs)
        self.ax.plot(lXs, lYs,                              # x, y
                     color='green',
                     label='Линия тренда')

        # вывдим спотовую кривую (кривую бескупонной доходности)
        lTempVal = oYeldCurve.lTempVal
        lKBDValues = oYeldCurve.get_KBD_values()
        self.ax.plot(lTempVal, lKBDValues,                  # x, y
                     label='Спотовая кривая',
                     linestyle='-',
                     color='red')

        # выводим форвардную кривую
        lForwardVal = oYeldCurve.get_forwards_val()
        self.ax.plot(lTempVal, lForwardVal,                # x, y
                     label='Форвардная кривая',
                     linestyle='-',
                     color='black')

        # выводим график рассеивания доходности ОФЗ
        oScatter = self.ax.scatter(lDate, lYield,          # x, y
                                   label='Доходность ОФЗ',
                                   color='blue')

        # ограничиваем поле диаграммы
        fMin = min(min(lKBDValues), min(lForwardVal))
        fMax = max(max(lKBDValues), max(lForwardVal))
        self.ax.set_ylim(fMin - fMin * 0.04, fMax + fMax * 0.04)

        # ограничиваем деления по осо x одним годом
        self.ax.set_xticks(np.arange(0, max(lTempVal)+1, 1))

        # подписи осей
        self.ax.set_xlabel(xlabel='Срок до погашения, лет', fontsize=14)
        self.ax.set_ylabel(ylabel='Доходность, %', fontsize=14)

        # задаём заголовок
        sTitle = choice_title(sShowing)
        self.ax.set_title(label=sTitle, fontsize=22)

        # расчерчиваем сетку на диаграмме
        self.ax.grid(linestyle='--',
                     color='gray',
                     linewidth=0.8,
                     alpha=0.7)
        self.ax.legend(fontsize=13)
        
        # включаем всплывающие подсказки для графика доходности ОФЗ
        self.cursor = mplcursors.cursor(oScatter, hover=True)
        self.cursor.connect('add', self.on_add)

        return self, sTitle

    def on_add(self,  sel):
        """ Настройка всплывающей подсказки.

        :param sel: экземпляр класса Selection
        :type sel: mplcursors._mplcursors.Selection

        """
        sName = self.lNames[sel.index]
        x, y = sel.target
        sel.annotation.set_multialignment("left")
        sel.annotation.set_text(f"облигация: {sName}\nдоходность: {y}")
