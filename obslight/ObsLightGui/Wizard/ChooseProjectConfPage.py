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

class ChooseProjectConfPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProjectConf.ui")

        self.registerField(u"addNewConf", self.ui_WizardPage.addNewConfButton)
        self.ui_WizardPage.addNewConfButton.toggled.connect(self.__completeChanged)
        self.registerField(u"LocalConfList", self.ui_WizardPage.LocalConfListWidget)
        self.ui_WizardPage.LocalConfListWidget.currentRowChanged.connect(self.__completeChanged)

    def initializePage(self):
        pass
#        serverList = self.manager.getObsServerList()
#        serverList.sort()
#        self.ui_WizardPage.LocalProjectListWidget.clear()
#        self.ui_WizardPage.LocalProjectListWidget.addItems(serverList)
#        if len(serverList) > 0:
#            self.ui_WizardPage.chooseServerButton.setChecked(True)

    def isAddNewLocalProject(self):
        return self.field(u"addNewConf")

    def LocalProjectRow(self):
        return self.field(u"LocalConfList")

    def isComplete(self):
        return self.isAddNewLocalProject() or (self.LocalProjectRow() >= 0)

    def validatePage(self):
        if not self.isAddNewLocalProject():
            self.setField(u"serverAlias",
                          self.ui_WizardPage.LocalConfListWidget.currentItem().text())
        return self.isComplete()

    def nextId(self):
        return self.wizard().pageIndex(u'ChooseRepository')

    def __completeChanged(self, _row):
        self.completeChanged.emit()

