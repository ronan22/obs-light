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

from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, PROJECT_ALIAS_REGEXP

from WizardPageWrapper import ObsLightWizardPage

class ConfigureProjectAliasPage(ObsLightWizardPage):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configProjectAlias.ui")
        noSpaceValidator = QRegExpValidator(PROJECT_ALIAS_REGEXP, self)
        self.ui_WizardPage.aliasLineEdit.setValidator(noSpaceValidator)
        self.registerField(u"projectAlias*", self.ui_WizardPage.aliasLineEdit)
        self.registerField(u"CreateChroot", self.ui_WizardPage.createChrootCheckBox)
        self.setCommitPage(True)

    def initializePage(self):
        prj = self.wizard().getSelectedProject()
        target = self.wizard().getSelectedTarget()
        arch = self.wizard().getSelectedArch()
        suggestedName = "%s_%s_%s" % (prj.replace(":", "_"), target, arch)
        self.ui_WizardPage.projectLabel.setText(prj)
        self.ui_WizardPage.targetLabel.setText(target)
        self.ui_WizardPage.architectureLabel.setText(arch)
        self.ui_WizardPage.aliasLineEdit.setText(suggestedName)

    def getSelectedProjectAlias(self):
        return  self.field(u"projectAlias")

    def validatePage(self):
        if not self.isComplete():
            return False
        alias = self.field(u"projectAlias")
        if self.manager.isALocalProject(alias):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

        retVal = self.callWithInfiniteProgress(self.manager.addProject,
                                               u"Adding project %s..." % alias,
                                               self.wizard().getSelectedServerAlias(),
                                               self.wizard().getSelectedProject(),
                                               self.wizard().getSelectedTarget(),
                                               self.wizard().getSelectedArch(),
                                               projectLocalName=alias)
        # If we get an exception, None is returned
        if retVal is None:
            return False
        self.gui.refresh()
        self.gui.setCurrentProject(alias)
        if self.field(u"CreateChroot"):
            self.callWithInfiniteProgress(self.manager.createChRoot,
                                          u"Creating chroot...",
                                          alias)
        return True
