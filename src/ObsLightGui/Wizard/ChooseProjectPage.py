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

from ObsLightGui.FilterableWidget import FilterableWidget

# See below
#from ObsLightGui.Utils import uiFriendly

from WizardPageWrapper import ObsLightWizardPage

class ChooseProjectPage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProject.ui")
        FilterableWidget.__init__(self, self.ui_WizardPage.filterLineEdit,
                                  self.ui_WizardPage.projectListWidget)
        self.registerField(u"projectRow*", self.ui_WizardPage.projectListWidget)


    def initializePage(self):
        serverAlias = self.field(u"serverAlias")
        self.setBusyCursor(self._fillProjectList, serverAlias)

    def _fillProjectList(self, serverAlias):
        self.ui_WizardPage.projectListWidget.clear()
        prjList = self._getProjectList(serverAlias)
        self.ui_WizardPage.projectListWidget.addItems(prjList)

    # I don't know why, but here uiFriendly prevents the wizard page
    # to refresh when getProjectList returns quickly.
    #@uiFriendly()
    def _getProjectList(self, serverAlias):
        return self.manager.getObsServerProjectList(serverAlias)

    def getSelectedProject(self):
        return self.ui_WizardPage.projectListWidget.item(self.field(u"projectRow")).text()
