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
        self.__chrootModel = None
        self.__oscWcModel = None
        self.__project = None
        self.__package = None
        self.__packageDir = None
        self.__packageInChrootDir = None
        self.__chrootPath = None

        self.mainWindow.fileTableView.doubleClicked.connect(self.on_fileTableView_activated)
        self.mainWindow.chrootTreeView.doubleClicked.connect(self.on_chrootTreeView_activated)
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
        self.__chrootModel = QFileSystemModel()
        if self.__project is not None and self.__package is not None:

            if self.manager.isChRootInit(self.__project):
                self.mainWindow.chrootTreeView.setEnabled(True)
                pathInChRoot = self.manager.getPackageParameter(self.__project,
                                                                self.__package,
                                                                parameter="fsPackageDirectory")
                chrootPath = self.manager.getChRootPath(self.__project)
                self.__chrootModel.directoryLoaded.connect(self.on_chrootPath_loaded)
                self.__packageInChrootDir = chrootPath
                if pathInChRoot is not None:
                    self.__packageInChrootDir += pathInChRoot
                self.__chrootPath = chrootPath
                self.__chrootModel.setRootPath(self.__chrootPath)
                if self.__chrootPath != self.__packageInChrootDir:
                    self.__chrootModel.setRootPath(self.__packageInChrootDir)
            else:
                self.mainWindow.chrootTreeView.setEnabled(False)
            self.mainWindow.packageTabWidget.setEnabled(True)
        else:
            self.mainWindow.packageTabWidget.setEnabled(False)
        self.mainWindow.chrootTreeView.setModel(self.__chrootModel)

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
        if path == self.__chrootPath:
            # Set the root index of the QTreeView to the root directory of
            # the project file system, so user does not see outside
            self.mainWindow.chrootTreeView.setRootIndex(self.__chrootModel.index(path))
            self.mainWindow.chrootTreeView.resizeColumnToContents(0)
        elif path == self.__packageInChrootDir:
            # Set the current index of the QTreeView to the package directory
            # so it appears unfolded
            self.mainWindow.chrootTreeView.setCurrentIndex(self.__chrootModel.index(path))
            self.mainWindow.chrootTreeView.resizeColumnToContents(0)

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
        filePath = index.model().filePath(index)
        self.manager.openFile(filePath)

    @popupOnException
    def on_fileTableView_activated(self, index):
        fileName = self.__oscWcModel.fileName(index)
        filePath = joinPath(self.__packageDir, fileName)
        self.manager.openFile(filePath)
