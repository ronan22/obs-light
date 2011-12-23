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

from ObsLightGui.Utils import uiFriendly

from WizardPageWrapper import ObsLightWizardPage

class ChooseProjectTargetPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseTarget.ui")
        self.registerField(u"targetCBox*", self.ui_WizardPage.targetComboBox)

    def initializePage(self):
        server = self.field(u"serverAlias")
        chooseProjectPageIndex = self.wizard().pageIndex(u'ChooseProject')
        chooseProjectPage = self.wizard().page(chooseProjectPageIndex)
        project = chooseProjectPage.getSelectedProject()
        self.setBusyCursor(self._fillTargetCBox, server, project)

    def _fillTargetCBox(self, server, project):
        self.ui_WizardPage.targetComboBox.clear()
        targetList = self._getTargetList(server, project)
        self.ui_WizardPage.targetComboBox.addItems(targetList)

    @uiFriendly()
    def _getTargetList(self, server, project):
        return self.manager.getTargetList(server, project)

    def getSelectedTarget(self):
        return self.ui_WizardPage.targetComboBox.currentText()
