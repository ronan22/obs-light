# -*- coding: utf8 -*-
#
# Copyright 2012, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 19 sept. 2012

@author: Ronan Le Martret
'''

from WizardPageWrapper import ObsLightWizardPage

class ChooseGbsArchPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseGbsArch.ui")

        self.ui_WizardPage.LocalTargetListcomboBox.currentIndexChanged.connect(self.on_LocalTargetListcomboBox)

        self._archList = ["i586"]
        self._indexComboBox = 0


    def on_LocalTargetListcomboBox(self):
        self._indexComboBox = self.ui_WizardPage.LocalTargetListcomboBox.currentIndex ()

    def initializePage(self):
        self.ui_WizardPage.LocalTargetListcomboBox.clear()
        self._archList = self.manager.getDefaultGbsArch()
        self.ui_WizardPage.LocalTargetListcomboBox.addItems(self._archList)
        if self._indexComboBox < len(self._archList):
            self.ui_WizardPage.LocalTargetListcomboBox.setCurrentIndex (self._indexComboBox)
        else:
            self._indexComboBox = 0

    def nextId(self):
        return self.wizard().pageIndex(u'ConfigProjectGitAliasPage')


    def getArch(self):
        return self._archList[self._indexComboBox]
