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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 4 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject
from PySide.QtGui import QFileDialog, QFileSystemModel, QPushButton, QTabWidget, QTreeView
from PySide.QtGui import QMessageBox

from ObsLight.ObsLightTools import isNonEmptyString
from Utils import popupOnException

class FileManager(QObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    __gui = None
    __localFsModel = None
    __chrootModel = None
    __obsLightManager = None
    __project = None
    __package = None
    __packageDir = None
    __packageInChrootDir = None
    __chrootPath = None
    __fileTreeView = None
    __chrootTreeView = None
    __packageTabWidget = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileTreeView = gui.getMainWindow().findChild(QTreeView, u"fileTreeView")
        self.__chrootTreeView = gui.getMainWindow().findChild(QTreeView, u"chrootTreeView")
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
        self.__localFsModel = QFileSystemModel()
        self.__chrootModel = QFileSystemModel()
        if self.__project is not None and self.__package is not None:
            path = self.__obsLightManager.getPackageDirectory(self.__project, self.__package)
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
            self.__localFsModel.directoryLoaded.connect(self.on_path_loaded)
            self.__packageDir = path
            self.__localFsModel.setRootPath(path)
            self.__packageTabWidget.setEnabled(True)
        else:
            self.__packageTabWidget.setEnabled(False)
        self.__fileTreeView.setModel(self.__localFsModel)
        self.__chrootTreeView.setModel(self.__chrootModel)

    def on_path_loaded(self, path):
        if path == self.__packageDir:
            self.__fileTreeView.setRootIndex(self.__localFsModel.index(path))
            self.__fileTreeView.resizeColumnToContents(0)

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
        currentIndex = self.__fileTreeView.currentIndex()
        if currentIndex.isValid():
            fileName = self.__localFsModel.fileName(currentIndex)
            result = QMessageBox.question(self.__gui.getMainWindow(),
                                          "Are you sure ?",
                                          "Are you sure you want to delete %s file ?"
                                            % fileName,
                                          buttons=QMessageBox.Yes | QMessageBox.No,
                                          defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            self.__obsLightManager.deleteFileFromPackage(self.__project, self.__package, fileName)
