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
Created on 17 avr. 2012

@author: Florent Vennetier
@author: Ronan Le Martret
'''

from WizardPageWrapper import ObsLightWizardPage
from ObsLightGui.Utils import popupOnException

class ChooseNewOrExistingPackagePage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index,
                                    u"wizard_chooseNewOrExistingPackage.ui")
        self.registerField(u"importExistingPackage",
                           self.ui_WizardPage.importExistingPackageButton)
        self.registerField(u"createNewPackage",
                           self.ui_WizardPage.createNewPackageButton)
        #TMP remove this (Import package from an other local OBS Light Project)
#        self.registerField(u"copyPackage",
#                           self.ui_WizardPage.copyPackageButton)

        self.registerField(u"importManifestButton",
                           self.ui_WizardPage.importManifestButton)

    @popupOnException
    def initializePage(self):
        projectAlias = self.wizard().getSelectedProjectAlias()
        isLocalProject = self.manager.getProjectParameter(projectAlias, "isLocalProject")
        if isLocalProject:
            self.ui_WizardPage.importExistingPackageButton.setEnabled(False)
#            self.ui_WizardPage.createNewPackageButton.setToolTip(u"Project is read only")

    def nextId(self):
        if self.field(u"createNewPackage"):
            return self.wizard().pageIndex(u"ConfigureNewPackage")
#        elif self.field(u"copyPackage"):
#            return self.wizard().pageIndex(u"ChooseLocalProject")
        elif self.field(u"importManifestButton"):
            return self.wizard().pageIndex(u"ChooseManifestPage")
        else:
            return self.wizard().pageIndex(u"ChoosePackage")
