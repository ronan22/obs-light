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
Created on 4 nov. 2011

@author: Florent Vennetier
'''

from os.path import join as joinPath

from PySide.QtCore import QObject
from PySide.QtGui import QFileDialog, QFileSystemModel, QMessageBox, QPushButton
from PySide.QtGui import QTabWidget, QTableView, QTreeView

from ObsLight.ObsLightTools import isNonEmptyString
from Utils import popupOnException

from OscWorkingCopyModel import OscWorkingCopyModel

class FileManager(QObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    __gui = None
    __chrootModel = None
    __oscWcModel = None
    __obsLightManager = None
    __project = None
    __package = None
    __packageDir = None
    __packageInChrootDir = None
    __chrootPath = None
    __fileTableView = None
    __chrootTreeView = None
    __packageTabWidget = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileTableView = gui.getMainWindow().findChild(QTableView, u"fileTableView")
        self.__fileTableView.doubleClicked.connect(self.on_fileTableView_activated)
        self.__chrootTreeView = gui.getMainWindow().findChild(QTreeView, u"chrootTreeView")
        self.__chrootTreeView.doubleClicked.connect(self.on_chrootTreeView_activated)
        self.__packageTabWidget = gui.getMainWindow().findChild(QTabWidget, u"packageTabWidget")
        addFileButton = gui.getMainWindow().findChild(QPushButton, u"addFileButton")
        addFileButton.clicked.connect(self.on_addFileButton_clicked)
        deleteFileButton = gui.getMainWindow().findChild(QPushButton, u"deleteFileButton")
        deleteFileButton.clicked.connect(self.on_deleteFileButton_clicked)

    def setCurrentPackage(self, project, package):
        '''
        Set the package that you want this class to operate on.
        None is valid.
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

            if self.__obsLightManager.isChRootInit(self.__project):
                self.__chrootTreeView.setEnabled(True)
                pathInChRoot = self.__obsLightManager.getPackageDirectoryInChRoot(self.__project,
                                                                                  self.__package)
                chrootPath = self.__obsLightManager.getChRootPath(self.__project)
                self.__chrootModel.directoryLoaded.connect(self.on_chrootPath_loaded)
                self.__packageInChrootDir = chrootPath
                if pathInChRoot is not None:
                    self.__packageInChrootDir += pathInChRoot
                self.__chrootPath = chrootPath
                self.__chrootModel.setRootPath(self.__chrootPath)
                if self.__chrootPath != self.__packageInChrootDir:
                    self.__chrootModel.setRootPath(self.__packageInChrootDir)
            else:
                self.__chrootTreeView.setEnabled(False)
            self.__packageTabWidget.setEnabled(True)
        else:
            self.__packageTabWidget.setEnabled(False)
        self.__chrootTreeView.setModel(self.__chrootModel)

        # --- working copy view ---
        if self.__project is not None and self.__package is not None:
            path = self.__obsLightManager.getPackageDirectory(self.__project, self.__package)
            self.__packageDir = path
            self.__oscWcModel = OscWorkingCopyModel(self.__obsLightManager,
                                                    self.__project,
                                                    self.__package)
        else:
            self.__oscWcModel = None
        self.__fileTableView.setModel(self.__oscWcModel)
        self.__fileTableView.resizeColumnToContents(0)

    def on_chrootPath_loaded(self, path):
        if path == self.__chrootPath:
            self.__chrootTreeView.setRootIndex(self.__chrootModel.index(path))
            self.__chrootTreeView.resizeColumnToContents(0)
        elif path == self.__packageInChrootDir:
            self.__chrootTreeView.setCurrentIndex(self.__chrootModel.index(path))
            self.__chrootTreeView.resizeColumnToContents(0)

    @popupOnException
    def on_addFileButton_clicked(self):
        fileNames, _selectedFilter = QFileDialog.getOpenFileNames(self.__gui.getMainWindow(),
                                                                  u"Select file to add")
        for fileName in fileNames:
            self.__obsLightManager.addFileToPackage(self.__project, self.__package, fileName)

    @popupOnException
    def on_deleteFileButton_clicked(self):
        currentIndex = self.__fileTableView.currentIndex()
        if currentIndex.isValid():
            fileName = self.__oscWcModel.fileName(currentIndex)
            result = QMessageBox.question(self.__gui.getMainWindow(),
                                          "Are you sure ?",
                                          "Are you sure you want to delete %s file ?"
                                            % fileName,
                                          buttons=QMessageBox.Yes | QMessageBox.No,
                                          defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            self.__obsLightManager.deleteFileFromPackage(self.__project, self.__package, fileName)

    @popupOnException
    def on_chrootTreeView_activated(self, index):
        filePath = index.model().filePath(index)
        self.__obsLightManager.openFile(filePath)

    @popupOnException
    def on_fileTableView_activated(self, index):
        fileName = self.__oscWcModel.fileName(index)
        filePath = joinPath(self.__packageDir, fileName)
        self.__obsLightManager.openFile(filePath)
