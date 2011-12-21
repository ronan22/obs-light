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

from ChooseServerWizardPageLoader import ChooseServerWizardPageLoader
from ConfigureServerUrlPageLoader import ConfigureServerUrlPageLoader
from ConfigureServerAliasPageLoader import ConfigureServerAliasPageLoader
from ChooseProjectWizardPageLoader import ChooseProjectWizardPageLoader
from ChooseProjectTargetWizardPageLoader import ChooseProjectTargetWizardPageLoader
from ChooseProjectArchWizardPageLoader import ChooseProjectArchWizardPageLoader

class ConfigWizard(ObsLightGuiObject):

    # TODO: merge _pageLoaders and Pages
    Pages = [u'ChooseServer',
             u'ConfigureServerUrl',
             u'ConfigureServerAlias',
             u'ChooseProject',
             u'ChooseProjectTarget',
             u'ChooseProjectArchitecture']
    _pageLoaders = {}
    wizard = None

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        self.wizard = QWizard(self.mainWindow)
        self.loadPages()

    @staticmethod
    def pageIndex(pageName):
        return ConfigWizard.Pages.index(pageName)

    def loadPages(self):
        pageLoader = ChooseServerWizardPageLoader(self.gui)
        self._pageLoaders[u'ChooseServer'] = pageLoader
        index = self.pageIndex(u'ChooseServer')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ConfigureServerUrlPageLoader(self.gui)
        self._pageLoaders[u'ConfigureServerUrl'] = pageLoader
        index = self.pageIndex(u'ConfigureServerUrl')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ConfigureServerAliasPageLoader(self.gui)
        self._pageLoaders[u'ConfigureServerAlias'] = pageLoader
        index = self.pageIndex(u'ConfigureServerAlias')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ChooseProjectWizardPageLoader(self.gui)
        self._pageLoaders[u'ChooseProject'] = pageLoader
        index = self.pageIndex(u'ChooseProject')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ChooseProjectTargetWizardPageLoader(self.gui)
        self._pageLoaders[u'ChooseProjectTarget'] = pageLoader
        index = self.pageIndex(u'ChooseProjectTarget')
        self.wizard.setPage(index, pageLoader.page)

        pageLoader = ChooseProjectArchWizardPageLoader(self.gui)
        self._pageLoaders[u'ChooseProjectArchitecture'] = pageLoader
        index = self.pageIndex(u'ChooseProjectArchitecture')
        self.wizard.setPage(index, pageLoader.page)

    def show(self):
        return self.wizard.show()
