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


from PyQt6.QtWidgets import QFileDialog


class OpenFileDialog(QFileDialog):
    def __init__(self, oParent=None, dParameter={}):
        super().__init__(oParent)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self.FileMode(QFileDialog.FileMode.ExistingFiles)
        self.setWindowTitle(dParameter.get('name'))
        self.setNameFilter(dParameter.get('filter'))

    def exec(self):
        fFileName = []
        if self.exec():
            fFileName = self.selectedFiles()
        if fFileName:
            return fFileName
        return


class OpenDirDialog(QFileDialog):
    def __init__(self, oParent=None, sNameDialog='Dialog'):
        super().__init__(oParent)
        self.sNameDialog = sNameDialog

        self.set_dialog()

    def set_dialog(self):
        self.getExistingDirectory(self, self.sNameDialog)

    def exec(self):
        fFileName = []
        if self.exec():
            fFileName = self.selectedFiles()
        if fFileName:
            return fFileName
        return


if __name__ == '__main__':
    pass
