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

class ChooseProjectArchPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseArchitecture.ui")
        self.registerField(u"archCBox*", self.ui_WizardPage.architectureComboBox)

    def initializePage(self):
        server = self.getSelectedServer()
        project = self.getSelectedProject()
        target = self.getSelectedTarget()
        self.setBusyCursor(self._fillArchCBox, server, project, target)

    def _fillArchCBox(self, server, project, target):
        self.ui_WizardPage.architectureComboBox.clear()
        archList = self._getArchList(server, project, target)
        self.ui_WizardPage.architectureComboBox.addItems(archList)

    @uiFriendly()
    def _getArchList(self, server, project, target):
        return self.manager.getArchitectureList(server, project, target)

    def getSelectedServer(self):
        return self.field(u"serverAlias")

    def getSelectedProject(self):
        chooseProjectPageIndex = self.wizard().pageIndex(u'ChooseProject')
        chooseProjectPage = self.wizard().page(chooseProjectPageIndex)
        project = chooseProjectPage.getSelectedProject()
        return project

    def getSelectedTarget(self):
        chooseTargetPageIndex = self.wizard().pageIndex(u'ChooseProjectTarget')
        chooseTargetPage = self.wizard().page(chooseTargetPageIndex)
        target = chooseTargetPage.getSelectedTarget()
        return target

    def getSelectedArch(self):
        return self.ui_WizardPage.architectureComboBox.currentText()
