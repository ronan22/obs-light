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
Created on 6 Sept. 2012

@author: Roanan Le Martret
'''
import os

from PySide.QtGui import QFileDialog, QFileSystemModel, QMessageBox

from Utils import popupOnException

from FileManagerModel import FileManagerModel


class PackageSourceFileManager(FileManagerModel):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    def __init__(self, gui, manager):
        FileManagerModel.__init__(self, gui, manager)

        self.setTreeView(self.mainWindow.packageTreeView)
        self.setLineEdit(self.mainWindow.packagePathLineEdit)

        self._init_connect()

#        #File
#        self.mainWindow.addFileButton.clicked.connect(self.on_addFileButton_clicked)
#        self.mainWindow.deleteFileButton.clicked.connect(self.on_deleteFileButton_clicked)

#---------------------------------------------------------------------------------------------------        
    def _initBaseDir(self):

        self._baseDirPath = self.manager.getPackageParameter(self._project,
                                                             self._package,
                                                             parameter="packageSourceDirectory")

        self._curentDirPath = self._baseDirPath

#    @popupOnException
#    def on_addFileButton_clicked(self):
#        fileNames, _selectedFilter = QFileDialog.getOpenFileNames(self.mainWindow,
#                                                                  u"Select file to add")
#        for fileName in fileNames:
#            self.manager.addFileToPackage(self._project, self._package, fileName)
#        self.refresh()

    @popupOnException
    def on_deleteFileButton_clicked(self):
        currentIndex = self.getTreeView().currentIndex()
        currentIndex = self.getTreeView().currentIndex()
        if currentIndex.isValid():
            fileName = os.path.basename(currentIndex.model().filePath(currentIndex))
            result = QMessageBox.question(self.mainWindow,
                                          "Are you sure ?",
                                          "Are you sure you want to delete %s file ?"
                                            % fileName,
                                          buttons=QMessageBox.Yes | QMessageBox.No,
                                          defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return

        self.manager.deleteFileFromPackage(self._project, self._package, fileName)
        self.on_TreeView_clicked(self.getTreeView().rootIndex ())
        self.refresh()


