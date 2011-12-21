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

from PySide.QtGui import QListWidget

#from ObsLightGui.Utils import uiFriendly

from WizardPageLoader import WizardPageLoader

class ChooseProjectWizardPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_chooseProject.ui")
        self.projectListWidget = self.page.findChild(QListWidget, u"projectListWidget")
        self.page.registerField(u"projectRow*", self.projectListWidget)
        self.page.initializePage = self._initializePage
        self.page.getSelectedProject = self.getSelectedProject

    def _initializePage(self):
        serverAlias = self.page.field(u"serverAlias")
        self.waitWhile(self._fillProjectList, serverAlias)

    def _fillProjectList(self, serverAlias):
        self.projectListWidget.clear()
        prjList = self._getProjectList(serverAlias)
        self.projectListWidget.addItems(prjList)

    # I don't know why, but here uiFriendly prevents the wizard page
    # to refresh when getProjectList returns quickly.
    #@uiFriendly()
    def _getProjectList(self, serverAlias):
        return self.manager.getObsServerProjectList(serverAlias)

    def getSelectedProject(self):
        return self.projectListWidget.item(self.page.field(u"projectRow")).text()
