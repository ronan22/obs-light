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

from PySide.QtGui import QFileDialog


class ChooseProjectConfPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProjectConf.ui")

        self.registerField(u"chooseConf", self.ui_WizardPage.chooseConfButton)
        self.ui_WizardPage.chooseConfButton.toggled.connect(self.__completeChanged)

        self.registerField(u"chooseGbsConf", self.ui_WizardPage.chooseGbsConfButton)
        self.ui_WizardPage.chooseGbsConfButton.toggled.connect(self.__completeChanged)

        self.registerField(u"addNewConf", self.ui_WizardPage.addNewConfButton)
        self.ui_WizardPage.addNewConfButton.toggled.connect(self.__completeChanged)

        self.registerField(u"LocalConfList", self.ui_WizardPage.LocalConfListWidget)
        self.ui_WizardPage.LocalConfListWidget.currentRowChanged.connect(self.selectConfRow)

        self.registerField(u"LocalGbsConfList", self.ui_WizardPage.LocalGbsConfListWidget)
        self.ui_WizardPage.LocalGbsConfListWidget.currentRowChanged.connect(self.selectGbsConfRow)

        self.ui_WizardPage.LoadConfFileButton.clicked.connect(self.on_loadConfFileButton_clicked)

        self._selectedFile = None
        self.projectConfDict = None
        self.projectGbsConfDict = None
        self._loadConfFile = None

    def initializePage(self):
        self.projectConfDict = self.manager.getProjectConfList()
        self.projectGbsConfDict = self.manager.getProjectGbsConfList()

        projectConfList = self.projectConfDict.keys()
        projectGbsConfList = self.projectGbsConfDict.keys()

        projectConfList.sort()
        projectGbsConfList.sort()

        self.ui_WizardPage.LocalConfListWidget.clear()
        self.ui_WizardPage.LocalGbsConfListWidget.clear()

        self.ui_WizardPage.LocalConfListWidget.addItems(projectConfList)
        self.ui_WizardPage.LocalGbsConfListWidget.addItems(projectGbsConfList)

        if len(projectConfList) > 0:
            self.ui_WizardPage.chooseConfButton.setChecked(True)
        elif len(projectGbsConfList) > 0:
            self.ui_WizardPage.chooseGbsConfButton.setChecked(True)
        else:
            self.ui_WizardPage.addNewConfButton.setChecked(True)

        self.__setSelection()

    def __setSelection(self):
        self._selectedFile = None
        if self.ui_WizardPage.chooseConfButton.isChecked():
            self.ui_WizardPage.LocalConfListWidget.setEnabled (True)
            self.ui_WizardPage.LocalGbsConfListWidget.setEnabled (False)
            self.ui_WizardPage.lineEdit.setEnabled (False)
            self.ui_WizardPage.LoadConfFileButton.setEnabled (False)
            self.selectConfRow(0)

        elif self.ui_WizardPage.chooseGbsConfButton.isChecked():
            self.ui_WizardPage.LocalConfListWidget.setEnabled (False)
            self.ui_WizardPage.LocalGbsConfListWidget.setEnabled (True)
            self.ui_WizardPage.lineEdit.setEnabled (False)
            self.ui_WizardPage.LoadConfFileButton.setEnabled (False)
            self.selectGbsConfRow(0)
        else:
            self.ui_WizardPage.LocalConfListWidget.setEnabled (False)
            self.ui_WizardPage.LocalGbsConfListWidget.setEnabled (False)
            self.ui_WizardPage.lineEdit.setEnabled (True)
            self.ui_WizardPage.LoadConfFileButton.setEnabled (True)
            self._selectedFile = self._loadConfFile

#    def isAddNewLocalProject(self):
#        return self.field(u"addNewConf")

#    def LocalProjectRow(self):
#        return self.field(u"LocalConfList")

    def isComplete(self):
        return self._selectedFile  is not None
#        return self.isAddNewLocalProject() or (self.LocalProjectRow() >= 0) or

    def validatePage(self):
#        if not self.isAddNewLocalProject():
#            self.setField(u"serverAlias",
#                          self.ui_WizardPage.LocalConfListWidget.currentItem().text())
        return self.isComplete()

    def nextId(self):
        return self.wizard().pageIndex(u'ChooseRepository')

    def selectConfRow(self, _row):
        if self.projectConfDict is not None:
            currentItem = self.ui_WizardPage.LocalConfListWidget.currentItem()
            if currentItem is not None:
                aFile = currentItem.text()
                self._selectedFile = self.projectConfDict.get(aFile, None)
            else:
                self._selectedFile = None
        else:
            self._selectedFile = None

        self.completeChanged.emit()

    def selectGbsConfRow(self, _row):
        if self.projectGbsConfDict is not None:
            currentItem = self.ui_WizardPage.LocalGbsConfListWidget.currentItem()
            if currentItem is not None:
                aFile = currentItem.text()
                self._selectedFile = self.projectGbsConfDict.get(aFile, None)
            else:
                self._selectedFile = None
        else:
            self._selectedFile = None

        self.completeChanged.emit()

    def __completeChanged(self, _row):
        self.__setSelection()
        self.completeChanged.emit()

    def on_loadConfFileButton_clicked(self):
        filters = "conf files (*.conf);;All files (*)"
        self._loadConfFile, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        "Select conf file (*.conf)",
                                                        filter=filters)
        if len(self._loadConfFile) < 1:
            return
        self._selectedFile = self._loadConfFile
        self.ui_WizardPage.lineEdit.setText(self._selectedFile)
        self.completeChanged.emit()


    def getSelectedProjectConf(self):
        return self._selectedFile
