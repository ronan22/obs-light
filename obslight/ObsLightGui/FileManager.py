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

from PackageSourceFileManager import PackageSourceFileManager
from ChrootFileManager import ChrootFileManager

class FileManager(QObject, ObsLightGuiObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)

        self.__chrootFileManager = PackageSourceFileManager(gui, self.manager)
        self.__packageSourceFileManager = ChrootFileManager(gui, self.manager)

        self.__project = None
        self.__package = None

#---------------------------------------------------------------------------------------------------
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

        self.__chrootFileManager.setCurrentProjectAndPackage(project, package)
        self.__packageSourceFileManager.setCurrentProjectAndPackage(project, package)

        self.refresh()

    def refresh(self):
        self.__chrootFileManager.refresh()
        self.__packageSourceFileManager.refresh()



#    def refreshPackageSourceFile(self):
#        # --- working copy view ---
#        if self.__project is not None and self.__package is not None:
#            path = self.manager.getPackageParameter(self.__project,
#                                                    self.__package,
#                                                    parameter="packageSourceDirectory")
#
#            self.__packageDir = path
#            self.__oscWcModel = PackageSourceFileManager(self.manager,
#                                                         self.__project,
#                                                         self.__package)
#        else:
#            self.__oscWcModel = None
#        self.mainWindow.fileTableView.setModel(self.__oscWcModel)
#        self.mainWindow.fileTableView.resizeColumnToContents(1)


