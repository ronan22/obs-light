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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 2 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QThreadPool, QRegExp
from PySide.QtGui import QLabel, QInputDialog, QPushButton, QTableView, QWidget
from PySide.QtGui import QLineEdit, QListWidget, QMessageBox, QRegExpValidator

from PackageModel import PackageModel
from ObsLightGui.FileManager import FileManager
from Utils import popupOnException, ProgressRunnable2, firstArgLast

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
    __rpmPrepButton = None
    __rpmBuildButton = None
    __rpmInstallButton = None
    __rpmBuildRpmButton = None
    __openTermButton = None
    __updateFilesButton = None
    __generatePatchButton = None
    __importPatchButton = None
    __deletePatchButton = None
    __modifyPatchButton = None
    __addAndCommitButton = None
    __refreshOscStatusButton = None
    __repairOscButton = None
    __packagePathLineEdit = None

    __packageSelectionDialog = None
    __packagesListWidget = None

    __menu = None

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__fileManager = FileManager(self.__gui)
        mainWindow = gui.getMainWindow()
        self.__packageWidget = mainWindow.findChild(QWidget,
                                                    u"packageWidget")
        self.__packageTableView = mainWindow.findChild(QTableView,
                                                       u"packageTableView")
        self.__packageTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__packageTableView.activated.connect(self.on_packageIndex_clicked)
        self.__importPackageButton = mainWindow.findChild(QPushButton,
                                                          u"importPackageButton")
        self.__importPackageButton.clicked.connect(self.on_newPackageButton_clicked)
        self.__deletePackageButton = mainWindow.findChild(QPushButton,
                                                          u"deletePackageButton")
        self.__deletePackageButton.clicked.connect(self.on_deletePackageButton_clicked)
        self.__rpmPrepButton = mainWindow.findChild(QPushButton,
                                                    u"rpmPrepButton")
        self.__rpmPrepButton.clicked.connect(self.on_rpmPrepButton_clicked)
        self.__rpmBuildButton = mainWindow.findChild(QPushButton,
                                                     u"rpmBuildButton")
        self.__rpmBuildButton.clicked.connect(self.on_rpmBuildButton_clicked)
        self.__rpmInstallButton = mainWindow.findChild(QPushButton,
                                                       u"rpmInstallButton")
        self.__rpmInstallButton.clicked.connect(self.on_rpmInstallButton_clicked)
        self.__rpmBuildRpmButton = mainWindow.findChild(QPushButton,
                                                        u"rpmBuildRpmButton")
        self.__rpmBuildRpmButton.clicked.connect(self.on_rpmBuildRpmButton_clicked)
        self.__openTermButton = mainWindow.findChild(QPushButton,
                                                     u"openTermButton")
        self.__openTermButton.clicked.connect(self.on_openTermButton_clicked)
        self.__updateFilesButton = mainWindow.findChild(QPushButton,
                                                        u"updateFilesButton")
        self.__updateFilesButton.clicked.connect(self.on_updateFilesButton_clicked)
        self.__generatePatchButton = mainWindow.findChild(QPushButton,
                                                          u"generatePatchButton")
        self.__generatePatchButton.clicked.connect(self.on_makePatchButton_clicked)
        self.__importPatchButton = mainWindow.findChild(QPushButton,
                                                        u"importPatchButton")
        self.__deletePatchButton = mainWindow.findChild(QPushButton,
                                                        u"deletePatchButton")
        self.__modifyPatchButton = mainWindow.findChild(QPushButton,
                                                        u"modifyPatchButton")
        self.__addAndCommitButton = mainWindow.findChild(QPushButton,
                                                         u"addAndCommitButton")
        self.__addAndCommitButton.clicked.connect(self.on_addAndCommitButton_clicked)
        self.__packageNameLabel = mainWindow.findChild(QLabel, u"packageNameLabelValue")
        self.__packageTitleLabel = mainWindow.findChild(QLabel, u"packageTitleLabel")
        self.__packageDescriptionLabel = mainWindow.findChild(QLabel,
                                                              u"packageDescriptionLabel")
        self.__packageSelectionDialog = self.__gui.loadWindow(u"obsPackageSelector.ui")
        self.__packageSelectionDialog.accepted.connect(self.on_packageSelectionDialog_accepted)
        self.__packagesListWidget = self.__packageSelectionDialog.findChild(QListWidget,
                                                                            u"packagesListWidget")
        self.__refreshOscStatusButton = mainWindow.findChild(QPushButton,
                                                             u"refreshOscStatusButton")
        self.__refreshOscStatusButton.clicked.connect(self.on_refreshOscStatusButton_clicked)
        self.__repairOscButton = mainWindow.findChild(QPushButton,
                                                      u"repairOscButton")
        self.__repairOscButton.clicked.connect(self.on_repairOscButton_clicked)
        self.__packagePathLineEdit = mainWindow.findChild(QLineEdit,
                                                          u"packagePathLineEdit")

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
        self.updateButtons()
        self.__packageTableView.resizeColumnToContents(PackageModel.ObsRevColumn)
        self.__packageTableView.resizeColumnToContents(PackageModel.OscRevColumn)

    def updateLabels(self):
        package = self.currentPackage()
        project = self.getCurrentProject()
        if package is not None:
            self.__packageNameLabel.setText(package)
            packageTitle = self.__obsLightManager.getPackageParameter(project,
                                                                      package,
                                                                      u"packageTitle")
            description = self.__obsLightManager.getPackageParameter(project,
                                                                     package,
                                                                     u"description")
            self.__packageTitleLabel.setText(packageTitle)
            self.__packageDescriptionLabel.setText(description)
            pkgDir = self.__obsLightManager.getPackageDirectory(project, package)
            self.__packagePathLineEdit.setText(pkgDir)
        else:
            self.__packageNameLabel.setText(u"No package selected")
            self.__packageTitleLabel.setText(u"")
            self.__packageDescriptionLabel.setText(u"")
            self.__packagePathLineEdit.setText("")

    def updateButtons(self):
        package = self.currentPackage()
        project = self.getCurrentProject()
        installed = (package is not None and
                     self.__obsLightManager.isInstalledInChRoot(project, package))
        self.__rpmBuildButton.setEnabled(installed)
        self.__rpmInstallButton.setEnabled(installed)
        self.__rpmBuildRpmButton.setEnabled(installed)
        self.__generatePatchButton.setEnabled(installed)

    def currentPackage(self):
        '''
        Get the name of the package that is currently selected in the
        package list. May return None.
        '''
        index = self.__packageTableView.currentIndex()
        if index.isValid():
            row = index.row()
            pkgNameIndex = self.__localModel.createIndex(row, PackageModel.NameColumn)
            packageName = self.__localModel.data(pkgNameIndex)
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
                                                                 PackageModel.NameColumn)
                packageName = self.__localModel.data(packageNameIndex)
                packages.add(packageName)
        return list(packages)

    def selectAllPackages(self):
        self.__packageTableView.selectAll()

    def getPackageListFromServer(self):
        if self.getCurrentProject() is None:
            return list()
        server = self.__obsLightManager.getProjectParameter(self.getCurrentProject(),
                                                            u"obsServer")
        prjObsName = self.__obsLightManager.getProjectParameter(self.getCurrentProject(),
                                                                u"projectObsName")
        packageList = self.__obsLightManager.getObsProjectPackageList(server,
                                                                      prjObsName)
        return packageList

    def showPackageSelectionDialog(self, packageList):
        if packageList is None:
            return
        self.__packagesListWidget.clear()
        self.__packageSelectionDialog.show()
        self.__packagesListWidget.addItems(packageList)

    def __mapOnSelectedPackages(self, method, initialMessage, loopMessage,
                                callback, *args, **kwargs):
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return
        elif len(packagesNames) < 2:
            progress = self.__gui.getInfiniteProgressDialog()
        else:
            progress = self.__gui.getProgressDialog()
            progress.setValue(0)
        runnable = ProgressRunnable2(progress)
        if initialMessage is not None:
            runnable.setDialogMessage(initialMessage)
        runnable.setFunctionToMap(method, packagesNames, loopMessage, *args, **kwargs)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        if callback is not None:
            runnable.finished.connect(callback)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_newPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Loading available packages list")
        runnable.setRunMethod(self.getPackageListFromServer)
        runnable.finished[object].connect(self.showPackageSelectionDialog)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def on_packageSelectionDialog_accepted(self):
        items = self.__packagesListWidget.selectedItems()
        packages = set()
        for item in items:
            packageName = item.text()
            packages.add(packageName)
        progress = None
        if len(packages) < 2:
            progress = self.__gui.getInfiniteProgressDialog()
        else:
            progress = self.__gui.getProgressDialog()
            progress.setValue(0)
        runnable = ProgressRunnable2(progress)
        runnable.setFunctionToMap(self.__localModel.addPackage,
                                  packages,
                                  message=u"Adding package %(arg)s")
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        #self.__fileManager.setCurrentPackage(None, None)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return

        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return
        result = QMessageBox.question(self.__gui.getMainWindow(),
                                      u"Are you sure ?",
                                      u"Are you sure you want to remove %d packages ?"
                                        % len(packagesNames),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        self.__mapOnSelectedPackages(self.__localModel.removePackage,
                                     u"Deleting packages...",
                                     None,
                                     None)
        self.__fileManager.setCurrentPackage(None, None)

    @popupOnException
    def on_rpmPrepButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        alreadyInstalled = list()
        for package in self.selectedPackages():
            if self.__obsLightManager.isInstalledInChRoot(self.__project, package):
                alreadyInstalled.append(package)
        if len(alreadyInstalled) > 0:
            questionString = u"The packages <b>%s" % unicode(alreadyInstalled[0])
            for package in alreadyInstalled[1:]:
                questionString += u", %s" % unicode(package)
            questionString += u"</b> are already present in the chroot, do you want to"
            questionString += u" overwrite them ?"
            result = QMessageBox.question(self.__gui.getMainWindow(),
                                          u"Overwrite ?",
                                          questionString,
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Yes)
            if result != QMessageBox.Yes:
                return
        self.__mapOnSelectedPackages(firstArgLast(self.__obsLightManager.addPackageSourceInChRoot),
                                     None,
                                     u"Importing %(arg)s source in chroot and executing %%prep",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmBuildButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.__obsLightManager.buildRpm),
                                     None,
                                     u"Executing %%build section of %(arg)s",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmInstallButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.__obsLightManager.installRpm),
                                     None,
                                     u"Executing %%install section of %(arg)s",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmBuildRpmButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.__obsLightManager.packageRpm),
                                     None,
                                     u"Packaging %(arg)s",
                                     None,
                                     projectName)

    @popupOnException
    def on_openTermButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        runnable = ProgressRunnable2()
        runnable.setRunMethod(self.__obsLightManager.openTerminal,
                              project,
                              package)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_updateFilesButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Updating files...")
        runnable.setRunMethod(self.__obsLightManager.updatePackage,
                              project,
                              package)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def __createPatch(self, patchName):
        project = self.getCurrentProject()
        package = self.currentPackage()
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Creating patch")
        runnable.setRunMethod(self.__obsLightManager.makePatch,
                              project,
                              package,
                              patchName)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_makePatchButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        dialog = QInputDialog(self.__gui.getMainWindow())
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText(u"Patch name:")
        dialog.setWindowTitle(u"Choose patch name...")
        le = dialog.findChildren(QLineEdit)
        if len(le) > 0:
            validator = QRegExpValidator(le[0])
            validator.setRegExp(QRegExp(u"\\S+"))
            le[0].setValidator(validator)
        dialog.textValueSelected.connect(self.__createPatch)
        dialog.show()

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
            runnable = ProgressRunnable2(progress)
            runnable.setDialogMessage(u"Committing changes")
            runnable.setRunMethod(self.__obsLightManager.addAndCommitChanges,
                                  project,
                                  package,
                                  message)
            runnable.caughtException.connect(self.__gui.popupErrorCallback)
            QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def __refreshStatus(self, method):
        if len(self.selectedPackages()) == 0:
            self.selectAllPackages()
        self.__mapOnSelectedPackages(firstArgLast(method),
                                     u"Refreshing package status",
                                     None,
                                     None,
                                     self.getCurrentProject())

    def on_refreshOscStatusButton_clicked(self):
        def refreshStatuses(*args, **kwargs):
            self.__obsLightManager.refreshOscDirectoryStatus(*args, **kwargs)
            self.__obsLightManager.refreshObsStatus(*args, **kwargs)
        self.__refreshStatus(refreshStatuses)

    def on_repairOscButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.__obsLightManager.repairOscPackageDirectory),
                                     None,
                                     u"Repairing OSC directory of %(arg)s...",
                                     self.on_refreshOscStatusButton_clicked,
                                     projectName)
