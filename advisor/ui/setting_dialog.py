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

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit

from advisor.ui.dialog_elements import ADialogApplyButtons
from advisor.ui.file_dialogs import OpenFileDialog
from advisor.lib.config import ConfigProgram


class SettingDialog(ADialogApplyButtons):
    def __init__(self, oConnector, sPathApp, oParent=None):
        super(SettingDialog, self).__init__(oParent)
        self.oButtonOpenFile = None
        self.oTextFiled = None
        self.oConnector = oConnector
        self.oConfigProgram = ConfigProgram(sPathApp)
        self.init_UI()
        self.connect_actions()

    def init_UI(self):
        self.setWindowTitle('Setting')
        self.setModal(True)
        self.oButtonOpenFile = QPushButton('...', self)
        sFileNameDB = self.oConfigProgram.get_config_value('DB', 'db_path')

        oVLayout = QVBoxLayout()
        oHLayoutFiledPath = QHBoxLayout()
        self.oTextFiled = QLineEdit(sFileNameDB)
        oHLayoutFiledPath.addWidget(self.oTextFiled)
        oHLayoutFiledPath.addWidget(self.oButtonOpenFile)
        oVLayout.addLayout(oHLayoutFiledPath)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)

    def connect_actions(self):
        self.oButtonOpenFile.clicked.connect(self.onClickOpenFile)

    def onClickOpenFile(self):
        dParameter = {'name': 'Selecting directory',
                      'filter': 'DB file (*.db)'}
        oFileDialog = OpenFileDialog(self, dParameter)
        lFileName = oFileDialog.exec()
        sFileName = ''
        if lFileName:
            sFileName = str(lFileName[0])

        self.oTextFiled.setText(sFileName)


if __name__ == '__main__':
    pass
