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

class ChooseProjectTemplatePage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProjectTemplate.ui")

#        self.registerField(u"addNewLocalProject", self.ui_WizardPage.addNewLocalProjectButton)
#        self.ui_WizardPage.addNewLocalProjectButton.toggled.connect(self.__completeChanged)
        self.registerField(u"LocalProjectList", self.ui_WizardPage.LocalProjectListWidget)
        self.ui_WizardPage.LocalProjectListWidget.currentRowChanged.connect(self.selectLocalProjectRow)

        self.projectTemplateDict = None
        self._selectedFile = None

    def initializePage(self):
        self.projectTemplateDict = self.manager.getProjectTemplateList()

        projectDefaultTemplateDict = self.manager.getProjectTemplateList(False)
        projectDefaultTemplateList = projectDefaultTemplateDict.keys()
        projectDefaultTemplateList.sort()
        if len(projectDefaultTemplateList) > 0:
            self._selectedFile = projectDefaultTemplateDict[projectDefaultTemplateList[0]]
            self.ui_WizardPage.projectTemplateConfLabel.setText(projectDefaultTemplateList[0])
            for p in projectDefaultTemplateList[1:]:
                self.projectTemplateDict[p] = projectDefaultTemplateDict[p]
        else:
            self.ui_WizardPage.chooseObslightDefaultButton.setEnabled(False)

        projectTemplateList = self.projectTemplateDict.keys()
        projectTemplateList.sort()

        self.ui_WizardPage.LocalProjectListWidget.clear()
        if len(projectTemplateList) > 0:
            self.ui_WizardPage.LocalProjectListWidget.addItems(projectTemplateList)
        else:
            self.ui_WizardPage.chooseNewLocalProjectButton.setEnabled(False)
            self.ui_WizardPage.LocalProjectListWidget.setEnabled(False)

        if len(projectDefaultTemplateList) > 0:
            self.ui_WizardPage.chooseObslightDefaultButton.setChecked(True)

    def selectLocalProjectRow(self, _row):
        if self.projectTemplateDict is not None:
            currentItem = self.ui_WizardPage.LocalProjectListWidget.currentItem()
            if currentItem is not None:
                aFile = currentItem.text()
                self._selectedFile = self.projectTemplateDict.get(aFile, None)
            else:
                self._selectedFile = None
        else:
            self._selectedFile = None
        self.__completeChanged(_row)

    def getSelectedProjectConf(self):
        return self._selectedFile

#    def isAddNewLocalProject(self):
#        return self.field(u"addNewLocalProject")

    def LocalProjectRow(self):
        return self.field(u"LocalProjectList")

    def isComplete(self):
        return (self._selectedFile is not None)

    def validatePage(self):
#        if not self.isAddNewLocalProject():
#            self.setField(u"serverAlias",
#                          self.ui_WizardPage.LocalProjectListWidget.currentItem().text())
        return self.isComplete()

    def nextId(self):
        return self.wizard().pageIndex(u"ChooseRepositoryTree")


    def __completeChanged(self, _row):
        self.completeChanged.emit()
