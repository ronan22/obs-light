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

from ChooseServerPage import ChooseServerPage
from ConfigureServerUrlPage import ConfigureServerUrlPage
from ConfigureServerAliasPage import ConfigureServerAliasPage
from ChooseProjectPage import ChooseProjectPage
from ChooseProjectTargetPage import ChooseProjectTargetPage
from ChooseProjectArchPage import ChooseProjectArchPage
from ConfigureProjectAliasPage import ConfigureProjectAliasPage
from ChoosePackagePage import ChoosePackagePage

class ConfigWizard(QWizard, ObsLightGuiObject):

    Pages = {}

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        QWizard.__init__(self, self.mainWindow)
        self.loadPages()

    def pageIndex(self, pageName):
        return self.Pages[pageName].index

    def loadPages(self):
        # TODO: put page name in each class as static member
        # and instantiate all theses classes from a list
        pageCounter = 0
        self.Pages[u'ChooseServer'] = ChooseServerPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ConfigureServerUrl'] = ConfigureServerUrlPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ConfigureServerAlias'] = ConfigureServerAliasPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ChooseProject'] = ChooseProjectPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ChooseProjectTarget'] = ChooseProjectTargetPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ChooseProjectArch'] = ChooseProjectArchPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ConfigureProjectAlias'] = ConfigureProjectAliasPage(self.gui, pageCounter)

        pageCounter += 1
        self.Pages[u'ChoosePackage'] = ChoosePackagePage(self.gui, pageCounter)

        for page in self.Pages.values():
            self.setPage(page.index, page)

    def getSelectedProject(self):
        return self.Pages[u'ChooseProject'].getSelectedProject()

    def getSelectedProjectAlias(self):
        return self.field(u"projectAlias")

    def getSelectedServerAlias(self):
        return self.field(u"serverAlias")

    def getSelectedTarget(self):
        return self.Pages[u'ChooseProjectTarget'].getSelectedTarget()

    def getSelectedArch(self):
        return self.Pages[u'ChooseProjectArch'].getSelectedArch()
