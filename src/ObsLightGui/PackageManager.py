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
Created on 2 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject
from PySide.QtGui import QInputDialog, QPushButton, QTableView

from PackageModel import PackageModel
from Utils import popupOnException

class PackageManager(QObject):
    '''
    Manages the package list widget and package-related buttons
    of the main window.
    '''

    __gui = None
    __obsLightManager = None
    __project = None
    __model = None
    
    __packageTableView = None
    __newPackageButton = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__packageTableView = gui.getMainWindow().findChild(QTableView,
                                                                  "packageTableView")
        self.__newPackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                "newPackageButton")
        self.__newPackageButton.clicked.connect(self.on_newPackageButton_clicked)
        self.__deletePackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                   "deletePackageButton")
        self.__deletePackageButton.clicked.connect(self.on_deletePackageButton_clicked)
        
    def getCurrentProject(self):
        return self.__project
    
    def setCurrentProject(self, projectName):
        '''
        Set the current active project. It will refresh package list.
        Passing None is valid.
        '''
        if projectName is not None and len(projectName) < 1:
            projectName = None
        self.__project = projectName
        self.__model = PackageModel(self.__obsLightManager, projectName)
        self.__packageTableView.setModel(self.__model)

    @popupOnException
    def on_newPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        packageName, accepted = QInputDialog.getText(self.__gui.getMainWindow(),
                                                     u"Choose package name...",
                                                     u"Package name (must exist on server):")
        if accepted:
            self.__model.addPackage(packageName)

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return
        row = self.__packageTableView.currentRow()
        packageName = self.__model.item(row, PackageModel.PackageNameColumn).text()
        if packageName is not None and len(packageName) > 0:
            self.__model.removePackage(packageName)
