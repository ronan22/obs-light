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
Created on 4 nov. 2011

@author: Florent Vennetier
'''

from os.path import join as joinPath

from PySide.QtCore import QObject
from PySide.QtGui import QFileDialog, QFileSystemModel, QMessageBox

from ObsLight.ObsLightUtils import isNonEmptyString
from Utils import popupOnException
from ObsLightGuiObject import ObsLightGuiObject

from OscWorkingCopyModel import OscWorkingCopyModel

class FileManager(QObject, ObsLightGuiObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectFileSystemModel = None
        self.__oscWcModel = None
        self.__project = None
        self.__package = None
        self.__packageDir = None
        self.__packageInChrootDir = None
        self.__projectFileSystemPath = None

        self.mainWindow.fileTableView.doubleClicked.connect(self.on_fileTableView_activated)
        self.mainWindow.chrootTreeView.doubleClicked.connect(self.on_chrootTreeView_activated)
        self.mainWindow.chrootTreeView.clicked.connect(self.on_chrootTreeView_clicked)
        self.mainWindow.addFileButton.clicked.connect(self.on_addFileButton_clicked)
        self.mainWindow.deleteFileButton.clicked.connect(self.on_deleteFileButton_clicked)

    def setCurrentPackage(self, project, package):
        '''
        Set the package that you want this class to operate on.
        None is valid, and will disable the right panel.
        '''
        if not isNonEmptyString(project):
            project = None
        if not isNonEmptyString(package):
            package = None
        self.__project = project
        self.__package = package
        self.refresh()

    def refresh(self):
        # --- chroot view ---------
        self.__projectFileSystemModel = QFileSystemModel()
        if self.__project is not None and self.__package is not None:

            if self.manager.isChRootInit(self.__project):
                self.mainWindow.chrootTreeView.setEnabled(True)
                pathInChRoot = self.manager.getPackageParameter(self.__project,
                                                                self.__package,
                                                                parameter="fsPackageDirectory")
                chrootPath = self.manager.getChRootPath(self.__project)
                # Qt 4.6 do not know "directoryLoaded"
                if hasattr(self.__projectFileSystemModel, "directoryLoaded"):
                    self.__projectFileSystemModel.directoryLoaded.connect(self.on_chrootPath_loaded)
                self.__packageInChrootDir = chrootPath
                if pathInChRoot is not None:
                    self.__packageInChrootDir += pathInChRoot
                self.__projectFileSystemPath = chrootPath
                self.__projectFileSystemModel.setRootPath(self.__projectFileSystemPath)
                if self.__projectFileSystemPath != self.__packageInChrootDir:
                    self.__projectFileSystemModel.setRootPath(self.__packageInChrootDir)

            else:
                self.mainWindow.chrootTreeView.setEnabled(False)
            self.mainWindow.packageTabWidget.setEnabled(True)
        else:
            self.mainWindow.packageTabWidget.setEnabled(False)
        self.mainWindow.chrootTreeView.setModel(self.__projectFileSystemModel)

        # Qt 4.6 do not know "directoryLoaded"
        if not hasattr(self.__projectFileSystemModel, "directoryLoaded"):
            self.on_chrootPath_loaded(self.__projectFileSystemPath)
            self.on_chrootPath_loaded(self.__packageInChrootDir)

        # --- working copy view ---
        if self.__project is not None and self.__package is not None:
            path = self.manager.getPackageParameter(self.__project,
                                                    self.__package,
                                                    parameter="oscPackageDirectory")

            self.__packageDir = path
            self.__oscWcModel = OscWorkingCopyModel(self.manager,
                                                    self.__project,
                                                    self.__package)
        else:
            self.__oscWcModel = None
        self.mainWindow.fileTableView.setModel(self.__oscWcModel)
        self.mainWindow.fileTableView.resizeColumnToContents(1)

    def on_chrootPath_loaded(self, path):
        """
        Called when the QFileSystem model loads paths.
        """
        ctv = self.mainWindow.chrootTreeView
        if path == self.__projectFileSystemPath:
            # Set the root index of the QTreeView to the root directory of
            # the project file system, so user does not see outside
            ctv.setRootIndex(self.__projectFileSystemModel.index(path))
            ctv.resizeColumnToContents(0)
        elif path == self.__packageInChrootDir:
            # Set the current index of the QTreeView to the package directory
            # so it appears unfolded
            ctv.setCurrentIndex(self.__projectFileSystemModel.index(path))
            ctv.resizeColumnToContents(0)

    @popupOnException
    def on_addFileButton_clicked(self):
        fileNames, _selectedFilter = QFileDialog.getOpenFileNames(self.mainWindow,
                                                                  u"Select file to add")
        for fileName in fileNames:
            self.manager.addFileToPackage(self.__project, self.__package, fileName)

    @popupOnException
    def on_deleteFileButton_clicked(self):
        currentIndex = self.mainWindow.fileTableView.currentIndex()
        if currentIndex.isValid():
            fileName = self.__oscWcModel.fileName(currentIndex)
            result = QMessageBox.question(self.mainWindow,
                                          "Are you sure ?",
                                          "Are you sure you want to delete %s file ?"
                                            % fileName,
                                          buttons=QMessageBox.Yes | QMessageBox.No,
                                          defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            self.manager.deleteFileFromPackage(self.__project, self.__package, fileName)

    @popupOnException
    def on_chrootTreeView_activated(self, index):
        """
        When user double-clicks on an item, open it with default application.
        """
        filePath = index.model().filePath(index)
        self.manager.openFile(filePath)

    @popupOnException
    def on_chrootTreeView_clicked(self, index):
        """
        When user clicks on an item, display the complete path
        of this item under the widget.
        """
        filePath = index.model().filePath(index)
        self.mainWindow.chrootPathLineEdit.setText(filePath)

    @popupOnException
    def on_fileTableView_activated(self, index):
        fileName = self.__oscWcModel.fileName(index)
        filePath = joinPath(self.__packageDir, fileName)
        self.manager.openFile(filePath)
