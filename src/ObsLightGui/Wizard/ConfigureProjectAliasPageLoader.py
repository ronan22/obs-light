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
Created on 21 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QRegExp
from PySide.QtGui import QLabel, QLineEdit, QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, uiFriendly

from WizardPageLoader import WizardPageLoader
import ConfigWizard

class ConfigureProjectAliasPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_configProjectAlias.ui")
        self.projectLabel = self.page.findChild(QLabel, u"projectLabel")
        self.targetLabel = self.page.findChild(QLabel, u"targetLabel")
        self.archLabel = self.page.findChild(QLabel, u"architectureLabel")
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"[^\\s:]+"))
        self.aliasLineEdit = self.page.findChild(QLineEdit, u"aliasLineEdit")
        self.aliasLineEdit.setValidator(noSpaceValidator)
        self.page.registerField(u"projectAlias*", self.aliasLineEdit)
        self.page.initializePage = self._initializePage
        self.page.validatePage = self._validatePage
        self.page.setCommitPage(True)

    def _initializePage(self):
        self.projectLabel.setText(self.getSelectedProject())
        self.targetLabel.setText(self.getSelectedTarget())
        self.archLabel.setText(self.getSelectedArch())

    def _validatePage(self):
        if not self.page.isComplete():
            return False
        alias = self.page.field(u"projectAlias")
        if self.manager.isALocalProject(alias):
            colorizeWidget(self.aliasLineEdit, u"red")
            return False

        self.waitWhile(self._addProject,
                       self.getSelectedServer(),
                       self.getSelectedProject(),
                       self.getSelectedTarget(),
                       self.getSelectedArch(),
                       alias)
        return True

    @uiFriendly()
    def _addProject(self, server, project, target, arch, alias):
        print server, project, target, arch, alias
        self.manager.addProject(server, project, target, arch, projectLocalName=alias)

    def getSelectedServer(self):
        return self.page.field(u"serverAlias")

    def getSelectedProject(self):
        chooseProjectPageIndex = ConfigWizard.ConfigWizard.pageIndex(u'ChooseProject')
        chooseProjectPage = self.page.wizard().page(chooseProjectPageIndex)
        project = chooseProjectPage.getSelectedProject()
        return project

    def getSelectedTarget(self):
        chooseTargetPageIndex = ConfigWizard.ConfigWizard.pageIndex(u'ChooseProjectTarget')
        chooseTargetPage = self.page.wizard().page(chooseTargetPageIndex)
        target = chooseTargetPage.getSelectedTarget()
        return target

    def getSelectedArch(self):
        chooseArchPageIndex = ConfigWizard.ConfigWizard.pageIndex(u'ChooseProjectArchitecture')
        chooseArchPage = self.page.wizard().page(chooseArchPageIndex)
        arch = chooseArchPage.getSelectedArch()
        return arch
