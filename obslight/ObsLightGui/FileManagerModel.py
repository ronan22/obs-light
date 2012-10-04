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
Created on 6 sept. 2011

@author: Ronan Le Martret

'''


from PySide.QtCore import QObject

from Utils import popupOnException
from ObsLightGuiObject import ObsLightGuiObject

from PySide.QtGui import  QFileSystemModel


class FileManagerModel(QObject, ObsLightGuiObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    def __init__(self, gui, manager):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)

        self.__treeView = None
        self.__lineEdit = None

        self._project = None
        self._package = None

        self._baseDirPath = "/"
        self._curentDirPath = "/"

        self.__systemModel = None

    def setTreeView(self, treeView):
        self.__treeView = treeView

    def setLineEdit(self, lineEdit):
        self.__lineEdit = lineEdit

    def getTreeView(self):
        return self.__treeView

    def _init_connect(self):
        if self.__treeView is not None:
            self.__treeView.doubleClicked.connect(self.on_TreeView_activated)
            self.__treeView.clicked.connect(self.on_TreeView_clicked)
            self.__treeView.expanded.connect(self.on_TreeView_expanded)
            self.__treeView.collapsed.connect(self.on_TreeView_expanded)

    def _isInit(self):
        return True

    def setCurrentProjectAndPackage(self, project, package):
        self._project = project
        self._package = package
#---------------------------------------------------------------------------------------------------        
    @popupOnException
    def on_TreeView_activated(self, index):
        """
        When user double-clicks on an item, open it with default application.
        """
        filePath = index.model().filePath(index)
        self.manager.openFile(filePath)

    @popupOnException
    def on_TreeView_clicked(self, index):
        """
        When user clicks on an item, display the complete path
        of this item under the widget.
        """
        filePath = index.model().filePath(index)
        if self.__lineEdit is not None:
            self.__lineEdit.setText(filePath)

    @popupOnException
    def on_TreeView_expanded(self, _index):
        if self.__treeView is not None:
            self.__treeView.resizeColumnToContents(0)

        self._baseDirPath = None
        self._curentDirPath = None

    def _initBaseDir(self):
        pass

#---------------------------------------------------------------------------------------------------
    def refresh(self):
        # --- view ---------
        self.__systemModel = QFileSystemModel()
        if self._project is not None and self._package is not None and self.__treeView is not None:
            if self._isInit():
                self.__treeView.setEnabled(True)

                # Qt 4.6 do not know "directoryLoaded"
                if hasattr(self.__systemModel, "directoryLoaded"):
                    self.__systemModel.directoryLoaded.connect(self.on_path_loaded)

                self._initBaseDir()

                self.__systemModel.setRootPath(self._baseDirPath)

                if self._baseDirPath != self._curentDirPath:
                    self.__systemModel.setRootPath(self._curentDirPath)

            else:
                self.__treeView.setEnabled(False)
            self.mainWindow.packageTabWidget.setEnabled(True)
        else:
            self.mainWindow.packageTabWidget.setEnabled(False)

        if self.__treeView is not None:
            self.__treeView.setModel(self.__systemModel)

        # Qt 4.6 do not know "directoryLoaded"
        if not hasattr(self.__systemModel, "directoryLoaded"):
            self.on_path_loaded(self.__baseDirPath)
            self.on_path_loaded(self.__curentDirPath)

    def on_path_loaded(self, path):
        """
        Called when the QFileSystem model loads paths.
        """
        if self.__treeView is not None:
            if path == self._baseDirPath:
                # Set the root index of the QTreeView to the root directory of
                # the project file system, so user does not see outside
                if self.__systemModel is not None:
                    self.__treeView.setRootIndex(self.__systemModel.index(path))

            elif path == self._curentDirPath:
                # Set the current index of the QTreeView to the package directory
                # so it appears unfolded
                if self.__systemModel is not None:
                    self.__treeView.setCurrentIndex(self.__systemModel.index(path))
            self.__treeView.resizeColumnToContents(0)

