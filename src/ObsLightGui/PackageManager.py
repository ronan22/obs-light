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

from PySide.QtCore import QObject, QThreadPool, Qt
from PySide.QtGui import QInputDialog, QProgressDialog, QPushButton, QTableView

from PackageModel import PackageModel
from ObsLightGui.FileManager import FileManager
from Utils import popupOnException, ProgressRunnable

class PackageManager(QObject):
    '''
    Manages the package list widget and package-related buttons
    of the main window.
    '''

    __gui = None
    __obsLightManager = None
    __project = None
    __model = None
    __fileManager = None
    __progress = None
    
    __packageTableView = None
    __newPackageButton = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileManager = FileManager(self.__gui)
        self.__packageTableView = gui.getMainWindow().findChild(QTableView,
                                                                  "packageTableView")
        self.__packageTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__packageTableView.activated.connect(self.on_packageIndex_clicked)
        self.__newPackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                "newPackageButton")
        self.__newPackageButton.clicked.connect(self.on_newPackageButton_clicked)
        self.__deletePackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                   "deletePackageButton")
        self.__deletePackageButton.clicked.connect(self.on_deletePackageButton_clicked)
        self.__progress = QProgressDialog(gui.getMainWindow())
        
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
        
    def on_packageIndex_clicked(self, index):
        if index.isValid():
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        
    def currentPackage(self):
        index = self.__packageTableView.currentIndex()
        if index.isValid():
            row = index.row()
            packageName = self.__model.data(self.__model.createIndex(row,
                                                                 PackageModel.PackageNameColumn))
            return packageName
        else:
            return None

    @popupOnException
    def on_newPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        packageName, accepted = QInputDialog.getText(self.__gui.getMainWindow(),
                                                     u"Choose package name...",
                                                     u"Package name (must exist on server):")
        if accepted:
            self.__progress.setLabelText("Adding package")
            self.__progress.setMinimumDuration(500)
            self.__progress.setWindowModality(Qt.WindowModal)
            # make the progress "infinite"
            self.__progress.setRange(0, 0)
            self.__progress.show()
            runnable = ProgressRunnable(self.__model.addPackage, packageName)
            runnable.setProgressDialog(self.__progress)
            runnable.setErrorCallback(self.__gui.obsLightErrorCallback)
            QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return
        row = self.__packageTableView.currentIndex().row()
        packageName = self.__model.data(self.__model.createIndex(row,
                                                                 PackageModel.PackageNameColumn))
        if packageName is not None and len(packageName) > 0:
            self.__model.removePackage(packageName)
