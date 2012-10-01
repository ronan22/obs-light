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

from PySide.QtGui import QStandardItemModel, QStandardItem, QCheckBox
from PySide.QtCore import QAbstractListModel, Qt, QAbstractItemModel
from PySide.QtGui import QFileDialog

class ChooseManifestPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseManifest.ui")
        self.__selectedManifestFilePath = None
        self.__ManifestFileDict = None

        self.registerField(u"liveManifest", self.ui_WizardPage.liveManifestButton)
        self.ui_WizardPage.liveManifestButton.toggled.connect(self.__OnLiveManifestButton)
        self.registerField(u"listManifest", self.ui_WizardPage.listManifestButton)
        self.ui_WizardPage.listManifestButton.toggled.connect(self.__OnListManifestButton)
        self.registerField(u"customManifest", self.ui_WizardPage.customManifestButton)
        self.ui_WizardPage.customManifestButton.toggled.connect(self.__OnCustomManifestButtonn)

        self.ui_WizardPage.loadManifestPushButton.clicked.connect(self.on_loadManifestPushButton_clicked)

        self.ui_WizardPage.ManifestListWidget.currentRowChanged.connect(self.selectManifestRow)

        self.__OnListManifestButton()

    def __OnLiveManifestButton(self):
        self.ui_WizardPage.ManifestListWidget.setEnabled(False)
        self.ui_WizardPage.lineManifestEdit.setEnabled(False)
        self.ui_WizardPage.loadManifestPushButton.setEnabled(False)
        self.completeChanged.emit()
        return False

    def __OnListManifestButton(self):
        self.ui_WizardPage.ManifestListWidget.setEnabled(True)
        self.ui_WizardPage.lineManifestEdit.setEnabled(False)
        self.ui_WizardPage.loadManifestPushButton.setEnabled(False)
        self.completeChanged.emit()
        return False

    def __OnCustomManifestButtonn(self):
        self.ui_WizardPage.ManifestListWidget.setEnabled(False)
        self.ui_WizardPage.lineManifestEdit.setEnabled(True)
        self.ui_WizardPage.loadManifestPushButton.setEnabled(True)
        self.completeChanged.emit()
        return False

    def initializePage(self):

        self.__OnListManifestButton()
        self.ui_WizardPage.ManifestListWidget.clear()

        self.__ManifestFileDict = self.manager.getProjectManifestList()

        self.ui_WizardPage.ManifestListWidget.addItems(self.__ManifestFileDict.keys())

    def on_loadManifestPushButton_clicked(self):
        filters = "manifest files (*.xml);;All files (*)"
        filePath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        "Select manifest file (*.xml) to import",
                                                        filter=filters)
        if len(filePath) < 1:
            return None

        self.ui_WizardPage.lineManifestEdit.setText(filePath)
        self.__selectedManifestFilePath = filePath
        self.completeChanged.emit()

    def selectManifestRow(self, _row):
        if self.__ManifestFileDict is not None:
            currentItem = self.ui_WizardPage.ManifestListWidget.currentItem()
            if currentItem is not None:
                aFile = currentItem.text()
                self.__selectedManifestFilePath = self.__ManifestFileDict.get(aFile, None)
            else:
                self.__selectedManifestFilePath = None
        else:
            self.__selectedManifestFilePath = None

        self.completeChanged.emit()

    def nextId(self):
        return self.wizard().pageIndex(u'ConfigureGitPackagePage')

    def isComplete(self):
        return self.__selectedManifestFilePath  is not None

    def validatePage(self):
#        print 'self.field(u"liveManifest")', self.field(u"liveManifest")
        if self.field(u"liveManifest"):

            user = "ronan"
            res = self.callWithInfiniteProgress(self.manager.generateUpdatedTizenManifest,
                                               "generate updated Tizen Manifest for %s user." % user,
                                               user)

            self.__selectedManifestFilePath = res
            return True
        else:
            return self.isComplete()

    def getManifestFilePath(self):
        return self.__selectedManifestFilePath




