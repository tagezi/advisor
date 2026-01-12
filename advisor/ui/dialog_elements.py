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

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QDialog, QHBoxLayout, QVBoxLayout, \
    QLabel, QLineEdit, QPushButton, QTextEdit

from advisor.ui.file_dialogs import OpenFileDialog


class ADialogApplyButtons(QDialog):
    """An abstract class that creates a block of Apply, OK, Cancel buttons and
    reserves action methods for them."""

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(ADialogApplyButtons, self).__init__(oParent)
        self.oHLayoutButtons = None
        self.oButtonApply = None
        self.oButtonOk = None
        self.oButtonCancel = None
        self.oConnector = oConnector
        self.init_UI_button_block()
        self.connect_actions_button()

    def init_UI_button_block(self):
        """ Creates a block of buttons for further use in child dialog classes.
        """
        self.oHLayoutButtons = QHBoxLayout()
        self.oButtonApply = QPushButton('Apply', self)
        self.oButtonApply.setFixedWidth(80)
        self.oButtonOk = QPushButton('Ok', self)
        self.oButtonOk.setFixedWidth(80)
        self.oButtonCancel = QPushButton('Cancel', self)
        self.oButtonCancel.setFixedWidth(80)

        self.oHLayoutButtons.addWidget(self.oButtonApply,
                                       alignment=Qt.AlignmentFlag.AlignRight)
        self.oHLayoutButtons.addWidget(self.oButtonOk)
        self.oHLayoutButtons.addWidget(self.oButtonCancel)

    def connect_actions_button(self):
        """ The method of linking signals and button slots. """
        self.oButtonApply.clicked.connect(self.onClickApply)
        self.oButtonOk.clicked.connect(self.onClickOk)
        self.oButtonCancel.clicked.connect(self.onCancel)

    def onCancel(self):
        """ The method closes the dialog without saving the data. """
        self.close()

    def onClickApply(self):
        """ Reserves the Apply dialog button method for future use. """
        pass

    def onClickOk(self):
        """ The method saves the data and closes the dialog In order for the
        data to be saved, you must override the method onClickApply."""
        self.onClickApply()
        self.close()


class AOneButton(QDialog):
    """An abstract class that creates a block of Apply, OK, Cancel buttons and
    reserves action methods for them."""

    def __init__(self, oParent=None):
        """ Initiating a class. """
        super(AOneButton, self).__init__(oParent)


class AComboBox:
    """ Это абстрактный сырой класс, который задаёт только поведение элемента
    combobox и пренадлежащих ему в форме элементов"""
    def __init__(self, sLabel='', iSize=300, oParent=None):
        super().__init__(oParent)
        self.oLabel = QLabel()
        oLineEdit = QLineEdit()
        self.oComboBox = QComboBox()
        self.oComboBox.setLineEdit(oLineEdit)
        self.set_combo_width(iSize)
        self.set_label(sLabel)

    def clear_list(self):
        """ Clean up a list of QComboBox.

        :return: None
        """
        self.oComboBox.clear()

    def get_text(self):
        """ The function gets text from QLineEdit of QComboBox.

        :return: Selected text from QComboBox.
        :rtype: str
        """
        return self.oComboBox.currentText()

    def set_text(self, sString=''):
        """ Set up text into QLineEdit of the block.

        :param sString: A string which display by default in QLineEdit.
        :type sString: str
        :return: None
        """
        oLineEdit = self.oComboBox.lineEdit()
        oLineEdit.setText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        self.oLabel.setText(sString)

    def set_combo_list(self, lItems=None):
        """ Set up a list of QComboBox.

        :param lItems: A list of elements for QComboBox.
        :type lItems: list
        :return: None
        """
        self.oComboBox.addItems(lItems)

    def set_combo_width(self, iSize=300):
        """ Set up width of QComboBox.

        :param iSize: A number which point to width of QComboBox.
        :type iSize: int
        :return: None
        """
        self.oComboBox.setFixedWidth(iSize)


class HComboBox(AComboBox, QHBoxLayout):
    """ Creates a block that units QLabel, QComboBox and QLineEdit. Also, it
    creates methods that change parameters inside block without direct access.
    """
    def __init__(self, sLabel='', iSize=300, oParent=None):
        super().__init__(sLabel, iSize, oParent)
        self.addWidget(self.oLabel)
        self.addWidget(self.oComboBox)

    def get_widget(self):
        return self.itemAt(1).widget()


class VComboBox(AComboBox, QVBoxLayout):
    """ Creates a block that units QLabel, QComboBox and QLineEdit. Also, it
    creates methods that change parameters inside block without direct access.
    """
    def __init__(self, sLabel='', iSize=300, oParent=None):
        super().__init__(sLabel, iSize, oParent)
        self.oComboBox.setStyleSheet('QComboBox {margin-left:5px}')
        self.addWidget(self.oLabel)
        self.addWidget(self.oComboBox)

    def get_widget(self):
        return self.itemAt(1).widget()


class ALineEdit:
    """ Creates a block that units QLabel and QLineEdit. Also, it creates
    methods that change parameters inside block without direct access.
    """

    def __init__(self, sLabel='', iSize=300, oParent=None):
        super().__init__(oParent)
        self.oLabel = QLabel()
        self.oLineEdit = QLineEdit()
        self.oLineEdit.setStyleSheet('QLineEdit {margin-top:5px}')
        self.set_line_width(iSize)
        self.set_label(sLabel)

    def get_text(self):
        """ The function gets text from QLineEdit.

        :return: Selected text from QLineEdit.
        :rtype: str
        """
        return self.oLineEdit.text().strip()

    def set_text(self, sString=''):
        """ Set up text into QLineEdit of the block.

        :param sString: A string which display by default in QLineEdit.
        :type sString: str
        :return: None
        """
        self.oLineEdit.setText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        self.oLabel.setText(sString)

    def set_line_width(self, iSize=300):
        """ Set up width of QLineEdit.

        :param iSize: A number which point to width of QComboBox.
        :type iSize: int
        :return: None
        """
        self.oLineEdit.setFixedWidth(iSize)


class HLineEdit(ALineEdit, QHBoxLayout):
    """ Creates a block that units QLabel and QLineEdit. Also, it creates
    methods that change parameters inside block without direct access.
    """

    def __init__(self, sLabel='', iSize=300, oParent=None):
        super(HLineEdit, self).__init__(sLabel, iSize, oParent)
        self.addWidget(self.oLabel)
        self.addWidget(self.oLineEdit)


class HLineEditButton(ALineEdit, QHBoxLayout):
    """ Creates a block that units QLabel, QComboBox and QLineEdit. Also, it
    creates methods that change parameters inside block without direct access.
    """

    def __init__(self, sLabel='', iSize=300, oParent=None):
        super(HLineEditButton, self).__init__(sLabel, iSize, oParent)
        self.lFileName = None
        self.addWidget(self.oLabel)
        self.addWidget(self.oLineEdit)
        self.oButton = QPushButton('...', oParent)
        self.oButton.setGeometry(3, 5, 30, 20)
        self.addWidget(self.oButton)
        self.connect_actions_button()

    def connect_actions_button(self):
        """ The method of linking signals and button slots. """
        self.oButton.clicked.connect(self.onSelect())

    def onClick(self):
        """ Reserves the Apply dialog button method for future use. """

        ...

    def onSelect(self):
        """

        :return:
        """
        dParameter = {'name': 'Selecting directory',
                      'filter': 'CSV (*.csv)'}
        oFileDialog = OpenFileDialog(self, dParameter)
        lFileName = oFileDialog.exec()
        if lFileName:
            print(lFileName)
            sFileName = str(lFileName[0])

        self.oLineEdit.setText(sFileName)


class VLineEdit(ALineEdit, QVBoxLayout):
    """ Creates a block that units QLabel and QLineEdit. Also, it creates
    methods that change parameters inside block without direct access.
    """

    def __init__(self, sLabel='', iSize=300, oParent=None):
        super(VLineEdit, self).__init__(sLabel, iSize, oParent)
        self.addWidget(self.oLabel)
        self.addWidget(self.oLineEdit)


class VTextEdit(QVBoxLayout):
    """ Creates a block that units QLabel and QTextEdit. Also, it creates
    methods that change parameters inside block without direct access.
    """

    def __init__(self, sLabel='', iSize=300, iHeight=120, oParent=None):
        super(QVBoxLayout, self).__init__(oParent)
        oLabel = QLabel()
        oTextEdit = QTextEdit()
        self.addWidget(oLabel)
        self.addWidget(oTextEdit)
        self.set_textedit_size()
        self.set_label(sLabel)
        self.set_textedit_size(iSize, iHeight)

    def clear_text(self):
        """ The function clears QTextEdit failed. """
        oTextEdit = self.itemAt(1).widget()
        oTextEdit.clear()

    def get_text(self):
        """ The function gets text from QLineEdit of QTextEdit.

        :return: Selected text from QTextEdit.
        :rtype: str
        """
        oTextEdit = self.itemAt(1).widget()
        return oTextEdit.toPlainText()

    def set_text(self, sString=''):
        """ Set up text into QTextEdit of the block.

        :param sString: A string which display by default in QTextEdit.
        :type sString: str
        :return: None
        """
        oTextEdit = self.itemAt(1).widget()
        oTextEdit.insertPlainText(sString)

    def set_label(self, sString=''):
        """ Set up text into Label of block.

        :param sString: A string which needs to display as Label in the block.
        :type sString: str
        :return: None
        """
        oLabel = self.itemAt(0).widget()
        oLabel.setText(sString)

    def set_textedit_size(self, iWidth=300, iHeight=120):
        """ Set up width of QTextEdit.

        :param iWidth: A number which point to width of QTextEdit.
        :type iWidth: int
        :param iHeight: A number which point to height of QTextEdit.
        :type iHeight: int
        :return: None
        """
        oTextEdit = self.itemAt(1).widget()
        oTextEdit.setFixedSize(iWidth, iHeight)


if __name__ == '__main__':
    pass
