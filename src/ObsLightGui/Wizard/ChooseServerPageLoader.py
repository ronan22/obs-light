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

from PySide.QtGui import QListWidget, QRadioButton

from WizardPageLoader import WizardPageLoader
import ConfigWizard

class ChooseServerPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_chooseServer.ui", False)

        addServerButton = self.page.findChild(QRadioButton,
                                              u"addNewServerButton")
        self.page.registerField(u"addNewServer", addServerButton)
        addServerButton.toggled.connect(self.__completeChanged)
        self.serverListWidget = self.page.findChild(QListWidget,
                                                    u"serverListWidget")
        self.page.registerField(u"serverList", self.serverListWidget)
        self.serverListWidget.currentRowChanged.connect(self.__completeChanged)

        self.page.initializePage = self.__initializePage
        self.page.isComplete = self.__isComplete
        self.page.validatePage = self.__validatePage
        self.page.nextId = self.__nextId

    def addNewServer(self):
        return self.page.field(u"addNewServer")

    def serverRow(self):
        return self.page.field(u"serverList")

    def __completeChanged(self, _row):
        self.page.completeChanged.emit()

    def __initializePage(self):
        serverList = self.manager.getObsServerList()
        self.serverListWidget.clear()
        self.serverListWidget.addItems(serverList)

    def __isComplete(self):
        return self.addNewServer() or (self.serverRow() >= 0)

    def __validatePage(self):
        if not self.addNewServer():
            self.page.setField(u"serverAlias", self.serverListWidget.currentItem().text())
        return self.__isComplete()

    def __nextId(self):
        if self.addNewServer():
            return ConfigWizard.ConfigWizard.pageIndex(u"ConfigureServerUrl")
        else:
            return ConfigWizard.ConfigWizard.pageIndex(u"ChooseProject")
