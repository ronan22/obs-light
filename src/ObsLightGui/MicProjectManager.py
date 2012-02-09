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
from KickstartScriptsModel import KickstartScriptsModel

class MicProjectManager(QObject, ObsLightGuiObject):
    # pylint: disable-msg=E0202, E1101

    def __init__(self, gui, name):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectName = name
        self.__repoModel = KickstartRepositoriesModel(self.manager, self.currentProject)
        self.__pkgModel = KickstartPackagesModel(self.manager, self.currentProject)
        self.__pkgGrpModel = KickstartPackageGroupsModel(self.manager, self.currentProject)
        self.__cmdModel = KickstartCommandsModel(self.manager, self.currentProject)
        self.__scriptModel = KickstartScriptsModel(self.manager, self.currentProject)

    def __loadUi(self):
        self.__loadImageType()
        self.__loadArchitecture()
        mw = self.mainWindow
        mw.kickstartPathLineEdit.setText(self.manager.getKickstartFile(self.currentProject))
        mw.kickstartRepositoriesTableView.setModel(self.repositoryModel)
        mw.kickstartPackagesTableView.setModel(self.packageModel)
        mw.kickstartPackageGroupsTableView.setModel(self.packageGroupModel)
        mw.kickstartScriptsListView.setModel(self.scriptModel)
        self.__loadCommands()
        self.__updateSaveState()

    def __loadImageType(self):
        """Load MIC image type values and preselect the current one"""
        imageTypes = self.manager.getAvailableMicProjectImageTypes(self.currentProject)
        self.mainWindow.imageTypeComboBox.clear()
        self.mainWindow.imageTypeComboBox.addItems(imageTypes)
        index = self.mainWindow.imageTypeComboBox.findText(self.imageType,
                                                           Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.imageTypeComboBox.setCurrentIndex(index)

    def __loadArchitecture(self):
        """Load MIC architecture type values and preselect the current one"""
        architectures = self.manager.getAvailableMicProjectArchitectures(self.currentProject)
        self.mainWindow.architectureComboBox.clear()
        self.mainWindow.architectureComboBox.addItems(architectures)
        index = self.mainWindow.architectureComboBox.findText(self.architecture,
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.architectureComboBox.setCurrentIndex(index)

    def __loadCommands(self):
        """Load commands in Kickstart options tab, and hide those which are not active"""
        self.mainWindow.kickstartOptionsListView.setModel(self.commandModel)
        aliasColumn = KickstartCommandsModel.AliasesColumn
        self.mainWindow.kickstartOptionsListView.setModelColumn(aliasColumn)
        for row in range(self.commandModel.rowCount()):
            index = self.commandModel.createIndex(row, KickstartCommandsModel.InUseColumn)
            inUse = self.commandModel.data(index, Qt.DisplayRole)
            self.mainWindow.kickstartOptionsListView.setRowHidden(row, not inUse)

    def __updateSaveState(self):
        """
        Activate/deactivate Kickstart option 'save' button, if
        commands have been modified or not
        """
        self.mainWindow.saveKickstartOptionButton.setEnabled(self.commandModel.hasBeenModified())

    @property
    def currentProject(self):
        """Get the MIC project name."""
        return self.__projectName

    @property
    def imageType(self):
        """Get the MIC project image type"""
        return self.manager.getMicProjectImageType(self.currentProject)

    @imageType.setter
    def imageType(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectImageType(self.currentProject, value)

    @property
    def architecture(self):
        """Get the MIC project architecture"""
        return self.manager.getMicProjectArchitecture(self.currentProject)

    @architecture.setter
    def architecture(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectArchitecture(self.currentProject, value)

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

    @property
    def scriptModel(self):
        return self.__scriptModel

    def refresh(self):
        """Refresh the project, reload Kickstart data in the UI"""
        self.repositoryModel.refresh()
        self.packageModel.refresh()
        self.packageGroupModel.refresh()
        self.commandModel.refresh()
        self.scriptModel.refresh()
        self.__loadUi()

    def createImage(self):
        """Start the creation of an image"""
        self.manager.createImage(self.currentProject)

# --- Repositories -----------------------------------------------------------
    def addRepository(self, name, url):
        """
        Add a repository with alias `name` and URL `url` in the Kickstart file
        """
        self.repositoryModel.addRepository(name, url)

    def removeRepository(self, name):
        """
        Remove the repository with alias `name` from the Kickstart file
        """
        self.repositoryModel.removeRepository(name)

    def getRepositoryNameByRowId(self, row):
        """
        Get the name (alias) of a repository by providing its row ID
        in the table view or model
        """
        if row < 0 or row > self.repositoryModel.rowCount():
            return None
        repoNameIndex = self.repositoryModel.createIndex(row,
                                                         KickstartRepositoriesModel.NameColumn)
        repoName = self.repositoryModel.data(repoNameIndex)
        return repoName

# --- Packages ---------------------------------------------------------------
    def addPackage(self, name):
        """Add the package `name` in the Kickstart file"""
        self.packageModel.addPackage(name)

    def removePackage(self, name):
        """Remove the package `name` from the Kickstart file"""
        self.packageModel.removePackage(name)

    def addPackageGroup(self, name):
        """Add the package group `name` in the Kickstart file"""
        self.packageGroupModel.addPackageGroup(name)

    def removePackageGroup(self, name):
        """Remove the package group `name` from the Kickstart file"""
        self.packageGroupModel.removePackageGroup(name)

    def getPackageNameByRowId(self, row):
        """
        Get the name of a package by providing its row ID
        in the table view or model
        """
        if row < 0 or row > self.packageModel.rowCount():
            return None
        pkgNameIndex = self.packageModel.createIndex(row,
                                                     KickstartPackagesModel.NameColumn)
        pkgName = self.packageModel.data(pkgNameIndex)
        return pkgName

    def getPackageGroupNameByRowId(self, row):
        """
        Get the name of a package group by providing its row ID
        in the table view or model
        """
        if row < 0 or row > self.packageGroupModel.rowCount():
            return None
        grpNameIndex = self.packageGroupModel.createIndex(row,
                                                          KickstartPackageGroupsModel.NameColumn)
        grpName = self.packageGroupModel.data(grpNameIndex)
        return grpName

# --- Commands ---------------------------------------------------------------
    def displayCommand(self, row):
        """
        Display in the Kickstart options TextEdit
        the whole text of the Kickstart command at `row`
        """
        index = self.commandModel.createIndex(row, KickstartCommandsModel.GeneratedTextColumn)
        cmdText = self.commandModel.data(index, Qt.DisplayRole)
        self.mainWindow.kickstartOptionTextEdit.clear()
        self.mainWindow.kickstartOptionTextEdit.appendPlainText(cmdText)

    def editCommand(self, row):
        """
        Save the text in the Kickstart options TextEdit
        as the full text of the command at `row`
        """
        index = self.commandModel.createIndex(row, KickstartCommandsModel.GeneratedTextColumn)
        text = self.mainWindow.kickstartOptionTextEdit.toPlainText()
        self.commandModel.setData(index, text, Qt.DisplayRole)
        self.__updateSaveState()

    def saveCommands(self):
        """
        Commit all the changes made to Kickstart commands
        to the Kickstart file
        """
        self.commandModel.commitChanges()
        self.__updateSaveState()
        self.refresh()

    def addNewCommand(self):
        """
        Add a new command at the end of the command list.
        You must edit this command and then save for it
        to be taken into account.
        """
        self.commandModel.newCommand()
        self.__loadCommands()
        lastRow = self.commandModel.rowCount() - 1
        index = self.commandModel.createIndex(lastRow, 0)
        selectionModel = self.mainWindow.kickstartOptionsListView.selectionModel()
        selectionModel.setCurrentIndex(index, QItemSelectionModel.SelectionFlag.SelectCurrent)
        self.displayCommand(lastRow)
        self.__updateSaveState()

    def removeCommand(self, row):
        """
        Remove the command at `row` from the Kickstart file.
        You must save for it to be actually removed.
        """
        self.commandModel.removeCommand(row)
        self.__updateSaveState()
        self.__loadCommands()

# --- Scripts ----------------------------------------------------------------
    def displayScript(self, row):
        """
        Load the Kickstart script tab widgets
        with the parameters of script at `row`
        """
        def getVal(column):
            index = self.scriptModel.createIndex(row, column)
            return self.scriptModel.data(index, Qt.DisplayRole)

        scriptType = getVal(KickstartScriptsModel.TypeColumn)
        self.mainWindow.preScriptRadioButton.setChecked(scriptType == 0)
        self.mainWindow.postScriptRadioButton.setChecked(scriptType == 1)
        self.mainWindow.tracebackScriptRadioButton.setChecked(scriptType == 2)

        errorOnFail = getVal(KickstartScriptsModel.ErrorOnFailColumn)
        self.mainWindow.errorOnFailCheckBox.setChecked(errorOnFail)

        noChroot = not getVal(KickstartScriptsModel.RunInChrootColumn)
        self.mainWindow.noChrootCheckBox.setChecked(noChroot)

        interpreter = getVal(KickstartScriptsModel.InterpreterColumn)
        self.mainWindow.interpreterLineEdit.setText(interpreter)
        self.mainWindow.specifyInterpreterCheckBox.setChecked(interpreter != "/bin/sh")

        logFile = getVal(KickstartScriptsModel.LogFileColumn)
        self.mainWindow.logLineEdit.setText(logFile)
        self.mainWindow.specifyLogFileCheckBox.setChecked(logFile is not None)

        scriptText = getVal(KickstartScriptsModel.ScriptColumn)
        self.mainWindow.kickstartScriptTextEdit.clear()
        self.mainWindow.kickstartScriptTextEdit.appendPlainText(scriptText)
