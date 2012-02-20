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

import os.path

from PySide.QtCore import QObject, Qt
from PySide.QtGui import QFileDialog, QInputDialog, QItemSelectionModel

from ObsLightGuiObject import ObsLightGuiObject
from KickstartRepositoriesModel import KickstartRepositoriesModel
from KickstartPackagesModel import KickstartPackagesModel
from KickstartPackageGroupsModel import KickstartPackageGroupsModel
from KickstartCommandsModel import KickstartCommandsModel
from KickstartScriptsModel import KickstartScriptsModel
from KickstartOverlayFilesModel import KickstartOverlayFilesModel

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
        self.__overlayModel = KickstartOverlayFilesModel(self.manager,
                                                         self.currentProject)

    def __loadUi(self):
        self.__loadImageType()
        self.__loadArchitecture()
        self.__loadModels()
        self.__loadCommands()
        self.__updateSaveState()
        self.mainWindow.micProjectPathLineEdit.setText(self.currentProjectPath)

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

    def __loadModels(self):
        """Associate view objects to their respective model"""
        mw = self.mainWindow
        mw.kickstartRepositoriesTableView.setModel(self.repositoryModel)
        mw.kickstartPackagesTableView.setModel(self.packageModel)
        mw.kickstartPackageGroupsTableView.setModel(self.packageGroupModel)
        mw.kickstartScriptsListView.setModel(self.scriptModel)
        mw.kickstartOverlayFilesTableView.setModel(self.overlayModel)

        mw.kickstartPackageGroupsTableView.resizeColumnToContents(self.packageGroupModel.NameColumn)
        for col in (self.packageModel.NameColumn, self.packageModel.ExcludedColumn):
            mw.kickstartPackagesTableView.resizeColumnToContents(col)
        for col in (self.overlayModel.DestinationColumn, self.overlayModel.SourceColumn):
            mw.kickstartOverlayFilesTableView.resizeColumnToContents(col)

    def __loadCommands(self):
        """Load commands in Kickstart options tab, and hide those which are not active"""
        self.mainWindow.kickstartOptionsListView.setModel(self.commandModel)
        aliasColumn = KickstartCommandsModel.AliasesColumn
        self.mainWindow.kickstartOptionsListView.setModelColumn(aliasColumn)
        # FIXME: modify ObsLightKickstartManager so it does not send unused commands
        for row in range(self.commandModel.rowCount()):
            index = self.commandModel.createIndex(row, KickstartCommandsModel.InUseColumn)
            inUse = self.commandModel.data(index, Qt.DisplayRole)
            self.mainWindow.kickstartOptionsListView.setRowHidden(row, not inUse)

    def __updateSaveState(self):
        """
        Activate/deactivate Kickstart option 'save' button, if
        commands have been modified or not
        """
        self.mainWindow.saveKickstartOptionButton.setEnabled(self.commandModel.modified)
        self.mainWindow.saveKickstartScriptButton.setEnabled(self.scriptModel.modified)

    @property
    def currentProject(self):
        """Get the MIC project name."""
        return self.__projectName

    @property
    def currentProjectPath(self):
        ksPath = self.manager.getKickstartFile(self.currentProject)
        projectPath = os.path.dirname(ksPath)
        return projectPath

    @property
    def currentProjectKickstartPath(self):
        return self.manager.getKickstartFile(self.currentProject)

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

    @property
    def overlayModel(self):
        return self.__overlayModel

    def refresh(self):
        """Refresh the project, reload Kickstart data in the UI"""
        self.repositoryModel.refresh()
        self.packageModel.refresh()
        self.packageGroupModel.refresh()
        self.commandModel.refresh()
        self.scriptModel.refresh()
        self.overlayModel.refresh()
        self.__loadUi()

    def createImage(self):
        """Start the creation of an image"""
        self.callWithInfiniteProgress(self.manager.createImage,
                                      "Creating file system image... (may be long)",
                                      self.currentProject)

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
        self.mainWindow.errorOnFailCheckBox.setChecked(bool(errorOnFail))

        noChroot = not getVal(KickstartScriptsModel.RunInChrootColumn)
        self.mainWindow.noChrootCheckBox.setChecked(bool(noChroot))

        interpreter = getVal(KickstartScriptsModel.InterpreterColumn)
        self.mainWindow.interpreterLineEdit.setText(interpreter)
        defaultInterpreter = KickstartScriptsModel.NewScriptInterpreter
        self.mainWindow.specifyInterpreterCheckBox.setChecked(interpreter != defaultInterpreter)

        logFile = getVal(KickstartScriptsModel.LogFileColumn)
        self.mainWindow.logFileLineEdit.setText(logFile)
        self.mainWindow.specifyLogFileCheckBox.setChecked(logFile is not None)

        scriptText = getVal(KickstartScriptsModel.ScriptColumn)
        self.mainWindow.kickstartScriptTextEdit.clear()
        self.mainWindow.kickstartScriptTextEdit.appendPlainText(scriptText)

    def addNewScript(self):
        """
        Add a new script at the end of the script list.
        """
        self.scriptModel.newScript()
        self.__updateSaveState()

    def removeScript(self, row):
        """
        Remove the script at `row` from the script list.
        """
        self.scriptModel.removeScript(row)
        self.__updateSaveState()

    def editScript(self, row):
        """
        Save the text in the Kickstart script TextEdit
        and all selected options
        as the content of the script at `row`
        """
        def setVal(column, value):
            index = self.scriptModel.createIndex(row, column)
            self.scriptModel.setData(index, value, Qt.DisplayRole)

        text = self.mainWindow.kickstartScriptTextEdit.toPlainText()
        setVal(KickstartScriptsModel.ScriptColumn, text)

        if self.mainWindow.tracebackScriptRadioButton.isChecked():
            scriptType = 2
        elif self.mainWindow.postScriptRadioButton.isChecked():
            scriptType = 1
        else:
            scriptType = 0
        setVal(KickstartScriptsModel.TypeColumn, scriptType)

        noChroot = self.mainWindow.noChrootCheckBox.isChecked()
        setVal(KickstartScriptsModel.RunInChrootColumn, not noChroot)

        errorOnFail = self.mainWindow.errorOnFailCheckBox.isChecked()
        setVal(KickstartScriptsModel.ErrorOnFailColumn, errorOnFail)

        if self.mainWindow.specifyInterpreterCheckBox.isChecked():
            interpreter = self.mainWindow.interpreterLineEdit.text()
        else:
            interpreter = KickstartScriptsModel.NewScriptInterpreter
        setVal(KickstartScriptsModel.InterpreterColumn, interpreter)

        if self.mainWindow.specifyLogFileCheckBox.isChecked():
            logFile = self.mainWindow.logFileLineEdit.text()
        else:
            logFile = None
        setVal(KickstartScriptsModel.LogFileColumn, logFile)

        self.__updateSaveState()

    def saveScripts(self):
        """
        Commit all the changes made to Kickstart scripts
        to the Kickstart file
        """
        self.scriptModel.commitChanges()
        self.refresh()

# --- Overlay files ----------------------------------------------------------
    def addNewOverlay(self):
        """
        Add a new overlay file. Asks user for source and destination.
        """
        extensions = (".tar", ".tar.gz", ".tar.bz2", ".tgz", ".tbz", ".tz2", ".tar.xz")
        filters = "Tar archives (%s);;" % " *".join(extensions)
        filters += "All files (*)"
        srcPath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                       "Select source file",
                                                       filter=filters)
        if len(srcPath) < 1:
            return
        defaultDstPath = "/%s" % os.path.basename(srcPath)
        for ext in extensions:
            if srcPath.endswith(ext):
                defaultDstPath = "/"
        dstPath, accepted = QInputDialog.getText(self.mainWindow,
                                                 "Select destination",
                                                 "Select destination file or directory where " +
                                                 "archive will be extracted",
                                                 text=defaultDstPath)
        if not accepted:
            return
        self.callWithInfiniteProgress(self.overlayModel.newOverlayFile,
                                      "Copying overlay file in project directory...",
                                      source=srcPath, destination=dstPath)
        self.refresh()

    def removeOverlays(self, rows):
        """
        Remove the overlay file at `row` from the Kickstart file.
        """
        self.overlayModel.removeOverlayFiles(rows)
        self.refresh()
