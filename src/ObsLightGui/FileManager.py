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
from PySide.QtGui import QFileSystemModel, QTreeView

class FileManager(QObject):
    '''
    Manage the file list widget and file-related buttons of the main window.
    '''

    __gui = None
    __model = None
    __obsLightManager = None
    __project = None
    __package = None
    __packageDir = None
    __fileTreeView = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileTreeView = gui.getMainWindow().findChild(QTreeView, "fileTreeView")

    def setCurrentPackage(self, project, package):
        '''
        Set the package that you want this class to operate on.
        None is valid.
        '''
        if project is not None and len(project) < 1:
            project = None
        if package is not None and len(package) < 1:
            package = None
        self.__project = project
        self.__package = package
        self.__model = QFileSystemModel()
        if self.__project is not None and self.__package is not None:
            path = self.__obsLightManager.getPackageDirectory(self.__project, self.__package)
            self.__model.directoryLoaded.connect(self.on_path_loaded)
            self.__packageDir = path
            self.__model.setRootPath(path)
        self.__fileTreeView.setModel(self.__model)
        
    def on_path_loaded(self, path):
        if path == self.__packageDir:
            self.__fileTreeView.setRootIndex(self.__model.index(path))
