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

from PySide.QtCore import QObject, QThreadPool
from PySide.QtGui import QLabel, QInputDialog, QPushButton, QTableView, QWidget
from PySide.QtGui import QListWidget, QMenu, QMessageBox

from PackageModel import PackageModel
from ObsLightGui.FileManager import FileManager
from Utils import popupOnException, ProgressRunnable2

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
    __importPackageButton = None
    __deletePackageButton = None
    __importPackageSourceButton = None
    __makePatchButton = None
    __addAndCommitButton = None

    __packageSelectionDialog = None
    __packagesListWidget = None

    __menu = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileManager = FileManager(self.__gui)
        self.__packageWidget = gui.getMainWindow().findChild(QWidget, u"packageWidget")
        self.__packageTableView = gui.getMainWindow().findChild(QTableView,
                                                                u"packageTableView")
        self.__packageTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__packageTableView.activated.connect(self.on_packageIndex_clicked)
        self.__importPackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                u"importPackageButton")
        self.__importPackageButton.clicked.connect(self.on_newPackageButton_clicked)
        self.__deletePackageButton = gui.getMainWindow().findChild(QPushButton,
                                                                   u"deletePackageButton")
        self.__deletePackageButton.clicked.connect(self.on_deletePackageButton_clicked)
        self.__importPackageSourceButton = gui.getMainWindow().findChild(QPushButton,
                                                                         "importRpmButton")
        self.__importPackageSourceButton.clicked.connect(self.on_importRpmButton_clicked)
        self.__makePatchButton = gui.getMainWindow().findChild(QPushButton,
                                                               u"generatePatchButton")
        self.__makePatchButton.clicked.connect(self.on_makePatchButton_clicked)
        self.__addAndCommitButton = gui.getMainWindow().findChild(QPushButton,
                                                                  u"addAndCommitButton")
        self.__addAndCommitButton.clicked.connect(self.on_addAndCommitButton_clicked)
        self.__packageNameLabel = gui.getMainWindow().findChild(QLabel, u"packageNameLabelValue")
        self.__packageTitleLabel = gui.getMainWindow().findChild(QLabel, u"packageTitleLabel")
        self.__packageDescriptionLabel = gui.getMainWindow().findChild(QLabel,
                                                                       u"packageDescriptionLabel")
        self.__packageSelectionDialog = self.__gui.loadWindow("obsPackageSelector.ui")
        self.__packageSelectionDialog.accepted.connect(self.on_packageSelectionDialog_accepted)
        self.__packagesListWidget = self.__packageSelectionDialog.findChild(QListWidget,
                                                                            "packagesListWidget")
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
        if projectName != self.__project:
            self.__project = projectName
            self.__localModel = PackageModel(self.__obsLightManager, projectName)
            self.__packageTableView.setModel(self.__localModel)
            self.__packageWidget.setEnabled(self.__project is not None)
        if self.currentPackage() is not None:
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        else:
            self.__fileManager.setCurrentPackage(None, None)
        self.refresh()

    def on_packageIndex_clicked(self, index):
        if index.isValid():
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        self.refresh()

    def refresh(self):
        self.__fileManager.refresh()
        self.updateLabels()

    def updateLabels(self):
        package = self.currentPackage()
        project = self.getCurrentProject()
        if package is not None:
            self.__packageNameLabel.setText(package)
            packageTitle = self.__obsLightManager.getPackageParameter(project, package,
                                                                      u"packageTitle")
            description = self.__obsLightManager.getPackageParameter(project, package,
                                                                     u"description")
            self.__packageTitleLabel.setText(packageTitle)
            self.__packageDescriptionLabel.setText(description)
        else:
            self.__packageNameLabel.setText(u"No package selected")
            self.__packageTitleLabel.setText(u"")
            self.__packageDescriptionLabel.setText(u"")


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

    def selectedPackages(self):
        '''
        Get the list of currently selected packages. If no package selected,
        returns an empty list (not None).
        '''
        indices = self.__packageTableView.selectedIndexes()
        packages = set()
        for index in indices:
            if index.isValid():
                row = index.row()
                packageNameIndex = self.__localModel.createIndex(row,
                                                                 PackageModel.PackageNameColumn)
                packageName = self.__localModel.data(packageNameIndex)
                packages.add(packageName)
        return list(packages)

    def getPackageListFromServer(self):
        if self.getCurrentProject() is None:
            return list()
        server = self.__obsLightManager.getProjectParameter(self.getCurrentProject(),
                                                            "obsServer")
        prjObsName = self.__obsLightManager.getProjectParameter(self.getCurrentProject(),
                                                                "projectObsName")
        packageList = self.__obsLightManager.getObsProjectPackageList(server,
                                                                      prjObsName)
        return packageList

    def showPackageSelectionDialog(self, packageList):
        if packageList is None:
            return
        self.__packagesListWidget.clear()
        self.__packageSelectionDialog.show()
        self.__packagesListWidget.addItems(packageList)

    @popupOnException
    def on_newPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        runnable = ProgressRunnable2()
        progress = self.__gui.getInfiniteProgressDialog()
        runnable.setProgressDialog(progress)
        runnable.setDialogMessage("Loading available packages list")
        runnable.setRunMethod(self.getPackageListFromServer)
        runnable.finished[object].connect(self.showPackageSelectionDialog)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)
#        packageList = self.getPackageListFromServer()
#        self.showPackageSelectionDialog(packageList)

    class __AddPackages(ProgressRunnable2):
        packageList = None
        model = None

        def __init__(self, packageList, model, progress):
            ProgressRunnable2.__init__(self)
            self.packageList = packageList
            self.model = model
            self.setProgressDialog(progress)

        def run(self):
            self.setMax(len(self.packageList))
            self.setDialogMessage(u"Adding packages...")
            for package in self.packageList:
                try:
                    self.model.addPackage(package)
                except BaseException as e:
                    self.hasCaughtException(e)
                finally:
                    self.hasProgressed()
            self.hasFinished()

    def on_packageSelectionDialog_accepted(self):
        items = self.__packagesListWidget.selectedItems()
        packages = set()
        for item in items:
            packageName = item.text()
            packages.add(packageName)
        progress = self.__gui.getProgressDialog()
        progress.setValue(0)
        runnable = PackageManager.__AddPackages(packages,
                                                self.__localModel,
                                                progress)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        #self.__fileManager.setCurrentPackage(None, None)
        QThreadPool.globalInstance().start(runnable)

    class __RemovePackages(ProgressRunnable2):
        packageList = None
        model = None

        def __init__(self, packageList, model, progress):
            ProgressRunnable2.__init__(self)
            self.packageList = packageList
            self.model = model
            self.setProgressDialog(progress)

        def run(self):
            self.setMax(len(self.packageList))
            self.setDialogMessage(u"Deleting packages...")
            for package in self.packageList:
                try:
                    self.model.removePackage(package)
                except BaseException as e:
                    self.hasCaughtException(e)
                finally:
                    self.hasProgressed()
            self.hasFinished()

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return
        packagesNames = self.selectedPackages()
        progress = None
        if len(packagesNames) < 1:
            return
        result = QMessageBox.question(self.__gui.getMainWindow(),
                                      "Are you sure ?",
                                      "Are you sure you want to remove %d packages ?"
                                        % len(packagesNames),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        # This is to avoid a bug happening with libglib2.0 < 2.29.92
        # "Assertion `req == dpy->xcb->pending_requests' failed"
        # that crashed the whole application if calling dialog before
        # it is visible.
        if len(packagesNames) > 100:
            progress = self.__gui.getProgressDialog()
            progress.setValue(0)
        runnable = PackageManager.__RemovePackages(packagesNames,
                                                   self.__localModel,
                                                   progress)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        self.__fileManager.setCurrentPackage(None, None)
        QThreadPool.globalInstance().start(runnable)

    class __AddPackageSourceInChRoot(ProgressRunnable2):
        project = None
        packageList = None
        manager = None

        def __init__(self, project, packageList, manager, progress):
            ProgressRunnable2.__init__(self)
            self.project = project
            self.packageList = packageList
            self.manager = manager
            self.setProgressDialog(progress)

        def run(self):
            self.setMax(len(self.packageList))
            for package in self.packageList:
                try:
                    self.setDialogMessage(u"Importing %s source in chroot" % package)
                    self.manager.addPackageSourceInChRoot(self.project, package)
                except BaseException as e:
                    self.hasCaughtException(e)
                finally:
                    self.hasProgressed()
            self.hasFinished()

    @popupOnException
    def on_importRpmButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return
        progress = self.__gui.getProgressDialog()
        progress.setValue(0)
        runnable = PackageManager.__AddPackageSourceInChRoot(projectName,
                                                             packagesNames,
                                                             self.__obsLightManager,
                                                             progress)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

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
            progress = self.__gui.getInfiniteProgressDialog()
            progress.setLabelText(u"Creating patch")
            progress.show()
            runnable = ProgressRunnable2()
            runnable.setRunMethod(self.__obsLightManager.makePatch,
                                  project,
                                  package,
                                  patchName)
            runnable.setProgressDialog(progress)
            runnable.caughtException.connect(self.__gui.popupErrorCallback)
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
            progress = self.__gui.getInfiniteProgressDialog()
            progress.setLabelText(u"Committing changes")
            progress.show()
            runnable = ProgressRunnable2()
            runnable.setRunMethod(self.__obsLightManager.addAndCommitChanges,
                                  project,
                                  package,
                                  message)
            runnable.setProgressDialog(progress)
            runnable.caughtException.connect(self.__gui.popupErrorCallback)
            QThreadPool.globalInstance().start(runnable)

    def on_contextMenu_requested(self, point):
        self.__menu = QMenu(u"Package", self.__packageWidget)
        self.__menu.addAction(u"toto")
        self.__menu.addSeparator()
        self.__menu.addAction(u"tata")
        destPoint = self.__packageWidget.mapToParent(point)
        self.__menu.popup(destPoint)
