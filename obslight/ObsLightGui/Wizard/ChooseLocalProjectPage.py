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
Created on 05 sept. 2012

@author: Ronan Le Martret
'''
from PySide.QtGui import QMessageBox
from ObsLightGui.FilterableWidget import FilterableWidget
from ObsLightGui.Utils import popupOnException, ProgressRunnable2

from WizardPageWrapper import ObsLightWizardPage

class ChooseLocalProjectPage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseLocalProject.ui")
        uwp = self.ui_WizardPage
        FilterableWidget.__init__(self, uwp.filterLineEdit,
                                  uwp.projectListWidget)

        self.registerField(u"projectList", self.ui_WizardPage.projectListWidget)
        self.ui_WizardPage.projectListWidget.currentRowChanged.connect(self.__completeChanged)

    def initializePage(self):
        projectList = self.manager.getLocalProjectList()
        projectSrc = self.field(u"projectAlias")
        if projectSrc in projectList:
            projectList.remove(projectSrc)
        self.ui_WizardPage.projectListWidget.addItems(projectList)

    @popupOnException
    def validatePage(self):
        return self.isComplete()

    def getSelectedLocalProject(self):
        return self.ui_WizardPage.projectListWidget.item(self.field(u"projectList")).text()

    def __completeChanged(self, _row):
        self.completeChanged.emit()

    def projectRow(self):
        return self.field(u"projectList")

    def isComplete(self):
        return (self.projectRow() >= 0)

