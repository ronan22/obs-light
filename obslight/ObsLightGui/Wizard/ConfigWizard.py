# -*- coding: utf8 -*-
#
# Copyright 2011-2012, Intel Inc.
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
import os

from PySide.QtGui import QPlainTextEdit, QWizard

from ObsLightGui.ObsLightGuiObject import ObsLightGuiObject

from ChooseLocalGbsOrOBSProjectPage import ChooseLocalGbsOrOBSProjectPage
from ChooseProjectTemplatePage import ChooseProjectTemplatePage
from ChooseProjectConfPage import ChooseProjectConfPage
from ChooseRepositoryTreePage import ChooseRepositoryTreePage
from ChooseRepositoryPage import ChooseRepositoryPage
from ChooseGbsArchPage import ChooseGbsArchPage
from ChooseManifestPage import ChooseManifestPage
from ConfigureGitPackagePage import  ConfigureGitPackagePage
from ConfigProjectGitAliasPage import ConfigProjectGitAliasPage

from ChooseServerPage import ChooseServerPage
from ConfigureServerUrlPage import ConfigureServerUrlPage
from ConfigureServerAliasPage import ConfigureServerAliasPage
from ChooseProjectPage import ChooseProjectPage
from ChooseLocalProjectPage import ChooseLocalProjectPage
from ChooseProjectTargetPage import ChooseProjectTargetPage
from ChooseProjectArchPage import ChooseProjectArchPage
from ConfigureProjectAliasPage import ConfigureProjectAliasPage
from ChooseNewOrExistingPackagePage import ChooseNewOrExistingPackagePage
from ConfigureNewPackagePage import ConfigureNewPackagePage
from ChoosePackagePage import ChoosePackagePage
from ChooseLocalPackagePage import ChooseLocalPackagePage

class ConfigWizard(QWizard, ObsLightGuiObject):

    Pages = {}

    def __init__(self, gui, parent=None):
        ObsLightGuiObject.__init__(self, gui)
        if parent is None:
            QWizard.__init__(self, self.mainWindow)
        else:
            QWizard.__init__(self, parent)
        self.setButtonText(QWizard.CommitButton, u"Validate >")
        # QPlainTextEdit is not a known field type so we have to register it
        self.setDefaultProperty(QPlainTextEdit.__name__, "plainText", "textChanged")
        self.loadPages()
        self.isModifyingServer = False
        self.__pageCounter = 0

    def pageIndex(self, pageName):
        return self.Pages[pageName].index

    def loadPages(self):
        self.__pageCounter = 0
        def addPage(name, aClass):
            self.Pages[name] = aClass(self.gui, self.__pageCounter)
            self.__pageCounter += 1

        addPage(u'ChooseLocalGbsOrOBSProject', ChooseLocalGbsOrOBSProjectPage)
        addPage(u'ChooseProjectTemplate', ChooseProjectTemplatePage)
        addPage(u'ChooseProjectConf', ChooseProjectConfPage)
        addPage(u'ChooseRepositoryTree', ChooseRepositoryTreePage)
        addPage(u'ChooseRepository', ChooseRepositoryPage)
        addPage(u'ChooseGbsArch', ChooseGbsArchPage)
        addPage(u'ChooseManifestPage', ChooseManifestPage)
        addPage(u'ConfigProjectGitAliasPage', ConfigProjectGitAliasPage)
        addPage(u'ChooseServer', ChooseServerPage)
        addPage(u'ConfigureServerUrl', ConfigureServerUrlPage)
        addPage(u'ConfigureServerAlias', ConfigureServerAliasPage)
        addPage(u'ChooseProject', ChooseProjectPage)
        addPage(u'ChooseProjectTarget', ChooseProjectTargetPage)
        addPage(u'ChooseProjectArch', ChooseProjectArchPage)
        addPage(u'ConfigureProjectAlias', ConfigureProjectAliasPage)
        addPage(u'ChooseNewOrExistingPackage', ChooseNewOrExistingPackagePage)
        addPage(u'ConfigureNewPackage', ConfigureNewPackagePage)
        addPage(u'ChoosePackage', ChoosePackagePage)
        addPage(u'ChooseLocalProject', ChooseLocalProjectPage)
        addPage(u'ChooseLocalPackagePage', ChooseLocalPackagePage)
        addPage(u'ConfigureGitPackagePage', ConfigureGitPackagePage)

        for page in self.Pages.values():
            self.setPage(page.index, page)

    def isLocalProject(self):
        return self.Pages[u'ChooseLocalGbsOrOBSProject'].isLocalProject()

    def getSelectedProject(self):
        return self.Pages[u'ChooseProject'].getSelectedProject()

    def getSelectedLocalProject(self):
        return self.Pages[u'ChooseLocalProject'].getSelectedLocalProject()

    def getSelectedProjectAlias(self):
        return  self.Pages[u'ConfigureProjectAlias'].getSelectedProjectAlias()

    def getSelectedServerAlias(self):
        return self.Pages[u'ConfigureServerAlias'].getSelectedServerAlias()

    def getSelectedTarget(self):
        return self.Pages[u'ChooseProjectTarget'].getSelectedTarget()

    def getSelectedArch(self):
        return self.Pages[u'ChooseProjectArch'].getSelectedArch()

    def getProjectTemplatePath(self, fullPath=True):

        if self.Pages[u'ChooseProjectTemplate'].isAddNewLocalProject():
            res = self.Pages[u'ChooseProjectConf'].getSelectedProjectConf()
        else:
            res = self.Pages[u'ChooseProjectTemplate'].getSelectedProjectConf()

        if res is not None and fullPath:
            return res
        else:
            return os.path.basename(res)

#    def getCreateChrootOption(self):
#        return self.field(u'CreateChroot')

    def skipToPackageSelection(self, projectAlias):
        self.setField(u"projectAlias", projectAlias)
        self.setStartId(self.Pages[u'ChooseNewOrExistingPackage'].index)

    def skipToPackageCreation(self, projectAlias):
        self.setField(u"projectAlias", projectAlias)
        self.setStartId(self.Pages[u'ConfigureNewPackage'].index)

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
        self.isModifyingServer = prefilledValues.has_key('serverAlias')

    def getProjectConfPath(self):
        return self.Pages[u'ChooseProjectConf'].getSelectedProjectConf()

    def getGbsAddedRepo(self):
        return self.Pages[u'ChooseRepository'].getAddedRepo()

    def getSelectedGbsArch(self):
        return self.Pages[u'ChooseGbsArch'].getArch()

    def getSelectedGbsProject(self):
        return self.getProjectTemplatePath(False)

    def getInitProjectRepo(self):
        return self.Pages[u'ChooseRepositoryTree'].getInitProjectRepo()

    def autoAddProjectRepo(self):
        return self.Pages[u'ChooseRepository'].autoAddProjectRepo()
