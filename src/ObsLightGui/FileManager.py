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
from PySide.QtGui import QFileSystemModel, QTabWidget, QTreeView

class FileManager(QObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    __gui = None
    __localModel = None
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
        self.__fileTreeView = gui.getMainWindow().findChild(QTreeView, "fileTreeView")
        self.__chrootTreeView = gui.getMainWindow().findChild(QTreeView, "chrootTreeView")
        self.__packageTabWidget = gui.getMainWindow().findChild(QTabWidget, "packageTabWidget")

    def setCurrentPackage(self, project, package):
        '''
        Set the package that you want this class to operate on.
        None is valid.
        '''
        if project is not None and len(project) < 1:
            project = None
        if package is not None and len(package) < 1:
            package = None
        if project != self.__project or self.__chrootModel is None:
            self.__chrootModel = QFileSystemModel()
        self.__project = project
        self.__package = package
        self.__localModel = QFileSystemModel()
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
            self.__localModel.directoryLoaded.connect(self.on_path_loaded)
            self.__packageDir = path
            self.__localModel.setRootPath(path)
            self.__packageTabWidget.setEnabled(True)
        else:
            self.__packageTabWidget.setEnabled(False)
        self.__fileTreeView.setModel(self.__localModel)
        self.__chrootTreeView.setModel(self.__chrootModel)

    def on_path_loaded(self, path):
        if path == self.__packageDir:
            self.__fileTreeView.setRootIndex(self.__localModel.index(path))
            self.__fileTreeView.resizeColumnToContents(0)

    def on_chrootPath_loaded(self, path):
        if path == self.__chrootPath:
            self.__chrootTreeView.setRootIndex(self.__chrootModel.index(path))
            self.__chrootTreeView.resizeColumnToContents(0)
        elif path == self.__packageInChrootDir:
            self.__chrootTreeView.setCurrentIndex(self.__chrootModel.index(path))
            self.__chrootTreeView.resizeColumnToContents(0)
