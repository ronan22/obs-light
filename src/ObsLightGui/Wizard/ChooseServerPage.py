# -*- coding: utf8 -*-
#
# Copyright 2011, Intel Inc.
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
Created on 19 déc. 2011

@author: Florent Vennetier
'''

from WizardPageWrapper import ObsLightWizardPage

class ChooseServerPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseServer.ui")
        self.registerField(u"addNewServer", self.ui_WizardPage.addNewServerButton)
        self.ui_WizardPage.addNewServerButton.toggled.connect(self.__completeChanged)
        self.registerField(u"serverList", self.ui_WizardPage.serverListWidget)
        self.ui_WizardPage.serverListWidget.currentRowChanged.connect(self.__completeChanged)

    def initializePage(self):
        serverList = self.manager.getObsServerList()
        self.ui_WizardPage.serverListWidget.clear()
        self.ui_WizardPage.serverListWidget.addItems(serverList)

    def isAddingNewServer(self):
        return self.field(u"addNewServer")

    def serverRow(self):
        return self.field(u"serverList")

    def isComplete(self):
        return self.isAddingNewServer() or (self.serverRow() >= 0)

    def validatePage(self):
        if not self.isAddingNewServer():
            self.setField(u"serverAlias",
                          self.ui_WizardPage.serverListWidget.currentItem().text())
        return self.isComplete()

    def nextId(self):
        if self.isAddingNewServer():
            return self.wizard().pageIndex(u"ConfigureServerUrl")
        else:
            return self.wizard().pageIndex(u"ChooseProject")

    def __completeChanged(self, _row):
        self.completeChanged.emit()
