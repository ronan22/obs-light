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

from PySide.QtGui import QFileDialog, QFileSystemModel, QMessageBox

from Utils import popupOnException

from FileManagerModel import FileManagerModel

class ChrootFileManager(FileManagerModel):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    def __init__(self, gui, manager):
        FileManagerModel.__init__(self, gui, manager)

        self.setTreeView(self.mainWindow.chrootTreeView)
        self.setLineEdit(self.mainWindow.chrootPathLineEdit)

        self._init_connect()

    def _isInit(self):
        if self._project is not None:
            return self.manager.isChRootInit(self._project)
        else:
            return False

    def _initBaseDir(self):
        pathInChRoot = self.manager.getPackageParameter(self._project,
                                                        self._package,
                                                        parameter="fsPackageDirectory")

        self._baseDirPath = self.manager.getChRootPath(self._project)

        if pathInChRoot is not None:
            self._curentDirPath = self._baseDirPath + pathInChRoot
