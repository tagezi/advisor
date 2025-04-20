#     This code is a part of program Advisor
#     Copyright (C) 2022 contributors Advisor
#     The full list is available at the link
#     https://github.com/tagezi/mli/blob/master/contributors.txt
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

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout

from advisor.ui.dialog_elements import ADialogApplyButtons, VComboBox, VLineEdit


class ASelectBondsDialog(ADialogApplyButtons):
    """ Creates abstract class that contain common elements for Dialogs of
        taxon."""

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(ASelectBondsDialog, self).__init__(oConnector, oParent)

        self.result = None
        self.oHLayoutTaxon = None
        self.oComboMin = None
        self.oComboMax = None
        self.sMin = ''
        self.sMax = ''

        self.init_UI()
        self.fill_combobox()
        self.connect_actions()

    def init_UI(self):
        """ initiating a dialog view """
        self.oComboMin = VComboBox('Минимальный период:', 50)
        self.oComboMax = VComboBox('Максимальный период', 50)

        oVLayoutPeriod = QVBoxLayout()
        oVLayoutPeriod.addLayout(self.oComboMin)
        oVLayoutPeriod.addLayout(self.oComboMax)

        self.oHLayoutTaxon = QHBoxLayout()
        self.oHLayoutTaxon.addLayout(oVLayoutPeriod)

    def connect_actions(self):
        """ Connects buttons with actions they should perform. """
        # (self.oComboMin.get_widget()).currentTextChanged.connect(
        #     self.onCurrentMainTaxonChanged)

    def clean_field(self):
        """ Clears all fields after use. """
        self.oComboMin.clear_list()
        self.oComboMax.clear_list()

    def create_period_list(self):
        """ Creates a list of taxon names for further use in dialog elements.

        :return: A list in form - (Taxon Rank) Taxon Name
        :type: list[str]
        """
        tRows = self.oConnector.get_period_list()

        return [str(tRow[0]) for tRow in tRows]

    def fill_combobox(self):
        """ Fills the fields with the drop-down list during the first
        initialization and after applying the Apply button."""
        lStatuses = self.create_period_list()
        self.oComboMin.set_combo_list(lStatuses)
        self.oComboMax.set_combo_list(lStatuses)

        self.oComboMin.set_text(lStatuses[0])
        self.oComboMax.set_text(lStatuses[-1])

    def onClickApply(self):
        self.sMin = self.oComboMin.get_text()
        self.sMax = self.oComboMax.get_text()

        if self.sMin > self.sMax:
            sTemp = self.sMin
            self.sMin = self.sMax
            self.sMax = sTemp

        self.clean_field()
        self.fill_combobox()

        self.result = [self.sMin, self.sMax]

    def GetValue(self):
        return self.result


class SelectBondsDialog(ASelectBondsDialog):
    """ Dialog window which adds information on new taxon. """

    def __init__(self, oConnector, oParent=None):
        """ Initiating a class. """
        super(SelectBondsDialog, self).__init__(oConnector, oParent)

    def init_UI(self):
        """ Creating a dialog window. """
        super().init_UI()
        self.setWindowTitle('Add new taxon to tree')
        self.setModal(True)

        oVLayout = QVBoxLayout()
        oVLayout.addLayout(self.oComboMin)
        oVLayout.addLayout(self.oComboMax)
        oVLayout.addLayout(self.oHLayoutTaxon)
        oVLayout.addLayout(self.oHLayoutButtons)
        self.setLayout(oVLayout)


if __name__ == '__main__':
    pass
