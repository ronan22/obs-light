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

from WizardPageWrapper import ObsLightWizardPage

class ChooseLocalGbsOrOBSProjectPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseLocalGbsOrOBSProject.ui")

    def initializePage(self):
        self.ui_WizardPage.LocalProjectRadioButton.setChecked(True)

#    def isAddingNewServer(self):
#        return self.field(u"LocalProjectRadioButton")
#
#    def serverRow(self):
#        return self.field(u"serverList")
#
#    def isComplete(self):
#        return self.isAddingNewServer()
#
#    def validatePage(self):
#        if not self.isAddingNewServer():
#            self.setField(u"serverAlias",
#                          self.ui_WizardPage.serverListWidget.currentItem().text())
#        return self.isComplete()

    def nextId(self):
        if self.ui_WizardPage.LocalProjectRadioButton.isChecked():
            return self.wizard().pageIndex(u'ChooseProjectTemplate')
        else:
            return self.wizard().pageIndex(u"ChooseServer")

#    def __completeChanged(self, _row):
#        self.completeChanged.emit()
