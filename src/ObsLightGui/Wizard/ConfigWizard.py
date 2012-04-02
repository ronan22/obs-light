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

    def __init__(self, gui, parent=None):
        ObsLightGuiObject.__init__(self, gui)
        if parent is None:
            QWizard.__init__(self, self.mainWindow)
        else:
            QWizard.__init__(self, parent)
        self.setButtonText(QWizard.CommitButton, u"Validate >")
        self.loadPages()

    def pageIndex(self, pageName):
        return self.Pages[pageName].index

    def loadPages(self):
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

    def getCreateChrootOption(self):
        return self.field(u'CreateChroot')

    def skipToPackageSelection(self, projectAlias):
        self.setField(u"projectAlias", projectAlias)
        self.setStartId(self.Pages[u'ChoosePackage'].index)

    def skipToServerCreation(self, **prefilledValues):
        """
        Skip to server creation page. `prefilledValues` allow to specify
        already known server configuration values. Possible keys
        for `prefilledValues`: "webUrl", "apiUrl", "repoUrl", "username",
        "password", "serverAlias".
        """
        self.setStartId(self.Pages[u'ConfigureServerUrl'].index)
        for key, value in prefilledValues.iteritems():
            self.setField(key, value)
