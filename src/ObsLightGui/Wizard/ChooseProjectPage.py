# -*- coding: utf8 -*-
#
# Copyright 2011-2012, Intel Inc.
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
from ObsLightGui.Utils import popupOnException

# See below
#from ObsLightGui.Utils import uiFriendly

from WizardPageWrapper import ObsLightWizardPage

class ChooseProjectPage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProject.ui")
        uwp = self.ui_WizardPage
        FilterableWidget.__init__(self, uwp.filterLineEdit,
                                  uwp.projectListWidget)
        self.registerField(u"projectRow*", uwp.projectListWidget)
        self.registerField(u"restrainMaintainer", uwp.restrainMaintainerCheckBox)
        self.registerField(u"restrainBugowner", uwp.restrainBugownerCheckBox)
        self.registerField(u"restrainRemoteLinks", uwp.restrainRemoteLinksCheckBox)
        uwp.restrainMaintainerCheckBox.stateChanged.connect(self._checkBoxStateChanged)
        uwp.restrainBugownerCheckBox.stateChanged.connect(self._checkBoxStateChanged)
        uwp.restrainRemoteLinksCheckBox.stateChanged.connect(self._checkBoxStateChanged)

    def initializePage(self):
        serverAlias = self.field(u"serverAlias")
        restrainMaintainer = self.field(u"restrainMaintainer")
        restrainBugowner = self.field(u"restrainBugowner")
        restrainRemoteLinks = self.field(u"restrainRemoteLinks")
        self.setBusyCursor(self._fillProjectList, serverAlias, restrainMaintainer,
                           restrainBugowner, restrainRemoteLinks)

    @popupOnException
    def _checkBoxStateChanged(self, _state):
        self.initializePage()

    def _fillProjectList(self, serverAlias, restrainMaintainer,
                         restrainBugowner, restrainRemoteLinks):
        self.ui_WizardPage.projectListWidget.clear()
        prjList = self._getProjectList(serverAlias, restrainMaintainer,
                                       restrainBugowner, restrainRemoteLinks)
        self.ui_WizardPage.projectListWidget.addItems(prjList)

    # I don't know why, but here uiFriendly prevents the wizard page
    # to refresh when getProjectList returns quickly.
    #@uiFriendly()
    def _getProjectList(self, serverAlias, restrainMaintainer,
                        restrainBugowner, restrainRemoteLinks):
        return self.manager.getObsServerProjectList(serverAlias,
                                                    maintainer=restrainMaintainer,
                                                    bugowner=restrainBugowner,
                                                    remoteurl=restrainRemoteLinks)

    def getSelectedProject(self):
        return self.ui_WizardPage.projectListWidget.item(self.field(u"projectRow")).text()
