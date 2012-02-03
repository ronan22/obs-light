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
Created on 2 nov. 2011

@author: Florent Vennetier
@author: Ronan Le Martret
'''

import inspect

from PySide.QtCore import QObject, QRegExp
from PySide.QtGui import QLabel, QInputDialog, QPushButton, QTableView, QWidget
from PySide.QtGui import QLineEdit, QMessageBox, QRegExpValidator, QComboBox

from PackageModel import PackageModel
from PackageSelector import PackageSelector
from ObsLightGui.FileManager import FileManager
from Utils import popupOnException, ProgressRunnable2, firstArgLast
from ObsLightGuiObject import ObsLightGuiObject

class PackageManager(QObject, ObsLightGuiObject):
    '''
    Manages the package list widget and package-related buttons
    of the main window.
    '''

    __project = None
    __pkgModel = None
    __fileManager = None

    __packageTableView = None
    __packageNameLabel = None
    __packageTitleLabel = None
    __packageDescriptionLabel = None
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
    __packagePathLineEdit = None

    __packageSelector = None

    __menu = None

    __isInitPackageFilter = False

    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__fileManager = FileManager(self.gui)
        mainWindow = self.mainWindow
        # TODO: remove/move all these findChild calls
        self.__packageTableView = mainWindow.findChild(QTableView,
                                                       u"packageTableView")
        self.__packageTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.__packageTableView.activated.connect(self.on_packageIndex_clicked)
        self.mainWindow.importPackageButton.clicked.connect(self.on_newPackageButton_clicked)
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
        self.__modifyPatchButton.clicked.connect(self.on_modifyPatchButton_clicked)
        self.__addAndCommitButton = mainWindow.findChild(QPushButton,
                                                         u"addAndCommitButton")
        self.__addAndCommitButton.clicked.connect(self.on_addAndCommitButton_clicked)
        self.__packageNameLabel = mainWindow.findChild(QLabel, u"packageNameLabelValue")
        self.__packageTitleLabel = mainWindow.findChild(QLabel, u"packageTitleLabel")
        self.__packageDescriptionLabel = mainWindow.findChild(QLabel,
                                                              u"packageDescriptionLabel")

        self.__packageSelector = PackageSelector(self.gui)
        self.__packageSelector.packagesSelected.connect(self.on_packageSelector_packagesSelected)
        clickSignal = self.mainWindow.refreshOscStatusButton.clicked
        clickSignal.connect(self.on_refreshOscStatusButton_clicked)
        clickSignal = self.mainWindow.repairOscButton.clicked
        clickSignal.connect(self.on_repairOscButton_clicked)
        self.__packagePathLineEdit = mainWindow.findChild(QLineEdit,
                                                          u"packagePathLineEdit")

        #Package Filter
        self.__packageOscStatusFilter = mainWindow.findChild(QComboBox,
                                                          u"OscStatusFilter")
        self.__packageOscStatusFilter.currentIndexChanged.connect(self.on_packageOscStatusFilter)

        self.__packageOscRev = mainWindow.findChild(QLineEdit,
                                                          u"OscRev")
        self.__packageOscRev.editingFinished.connect(self.on_packageOscRev)
        self.__packageObsStatusFilter = mainWindow.findChild(QComboBox,
                                                          u"ObsStatusFilter")
        self.__packageObsStatusFilter.currentIndexChanged.connect(self.on_packageObsStatusFilter)

        self.__packageObsRev = mainWindow.findChild(QLineEdit, u"ObsRev")
        self.__packageObsRev.editingFinished.connect(self.on_packageObsRev)
        self.__packageChRootStatus = mainWindow.findChild(QComboBox,
                                                          u"ChRootStatus")
        self.__packageChRootStatus.currentIndexChanged.connect(self.on_packageChRootStatus)
    #---------------------------------------------------------------------------
    def initPackageFilter(self):
        currentProject = self.getCurrentProject()
        if currentProject != None:
            if not self.__isInitPackageFilter:
                self.__packageOscStatusFilter.insertItem(0, "")
                self.__packageObsStatusFilter.insertItem(0, "")
                self.__packageChRootStatus.insertItem(0, "")

                for i in self.manager.getListOscStatus(currentProject):
                    self.__packageOscStatusFilter.addItem(i)

                for i in self.manager.getListStatus(currentProject):
                    self.__packageObsStatusFilter.addItem(i)

                for i in self.manager.getListChRootStatus(currentProject):
                    self.__packageChRootStatus.addItem(i)

                self.__isInitPackageFilter = True

            packageFilter = self.manager.getPackageFilter(currentProject)
            if "oscStatus" in packageFilter.keys():
                val = packageFilter["oscStatus"]
                i = self.__packageOscStatusFilter.findText(val)
                self.__packageOscStatusFilter.setCurrentIndex(i)
            else:
                self.__packageOscStatusFilter.setCurrentIndex(0)

            if "oscRev" in packageFilter.keys():
                val = packageFilter["oscRev"]
                self.__packageOscRev.setText(val)
            else:
                self.__packageOscRev.setText("")

            if "status" in packageFilter.keys():
                val = packageFilter["status"]
                i = self.__packageObsStatusFilter.findText(val)
                self.__packageObsStatusFilter.setCurrentIndex(i)
            else:
                self.__packageObsStatusFilter.setCurrentIndex(0)

            if "obsRev" in packageFilter.keys():
                val = packageFilter["obsRev"]
                self.__packageObsRev.setText(val)
            else:
                self.__packageObsRev.setText("")

            if "chRootStatus" in packageFilter.keys():
                val = packageFilter["chRootStatus"]
                i = self.__packageChRootStatus.findText(val)
                self.__packageChRootStatus.setCurrentIndex(i)
            else:
                self.__packageChRootStatus.setCurrentIndex(0)
    #---------------------------------------------------------------------------
    def on_packageOscRev(self):
        currentProject = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(currentProject)
        if "oscRev" in packageFilter.keys():
            self.manager.removePackageFilter(currentProject, "oscRev")

        if self.__packageOscRev.text() != "":
            self.manager.addPackageFilter(currentProject,
                                          "oscRev",
                                          self.__packageOscRev.text())
        self.refresh()

    def on_packageObsRev(self):
        currentProject = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(currentProject)
        if "obsRev" in packageFilter.keys():
            self.manager.removePackageFilter(currentProject, "obsRev")
        if self.__packageObsRev.text() != "":
            self.manager.addPackageFilter(currentProject,
                                          "obsRev",
                                          self.__packageObsRev.text())
        self.refresh()

    def on_packageOscStatusFilter(self):
        currentProject = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(currentProject)
        if "oscStatus" in packageFilter.keys():
            self.manager.removePackageFilter(currentProject, "oscStatus")
        if self.__packageOscStatusFilter.currentIndex() != 0:
            self.manager.addPackageFilter(currentProject,
                                          "oscStatus",
                                          self.__packageOscStatusFilter.currentText())
        self.refresh()


    def on_packageObsStatusFilter(self):
        currentProject = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(currentProject)
        if "status" in packageFilter.keys():
            self.manager.removePackageFilter(currentProject, "status")
        if self.__packageObsStatusFilter.currentIndex() != 0:
            self.manager.addPackageFilter(currentProject,
                                          "status",
                                          self.__packageObsStatusFilter.currentText())
        self.refresh()

    def on_packageChRootStatus(self):
        currentProject = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(currentProject)
        if "chRootStatus" in packageFilter.keys():
            self.manager.removePackageFilter(currentProject, "chRootStatus")
        if self.__packageChRootStatus.currentIndex () != 0:
            self.manager.addPackageFilter(currentProject,
                                          "chRootStatus",
                                          self.__packageChRootStatus.currentText())
        self.refresh()
    #---------------------------------------------------------------------------
    def __loadPkgModel(self, projectName):
        self.__pkgModel = PackageModel(self.manager, projectName)

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
            self.callWithInfiniteProgress(self.__loadPkgModel,
                                          "Loading package list",
                                          projectName)
            self.__packageTableView.setModel(self.__pkgModel)
            self.mainWindow.packageWidget.setEnabled(self.__project is not None)
        if self.currentPackage() is not None:
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        else:
            self.__fileManager.setCurrentPackage(None, None)
        self.initPackageFilter()
        self.refresh()

    def on_packageIndex_clicked(self, index):
        if index.isValid():
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        self.refresh()

    def refresh(self):
        if self.__pkgModel != None:
            self.__pkgModel.refresh()
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
            packageTitle = self.manager.getPackageParameter(project,
                                                            package,
                                                            "title")
            description = self.manager.getPackageParameter(project,
                                                           package,
                                                           "description")

            self.__packageTitleLabel.setText(packageTitle)
            self.__packageDescriptionLabel.setText(description)
            pkgDir = self.manager.getPackageDirectory(project, package)
            self.__packagePathLineEdit.setText(pkgDir)
        else:
            self.__packageNameLabel.setText(u"No package selected")
            self.__packageTitleLabel.setText(u"")
            self.__packageDescriptionLabel.setText(u"")
            self.__packagePathLineEdit.setText("")

    def updateButtons(self):
        package = self.currentPackage()
        project = self.getCurrentProject()
        chrootInit = (project is not None and
                      self.manager.isChRootInit(project))
        installed = (chrootInit and package is not None and
                     self.manager.isInstalledInChRoot(project, package))
        self.__rpmPrepButton.setEnabled(chrootInit)
        self.__rpmBuildButton.setEnabled(installed)
        self.__rpmInstallButton.setEnabled(installed)
        self.__rpmBuildRpmButton.setEnabled(installed)
        patchIsInitialized = (package is not None and
                              self.manager.patchIsInit(project, package))
        self.__generatePatchButton.setEnabled(installed and not patchIsInitialized)
        self.__modifyPatchButton.setEnabled(installed and patchIsInitialized)

    def currentPackage(self):
        '''
        Get the name of the package that is currently selected in the
        package list. May return None.
        '''
        index = self.__packageTableView.currentIndex()
        if index.isValid():
            row = index.row()
            pkgNameIndex = self.__pkgModel.createIndex(row, PackageModel.NameColumn)
            packageName = self.__pkgModel.data(pkgNameIndex)
            return packageName
        else:
            return None

    def selectedPackages(self):
        '''
        Get the list of currently selected packages. If no package selected,
        returns an empty list (not None).
        '''
        indices = self.__packageTableView.selectedIndexes()
        if len(indices) < 1:
            indices.append(self.__packageTableView.currentIndex())
        packages = set()
        for index in indices:
            if index.isValid():
                row = index.row()
                packageNameIndex = self.__pkgModel.createIndex(row,
                                                               PackageModel.NameColumn)
                packageName = self.__pkgModel.data(packageNameIndex)
                packages.add(packageName)
        return list(packages)

    def selectAllPackages(self):
        self.__packageTableView.selectAll()

    def getPackageListFromServer(self):
        if self.getCurrentProject() is None:
            return list()
        server = self.manager.getProjectParameter(self.getCurrentProject(),
                                                            u"obsServer")
        prjObsName = self.manager.getProjectParameter(self.getCurrentProject(),
                                                                u"projectObsName")
        packageList = self.manager.getObsProjectPackageList(server,
                                                                      prjObsName)
        return packageList

    def showPackageSelectionDialog(self, packageList):
        if packageList is None or len(packageList) < 1:
            QMessageBox.information(self.mainWindow,
                                    u"No package",
                                    u"No packages were found.")
            return
        self.__packageSelector.showPackageSelectionDialog(packageList)

    def __mapOnSelectedPackages(self,
                                method,
                                initialMessage,
                                loopMessage,
                                callback,
                                *args,
                                **kwargs):
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return
        elif len(packagesNames) < 2:
            progress = self.gui.getInfiniteProgressDialog()
        else:
            progress = self.gui.getProgressDialog()
            progress.setValue(0)
        runnable = ProgressRunnable2(progress)
        if initialMessage is not None:
            runnable.setDialogMessage(initialMessage)
        runnable.setFunctionToMap(method, packagesNames, loopMessage, *args, **kwargs)
        #runnable.setRunMethod(method, packagesNames, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        if callback is not None:
            argNum = len(inspect.getargspec(callback)[0])
            if argNum > 1:
                runnable.finished[object].connect(callback)
            else:
                runnable.finished.connect(callback)
        runnable.runOnGlobalInstance()

    def __mapOnSelectedPackages2(self,
                                method,
                                initialMessage,
                                loopMessage,
                                callback,
                                *args,
                                **kwargs):
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return

        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        if initialMessage is not None:
            runnable.setDialogMessage(initialMessage)
#        runnable.setFunctionToMap(method, packagesNames, loopMessage, *args, **kwargs)
        runnable.setRunMethod(method, packagesNames, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        if callback is not None:
            argNum = len(inspect.getargspec(callback)[0])
            if argNum > 1:
                runnable.finished[object].connect(callback)
            else:
                runnable.finished.connect(callback)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_newPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        self.gui.runWizard(autoSelectProject=self.getCurrentProject())

    def on_packageSelector_packagesSelected(self, packages):
        if len(packages) < 2:
            progress = self.gui.getInfiniteProgressDialog()
        else:
            progress = self.gui.getProgressDialog()
            progress.setValue(0)
        runnable = ProgressRunnable2(progress)
        runnable.setFunctionToMap(self.__pkgModel.addPackage,
                                  packages,
                                  message=u"Adding package %(arg)s")
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refresh)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_deletePackageButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return

        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return
        result = QMessageBox.question(self.mainWindow,
                                      u"Are you sure ?",
                                      u"Are you sure you want to remove %d packages ?"
                                        % len(packagesNames),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        self.__mapOnSelectedPackages(self.__pkgModel.removePackage,
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
            if self.manager.isInstalledInChRoot(self.__project, package):
                alreadyInstalled.append(package)
        if len(alreadyInstalled) > 0:
            questionString = u"The packages <b>%s" % unicode(alreadyInstalled[0])
            for package in alreadyInstalled[1:]:
                questionString += u", %s" % unicode(package)
            questionString += u"</b> are already present in the chroot, do you want to"
            questionString += u" overwrite them ?"
            result = QMessageBox.question(self.mainWindow,
                                          u"Overwrite ?",
                                          questionString,
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Yes)
            if result != QMessageBox.Yes:
                return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.addPackageSourceInChRoot),
                                     None,
                                     u"Importing %(arg)s source in chroot and executing %%prep",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmBuildButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.buildRpm),
                                     None,
                                     u"Executing %%build section of %(arg)s",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmInstallButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.installRpm),
                                     None,
                                     u"Executing %%install section of %(arg)s",
                                     None,
                                     projectName)

    @popupOnException
    def on_rpmBuildRpmButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.packageRpm),
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
        runnable.setRunMethod(self.manager.openTerminal,
                              project,
                              package)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_updateFilesButton_clicked(self):
        project = self.getCurrentProject()
        if project is None:
            return
        def myTestConflict(package, project):
            conflict = self.manager.testConflict(project, package)
            return package, conflict

        self.__mapOnSelectedPackages(myTestConflict,
                                     u"Checking for potential conflicts",
                                     u"Checking if package <i>%(arg)s</i> has a conflict",
                                     self.__preCheckingConflicts,
                                     project)

    def __preCheckingConflicts(self, values):
        packagesInConflict = []
        if values is None:
            return
        for package, conflict in values:
            if conflict:
                packagesInConflict.append(package)
        if len(packagesInConflict) > 0:
            question = u"Some files in packages you selected (<i>%s</i>) have conflicts.<br />"
            question += u"It is recommended that you resolve these conflicts before updating.<br />"
            question += u"-> modify conflicting file and run "
            question += u"<i>osc resolved FILE</i> in package directory.<br />"
            question += u"<br />Do you want to continue anyway?"
            result = QMessageBox.question(self.mainWindow,
                                          u"Conflict detected",
                                          question % u", ".join(packagesInConflict),
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Cancel)
            if result != QMessageBox.Yes:
                return
        self.__doUpdatePackages()

    def __doUpdatePackages(self):
        project = self.getCurrentProject()
        if project is None:
            return
        self.__mapOnSelectedPackages2(firstArgLast(self.manager.updatePackage),
                                     u"Updating packages",
                                     u"Updating <i>%(arg)s</i> package...",
                                     self.__refreshStatus,
                                     project)

    @popupOnException
    def __createPatch(self, patchName):
        project = self.getCurrentProject()
        package = self.currentPackage()
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Creating patch...")
        runnable.setRunMethod(self.manager.makePatch,
                              project,
                              package,
                              patchName)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refresh)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_makePatchButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        dialog = QInputDialog(self.mainWindow)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setLabelText(u"Patch name (should end with <i>.patch</i>):")
        dialog.setWindowTitle(u"Choose patch name...")
        le = dialog.findChildren(QLineEdit)
        if len(le) > 0:
            validator = QRegExpValidator(le[0])
            validator.setRegExp(QRegExp(u"\\S+\.patch"))
            le[0].setText(u".patch")
            le[0].setValidator(validator)
        dialog.textValueSelected.connect(self.__createPatch)
        dialog.show()

    def on_modifyPatchButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Updating patch...")
        runnable.setRunMethod(self.manager.updatePatch,
                              project,
                              package)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refresh)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_addAndCommitButton_clicked(self):
        project = self.getCurrentProject()
        package = self.currentPackage()
        if project is None or package is None:
            return

        conflict = self.manager.testConflict(project, package)

        if conflict:
            question = u"A file in package <i>%s</i> has a conflict.<br />"
            question += u"It is recommended that you resolve this conflict before committing.<br />"
            question += u"-> modify conflicting file and run "
            question += u"<i>osc resolved FILE</i> in package directory.<br />"
            question += u"<br />Do you want to continue anyway?"
            result = QMessageBox.question(self.mainWindow,
                                          u"Conflict detected",
                                          question % package,
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Cancel)
            if result != QMessageBox.Yes:
                return

        message, accepted = QInputDialog.getText(self.mainWindow,
                                                 u"Enter commit message...",
                                                 u"Commit message:")
        if accepted:
            progress = self.gui.getInfiniteProgressDialog()
            runnable = ProgressRunnable2(progress)
            runnable.setDialogMessage(u"Committing changes")
            runnable.setRunMethod(self.manager.addAndCommitChanges,
                                  project,
                                  package,
                                  message)
            runnable.caughtException.connect(self.gui.popupErrorCallback)
            runnable.finished.connect(self.__refreshStatus)
            runnable.runOnGlobalInstance()

    def __refreshBothStatuses(self, *args, **kwargs):
        self.manager.refreshOscDirectoryStatus(*args, **kwargs)
        self.manager.refreshObsStatus(*args, **kwargs)

    def __refreshStatus(self):
        if len(self.selectedPackages()) == 0:
            self.selectAllPackages()
        self.__mapOnSelectedPackages2(firstArgLast(self.__refreshBothStatuses),
                                     u"Refreshing package status",
                                     u"Refreshing <i>%(arg)s</i> package status...",
                                     self.refresh,
                                     self.getCurrentProject())

    @popupOnException
    def on_refreshOscStatusButton_clicked(self):
        self.__refreshStatus()

    @popupOnException
    def on_repairOscButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        question = u"<i>Warning:</i> if you have local modifications, they will"
        question += u" be discarded.<br/>Do you want to continue?"
        result = QMessageBox.warning(self.mainWindow,
                                     u"Discard modifications?",
                                     question,
                                     buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                     defaultButton=QMessageBox.Cancel)
        if result != QMessageBox.Yes:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.repairOscPackageDirectory),
                                     None,
                                     u"Repairing OSC directory of %(arg)s...",
                                     self.__refreshStatus,
                                     projectName)
