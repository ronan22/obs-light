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
'''

from WizardPageWrapper import ObsLightWizardPage

class ChooseNewOrExistingPackage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index,
                                    u"wizard_chooseNewOrExistingPackage.ui")
        self.registerField(u"importExistingPackage",
                           self.ui_WizardPage.importExistingPackageButton)
        self.registerField(u"createNewPackage",
                           self.ui_WizardPage.createNewPackageButton)

    def nextId(self):
        if self.field(u"createNewPackage"):
            return self.wizard().pageIndex(u"ConfigureNewPackage")
        else:
            return self.wizard().pageIndex(u"ChoosePackage")