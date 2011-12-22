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
from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, uiFriendly

from WizardPageWrapper import ObsLightWizardPage

class ConfigureProjectAliasPage(ObsLightWizardPage):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configProjectAlias.ui")
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"[^\\s:]+"))
        self.ui_WizardPage.aliasLineEdit.setValidator(noSpaceValidator)
        self.registerField(u"projectAlias*", self.ui_WizardPage.aliasLineEdit)
        self.setCommitPage(True)

    def initializePage(self):
        self.ui_WizardPage.projectLabel.setText(self.getSelectedProject())
        self.ui_WizardPage.targetLabel.setText(self.getSelectedTarget())
        self.ui_WizardPage.architectureLabel.setText(self.getSelectedArch())

    def validatePage(self):
        if not self.isComplete():
            return False
        alias = self.field(u"projectAlias")
        if self.manager.isALocalProject(alias):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

        self.setBusyCursor(self._addProject,
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

    # TODO: move to ConfigWizard
    def getSelectedServer(self):
        return self.field(u"serverAlias")

    # TODO: move to ConfigWizard
    def getSelectedProject(self):
        chooseProjectPageIndex = self.wizard().pageIndex(u'ChooseProject')
        chooseProjectPage = self.wizard().page(chooseProjectPageIndex)
        project = chooseProjectPage.getSelectedProject()
        return project

    # TODO: move to ConfigWizard
    def getSelectedTarget(self):
        chooseTargetPageIndex = self.wizard().pageIndex(u'ChooseProjectTarget')
        chooseTargetPage = self.wizard().page(chooseTargetPageIndex)
        target = chooseTargetPage.getSelectedTarget()
        return target

    # TODO: move to ConfigWizard
    def getSelectedArch(self):
        chooseArchPageIndex = self.wizard().pageIndex(u'ChooseProjectArch')
        chooseArchPage = self.wizard().page(chooseArchPageIndex)
        arch = chooseArchPage.getSelectedArch()
        return arch
