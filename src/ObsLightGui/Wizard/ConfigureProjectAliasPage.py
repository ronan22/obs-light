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
        self.registerField(u"CreateChroot", self.ui_WizardPage.createChrootCheckBox)
        self.setCommitPage(True)

    def initializePage(self):
        self.ui_WizardPage.projectLabel.setText(self.wizard().getSelectedProject())
        self.ui_WizardPage.targetLabel.setText(self.wizard().getSelectedTarget())
        self.ui_WizardPage.architectureLabel.setText(self.wizard().getSelectedArch())

    def validatePage(self):
        if not self.isComplete():
            return False
        alias = self.field(u"projectAlias")
        if self.manager.isALocalProject(alias):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

        self.setBusyCursor(self._addProject,
                           self.wizard().getSelectedServerAlias(),
                           self.wizard().getSelectedProject(),
                           self.wizard().getSelectedTarget(),
                           self.wizard().getSelectedArch(),
                           alias)
        self.gui.refresh()
        if self.field(u"CreateChroot"):
            self.setBusyCursor(self._createChroot, alias)
        return True

    @uiFriendly()
    def _addProject(self, server, project, target, arch, alias):
        self.manager.addProject(server, project, target, arch, projectLocalName=alias)

    @uiFriendly()
    def _createChroot(self, alias):
        self.manager.createChRoot(alias)
