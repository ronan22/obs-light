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

class ChooseProjectTemplatePage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProjectTemplate.ui")

        self.registerField(u"addNewLocalProject", self.ui_WizardPage.addNewLocalProjectButton)
        self.ui_WizardPage.addNewLocalProjectButton.toggled.connect(self.__completeChanged)
        self.registerField(u"LocalProjectList", self.ui_WizardPage.LocalProjectListWidget)
        self.ui_WizardPage.LocalProjectListWidget.currentRowChanged.connect(self.__completeChanged)

    def initializePage(self):
        pass
#        serverList = self.manager.getObsServerList()
#        serverList.sort()
#        self.ui_WizardPage.LocalProjectListWidget.clear()
#        self.ui_WizardPage.LocalProjectListWidget.addItems(serverList)
#        if len(serverList) > 0:
#            self.ui_WizardPage.chooseServerButton.setChecked(True)

    def isAddNewLocalProject(self):
        return self.field(u"addNewLocalProject")

    def LocalProjectRow(self):
        return self.field(u"LocalProjectList")

    def isComplete(self):
        return self.isAddNewLocalProject() or (self.LocalProjectRow() >= 0)

    def validatePage(self):
        if not self.isAddNewLocalProject():
            self.setField(u"serverAlias",
                          self.ui_WizardPage.serverListWidget.currentItem().text())
        return self.isComplete()

    def nextId(self):
        if self.isAddNewLocalProject():
            return self.wizard().pageIndex(u"ChooseProjectConf")
        else:
            return self.wizard().pageIndex(u"ChooseProject")

    def __completeChanged(self, _row):
        self.completeChanged.emit()
