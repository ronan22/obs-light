# -*- coding: utf8 -*-
#
# Copyright 2012, Intel Inc.
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
Created on 19 sept. 2012

@author: Ronan Le Martret
'''

import os

from WizardPageWrapper import ObsLightWizardPage

from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, PROJECT_ALIAS_REGEXP

class ConfigProjectGitAliasPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configProjectGitAlias.ui")


        noSpaceValidator = QRegExpValidator(PROJECT_ALIAS_REGEXP, self)
        self.ui_WizardPage.aliasLineEdit.setValidator(noSpaceValidator)
        self.registerField(u"projectGbsAlias*", self.ui_WizardPage.aliasLineEdit)
        self.registerField(u"CreateGbsChroot", self.ui_WizardPage.createGbsChrootCheckBox)
        self.ui_WizardPage.createGbsChrootCheckBox.setChecked(True)

        self.setCommitPage(True)

    def initializePage(self):
        arch = self.wizard().getSelectedGbsArch()
        prj = os.path.basename(self.wizard().getProjectConfPath())

        self.ui_WizardPage.architectureLabel.setText(arch)
        suggestedName = "%s_%s" % (prj.replace(":", "_").replace(".conf", ""), arch)
        self.ui_WizardPage.aliasLineEdit.setText(suggestedName)

    def validatePage(self):
        if not self.isComplete():
            return False

        alias = self.ui_WizardPage.aliasLineEdit.text()

        if self.manager.isALocalProject(alias):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

        self.setField(u"projectAlias", alias)
        retVal = self.callWithInfiniteProgress(self.manager.addGbsProject,
                                               u"Adding project %s..." % alias,
                                               self.wizard().getProjectConfPath(),
                                               self.wizard().getGbsAddedRepo(),
                                               self.wizard().getSelectedGbsArch(),
                                               alias,
                                               self.wizard().autoAddProjectRepo())
        # If we get an exception, None is returned
        if retVal is None:
            return False
        self.gui.refresh()
        self.gui.setCurrentProject(alias)
        if self.field(u"CreateGbsChroot"):
            self.callWithInfiniteProgress(self.manager.createChRoot,
                                          u"Creating chroot...",
                                          alias)
        return True


    def nextId(self):
        return self.wizard().pageIndex(u'ChooseNewOrExistingPackage')

