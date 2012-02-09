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
Created on 3 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Qt
from PySide.QtGui import QItemSelectionModel

from ObsLightGuiObject import ObsLightGuiObject
from KickstartRepositoriesModel import KickstartRepositoriesModel
from KickstartPackagesModel import KickstartPackagesModel
from KickstartPackageGroupsModel import KickstartPackageGroupsModel
from KickstartCommandsModel import KickstartCommandsModel

class MicProjectManager(QObject, ObsLightGuiObject):
    # pylint: disable-msg=E0202, E1101

    __projectName = ""
    __repoModel = None
    __pkgModel = None
    __pkgGrpModel = None
    __cmdModel = None

    def __init__(self, gui, name):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectName = name
        self.__repoModel = KickstartRepositoriesModel(self.manager, self.name)
        self.__pkgModel = KickstartPackagesModel(self.manager, self.name)
        self.__pkgGrpModel = KickstartPackageGroupsModel(self.manager, self.name)
        self.__cmdModel = KickstartCommandsModel(self.manager, self.name)

    def __loadUi(self):
        self.__loadImageType()
        self.__loadArchitecture()
        self.mainWindow.kickstartPathLineEdit.setText(self.manager.getKickstartFile(self.name))
        self.mainWindow.kickstartRepositoriesTableView.setModel(self.repositoryModel)
        self.mainWindow.kickstartPackagesTableView.setModel(self.packageModel)
        self.mainWindow.kickstartPackageGroupsTableView.setModel(self.packageGroupModel)
        self.__loadCommands()
        self.__updateSaveState()

    def __loadImageType(self):
        imageTypes = self.manager.getAvailableMicProjectImageTypes(self.name)
        self.mainWindow.imageTypeComboBox.clear()
        self.mainWindow.imageTypeComboBox.addItems(imageTypes)
        index = self.mainWindow.imageTypeComboBox.findText(self.imageType,
                                                           Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.imageTypeComboBox.setCurrentIndex(index)

    def __loadArchitecture(self):
        architectures = self.manager.getAvailableMicProjectArchitectures(self.name)
        self.mainWindow.architectureComboBox.clear()
        self.mainWindow.architectureComboBox.addItems(architectures)
        index = self.mainWindow.architectureComboBox.findText(self.architecture,
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.architectureComboBox.setCurrentIndex(index)

    def __loadCommands(self):
        self.mainWindow.kickstartOptionsListView.setModel(self.commandModel)
        self.mainWindow.kickstartOptionsListView.setModelColumn(self.commandModel.AliasesColumn)
        for row in range(self.commandModel.rowCount()):
            index = self.commandModel.createIndex(row, self.commandModel.InUseColumn)
            inUse = self.commandModel.data(index, Qt.DisplayRole)
            self.mainWindow.kickstartOptionsListView.setRowHidden(row, not inUse)

    def __updateSaveState(self):
        self.mainWindow.saveKickstartOptionButton.setEnabled(self.commandModel.hasBeenModified())

    @property
    def name(self):
        """
        Get the MIC project name.
        """
        return self.__projectName

    @property
    def imageType(self):
        return self.manager.getMicProjectImageType(self.name)

    @imageType.setter
    def imageType(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectImageType(self.name, value)

    @property
    def architecture(self):
        return self.manager.getMicProjectArchitecture(self.name)

    @architecture.setter
    def architecture(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectArchitecture(self.name, value)

    @property
    def repositoryModel(self):
        return self.__repoModel

    @property
    def packageModel(self):
        return self.__pkgModel

    @property
    def packageGroupModel(self):
        return self.__pkgGrpModel

    @property
    def commandModel(self):
        return self.__cmdModel

    def refresh(self):
        self.repositoryModel.refresh()
        self.packageModel.refresh()
        self.packageGroupModel.refresh()
        self.commandModel.refresh()
        self.__loadUi()

    def createImage(self):
        self.manager.createImage(self.name)

# --- Repositories -----------------------------------------------------------
    def addRepository(self, name, url):
        self.repositoryModel.addRepository(name, url)

    def removeRepository(self, name):
        self.repositoryModel.removeRepository(name)

    def getRepositoryNameByRowId(self, row):
        if row < 0 or row > self.repositoryModel.rowCount():
            return None
        repoNameIndex = self.repositoryModel.createIndex(row,
                                                         KickstartRepositoriesModel.NameColumn)
        repoName = self.repositoryModel.data(repoNameIndex)
        return repoName

# --- Packages ---------------------------------------------------------------
    def addPackage(self, name):
        self.packageModel.addPackage(name)

    def removePackage(self, name):
        self.packageModel.removePackage(name)

    def addPackageGroup(self, name):
        self.packageGroupModel.addPackageGroup(name)

    def removePackageGroup(self, name):
        self.packageGroupModel.removePackageGroup(name)

    def getPackageNameByRowId(self, row):
        if row < 0 or row > self.packageModel.rowCount():
            return None
        pkgNameIndex = self.packageModel.createIndex(row,
                                                     KickstartPackagesModel.NameColumn)
        pkgName = self.packageModel.data(pkgNameIndex)
        return pkgName

    def getPackageGroupNameByRowId(self, row):
        if row < 0 or row > self.packageGroupModel.rowCount():
            return None
        grpNameIndex = self.packageGroupModel.createIndex(row,
                                                          KickstartPackageGroupsModel.NameColumn)
        grpName = self.packageGroupModel.data(grpNameIndex)
        return grpName

# --- Commands ---------------------------------------------------------------
    def displayCommand(self, row):
        index = self.commandModel.createIndex(row, KickstartCommandsModel.GeneratedTextColumn)
        cmdText = self.commandModel.data(index, Qt.DisplayRole)
        self.mainWindow.kickstartOptionTextEdit.clear()
        self.mainWindow.kickstartOptionTextEdit.appendPlainText(cmdText)

    def editCommand(self, row):
        index = self.commandModel.createIndex(row, KickstartCommandsModel.GeneratedTextColumn)
        text = self.mainWindow.kickstartOptionTextEdit.toPlainText()
        self.commandModel.setData(index, text, Qt.DisplayRole)
        self.__updateSaveState()

    def saveCommands(self):
        self.commandModel.commitChanges()
        self.__updateSaveState()
        self.refresh()

    def addNewCommand(self):
        self.commandModel.newCommand()
        self.__loadCommands()
        lastRow = self.commandModel.rowCount() - 1
        index = self.commandModel.createIndex(lastRow, 0)
        selectionModel = self.mainWindow.kickstartOptionsListView.selectionModel()
        selectionModel.setCurrentIndex(index, QItemSelectionModel.SelectionFlag.SelectCurrent)
        self.displayCommand(lastRow)
        self.__updateSaveState()

    def removeCommand(self, row):
        self.commandModel.removeCommand(row)
        self.__updateSaveState()
        self.__loadCommands()
