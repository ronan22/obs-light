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
from PySide.QtGui import QLabel, QInputDialog, QProgressDialog, QPushButton, QTableView, QWidget
from PySide.QtGui import QMenu

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
    __localModel = None
    __fileManager = None

    __packageWidget = None
    __packageTableView = None
    __packageNameLabel = None
    __packageTitleLabel = None
    __packageDescriptionLabel = None
    __newPackageButton = None
    __deletePackageButton = None
    __makePatchButton = None
    __addAndCommitButton = None

    __menu = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileManager = FileManager(self.__gui)
        self.__packageWidget = gui.getMainWindow().findChild(QWidget, "packageWidget")
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
        self.__makePatchButton = gui.getMainWindow().findChild(QPushButton,
                                                               "generatePatchButton")
        self.__makePatchButton.clicked.connect(self.on_makePatchButton_clicked)
        self.__addAndCommitButton = gui.getMainWindow().findChild(QPushButton,
                                                                  "addAndCommitButton")
        self.__addAndCommitButton.clicked.connect(self.on_addAndCommitButton_clicked)
        self.__packageNameLabel = gui.getMainWindow().findChild(QLabel, "packageNameLabelValue")
        self.__packageTitleLabel = gui.getMainWindow().findChild(QLabel, "packageTitleLabel")
        self.__packageDescriptionLabel = gui.getMainWindow().findChild(QLabel,
                                                                       "packageDescriptionLabel")
        #self.__packageWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        #self.__packageWidget.customContextMenuRequested.connect(self.on_contextMenu_requested)

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
        self.__localModel = PackageModel(self.__obsLightManager, projectName)
        self.__packageTableView.setModel(self.__localModel)
        self.__packageWidget.setEnabled(self.__project is not None)
        if self.currentPackage() is not None:
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        else:
            self.__fileManager.setCurrentPackage(None, None)
        self.updateLabels()

    def on_packageIndex_clicked(self, index):
        if index.isValid():
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        self.updateLabels()

    def updateLabels(self):
        package = self.currentPackage()
        project = self.getCurrentProject()
        if package is not None:
            self.__packageNameLabel.setText(package)
            packageTitle = self.__obsLightManager.getPackageParameter(project, package,
                                                                      "packageTitle")
            description = self.__obsLightManager.getPackageParameter(project, package,
                                                                     "description")
            self.__packageTitleLabel.setText(packageTitle)
            self.__packageDescriptionLabel.setText(description)
        else:
            self.__packageNameLabel.setText("No package selected")
            self.__packageTitleLabel.setText("")
            self.__packageDescriptionLabel.setText("")


    def currentPackage(self):
        '''
        Get the name of the package that is currently selected in the
        package list. May return None.
        '''
        index = self.__packageTableView.currentIndex()
        if index.isValid():
            row = index.row()
            packageName = self.__localModel.data(self.__localModel.createIndex(row,
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
            progress = self.__gui.getProgressDialog()
            progress.setLabelText("Adding package")
            progress.show()
            runnable = ProgressRunnable(self.__localModel.addPackage, packageName)
            runnable.setProgressDialog(progress)
            runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
            runnable.finished.connect(self.updateLabels)
            QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return
        row = self.__packageTableView.currentIndex().row()
        packageName = self.__localModel.data(self.__localModel.createIndex(row,
                                                                           PackageModel.PackageNameColumn))
        if packageName is not None and len(packageName) > 0:
            self.__localModel.removePackage(packageName)
            self.__fileManager.setCurrentPackage(None, None)

    @popupOnException
    def on_makePatchButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        patchName, accepted = QInputDialog.getText(self.__gui.getMainWindow(),
                                                   u"Choose patch name...",
                                                   u"Patch name:")
        if accepted:
            progress = self.__gui.getProgressDialog()
            progress.setLabelText("Creating patch")
            progress.show()
            runnable = ProgressRunnable(self.__obsLightManager.makePatch,
                                        project,
                                        package,
                                        patchName)
            runnable.setProgressDialog(progress)
            runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
            QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_addAndCommitButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        message, accepted = QInputDialog.getText(self.__gui.getMainWindow(),
                                                 u"Enter commit message...",
                                                 u"Commit message:")
        if accepted:
            progress = self.__gui.getProgressDialog()
            progress.setLabelText("Committing changes")
            progress.show()
            runnable = ProgressRunnable(self.__obsLightManager.addAndCommitChanges,
                                        project,
                                        package,
                                        message)
            runnable.setProgressDialog(progress)
            runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
            QThreadPool.globalInstance().start(runnable)

    def on_contextMenu_requested(self, point):
        self.__menu = QMenu("Package", self.__packageWidget)
        self.__menu.addAction("toto")
        self.__menu.addSeparator()
        self.__menu.addAction("tata")
        destPoint = self.__packageWidget.mapToParent(point)
        self.__menu.popup(destPoint)
