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

from PySide.QtGui import QWizard

from ObsLightGui.ObsLightGuiObject import ObsLightGuiObject
from ChooseServerWizardPage import ChooseServerWizardPageLoader
from ConfigureServerUrlPageLoader import ConfigureServerUrlPageLoader

class ConfigWizard(ObsLightGuiObject):

    Pages = ['ChooseServer',
             'ConfigureServerUrl',
             'ConfigureServerCredentials',
             'ConfigureServerAlias',
             'ChooseProject',
             'ChooseProjectTarget',
             'ChooseProjectArchitecture']

#    ChooseServerPage = 0
#    ConfigureServerUrlsPage = ChooseServerPage + 1
#    ConfigureServerCredentialsPage = ConfigureServerUrlsPage + 1
#    ConfigureServerAliasPage = ConfigureServerCredentialsPage + 1
#    ChooseProjectPage = ConfigureServerAliasPage + 1

    wizard = None

    chooseServerWP = None
    configServerUrlWP = None
    configServerCredentialsWP = None
    configServerAliasWP = None

    oldNextId = None

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        self.wizard = QWizard(self.mainWindow)
        self.loadPages()
        self.oldNextId = self.wizard.nextId
        def newNextId():
            nextId = self.wizard.currentPage().nextId()
            return nextId
        self.wizard.nextId = newNextId

    @staticmethod
    def pageIndex(pageName):
        return ConfigWizard.Pages.index(pageName)

    def loadPage(self, pageName):
        page = self.gui.loadWindow(pageName)
        return page

    def loadPages(self):

        pageLoader = ChooseServerWizardPageLoader(self.gui)
        index = self.pageIndex('ChooseServer')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ConfigureServerUrlPageLoader(self.gui)
        index = self.pageIndex('ConfigureServerUrl')
        self.wizard.setPage(index, pageLoader.page)

        pageCounter = 1
        for pageName in [u"wizard_configServerCredentials.ui",
                         u"wizard_configServerAlias.ui",
                         u"wizard_chooseProject.ui",
                         u"wizard_chooseTarget.ui",
                         u"wizard_chooseArchitecture.ui"]:
            pageCounter += 1
            self.wizard.setPage(pageCounter, self.loadPage(pageName))

    def show(self):
        return self.wizard.show()
