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

import PySide

from PySide.QtCore import QObject
from PySide.QtGui import QInputDialog, QTableView
from PySide.QtGui import QLineEdit, QMessageBox, QRegExpValidator

from PackageModel import PackageModel
from ObsLightGui.FileManager import FileManager
from Utils import popupOnException, ProgressRunnable2, firstArgLast, PATCH_NAME_REGEXP
from ObsLightGuiObject import ObsLightGuiObject

class PackageManager(QObject, ObsLightGuiObject):
    '''
    Manages the package list widget and package-related buttons
    of the main window.
    '''

    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__fileManager = FileManager(self.gui)

        # loaded in __loadPkgModel()
        self.__pkgModel = None
        # loaded in setCurrentProject()
        self.__project = None
        # in use in initializePackageFilters()
        self.__packageFilterInitialized = False
        # in use in on_addAndCommitButton_clicked()
        self.__commitDialog = None

        mw = self.mainWindow
        mw.packageTableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        mw.packageTableView.clicked.connect(self.on_packageTableView_activated)

        self.__connectButtons()
        self.__connectPackageFilterSignals()

    def __connectButtons(self):
        """
        Connect all package-related buttons to the appropriate methods.
        """
        mw = self.mainWindow
        mw.newPackageButton.clicked.connect(self.on_newPackageButton_clicked)
        mw.importPackageButton.clicked.connect(self.on_importPackageButton_clicked)
        mw.deletePackageButton.clicked.connect(self.on_deletePackageButton_clicked)
        mw.openTermButton.clicked.connect(self.on_openTermButton_clicked)
        mw.updateFilesButton.clicked.connect(self.on_updateFilesButton_clicked)
        mw.generatePatchButton.clicked.connect(self.on_makePatchButton_clicked)
        mw.modifyPatchButton.clicked.connect(self.on_modifyPatchButton_clicked)
        mw.addAndCommitButton.clicked.connect(self.on_addAndCommitButton_clicked)
        mw.refreshOscStatusButton.clicked.connect(self.on_refreshOscStatusButton_clicked)
        mw.repairOscButton.clicked.connect(self.on_repairOscButton_clicked)

        mw.rpmPrepButton.clicked.connect(self.on_rpmPrepButton_clicked)
        mw.rpmBuildButton.clicked.connect(self.on_rpmBuildButton_clicked)
        mw.rpmInstallButton.clicked.connect(self.on_rpmInstallButton_clicked)
        mw.rpmBuildRpmButton.clicked.connect(self.on_rpmBuildRpmButton_clicked)

        mw.PatchMode_checkBox.clicked.connect(self.on_PatchMode_checkBox_clicked)

    def on_PatchMode_checkBox_clicked(self):
        """
        The "Patch Mode" allows the user to automatically generate patches from his local work.
        The "Patch Mode" requires the user to perform a "% prep" and a first "% build".
        If the user disables the "Patch Mode", it definitely will be disabled.
        To reactivate the "Patch Mode" re-install the package.
        """
        mw = self.mainWindow

        if not mw.PatchMode_checkBox.isChecked():
            questionString = u"If the user disables the Patch Mode, it definitely will be disabled. \
                              To reactivate the Patch Mode re-install the package."
            result = QMessageBox.question(self.mainWindow,
                                          u"Overwrite ?",
                                          questionString,
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Yes)
            if result == QMessageBox.Yes:
                self.__disable_PatchMode()
            else:
                mw.PatchMode_checkBox.setCheckState(PySide.QtCore.Qt.CheckState(PySide.QtCore.Qt.Checked))

    def __disable_PatchMode(self):
        """
        Disable the patch Mode of the Package.
        """
        mw = self.mainWindow
        currentProject = self.getCurrentProject()

        for package in self.selectedPackages():
            self.manager.setPackageParameter(currentProject, package, "patchMode", False)

        if mw.PatchMode_checkBox.isChecked():
            mw.PatchMode_checkBox.setCheckState(PySide.QtCore.Qt.CheckState(PySide.QtCore.Qt.Unchecked))
        mw.PatchMode_checkBox.setEnabled(0)

        self.updateButtons()


    def __connectPackageFilterSignals(self):
        """
        Connect package filter signals to the appropriate methods.
        """
        mw = self.mainWindow
        signal = mw.oscStatusFilterComboBox.currentIndexChanged
        signal.connect(self.on_oscStatusFilterComboBox_currentIndexChanged)
        signal = mw.obsStatusFilterComboBox.currentIndexChanged
        signal.connect(self.on_obsStatusFilterComboBox_currentIndexChanged)
        signal = mw.chrootStatusComboBox.currentIndexChanged
        signal.connect(self.on_chrootStatusComboBox_currentIndexChanged)

        signal = mw.obsRevFilterLineEdit.editingFinished
        signal.connect(self.on_obsRevFilterLineEdit_editingFinished)
        signal = mw.oscRevFilterLineEdit.editingFinished
        signal.connect(self.on_oscRevFilterLineEdit_editingFinished)

    def initializePackageFilters(self):
        currentProject = self.getCurrentProject()
        if currentProject is not None:
            if not self.__packageFilterInitialized:
                self.mainWindow.oscStatusFilterComboBox.insertItem(0, "")
                self.mainWindow.obsStatusFilterComboBox.insertItem(0, "")
                self.mainWindow.chrootStatusComboBox.insertItem(0, "")

                for i in self.manager.getListOscStatus(currentProject):
                    self.mainWindow.oscStatusFilterComboBox.addItem(i)

                for i in self.manager.getListStatus(currentProject):
                    self.mainWindow.obsStatusFilterComboBox.addItem(i)

                for i in self.manager.getListChRootStatus(currentProject):
                    self.mainWindow.chrootStatusComboBox.addItem(i)

                self.__packageFilterInitialized = True

            packageFilter = self.manager.getPackageFilter(currentProject)
            for status, cbox in [("oscStatus", self.mainWindow.oscStatusFilterComboBox),
                                 ("status", self.mainWindow.obsStatusFilterComboBox),
                                 ("chRootStatus", self.mainWindow.chrootStatusComboBox)]:
                if status in packageFilter:
                    val = packageFilter[status]
                    index = cbox.findText(val)
                    cbox.setCurrentIndex(index)
                else:
                    cbox.setCurrentIndex(0)

            for revType, lineEdit in [("oscRev", self.mainWindow.obsRevFilterLineEdit),
                                      ("obsRev", self.mainWindow.oscRevFilterLineEdit)]:
                if revType in packageFilter:
                    val = packageFilter[revType]
                    lineEdit.setText(val)
                else:
                    lineEdit.setText("")

    def __updatePackageFilter(self, filterType, filterValue):
        """
        Update `filterType` package filter with `filterValue`,
        and refresh package view. 
        """
        project = self.getCurrentProject()
        packageFilter = self.manager.getPackageFilter(project)
        if filterType in packageFilter:
            self.manager.removePackageFilter(project, filterType)
        if filterValue != "":
            self.manager.addPackageFilter(project, filterType, filterValue)
        self.refresh()

    def on_oscRevFilterLineEdit_editingFinished(self):
        self.__updatePackageFilter("oscRev", self.mainWindow.oscRevFilterLineEdit.text())

    def on_obsRevFilterLineEdit_editingFinished(self):
        self.__updatePackageFilter("obsRev", self.mainWindow.obsRevFilterLineEdit.text())

    def on_oscStatusFilterComboBox_currentIndexChanged(self):
        self.__updatePackageFilter("oscStatus",
                                   self.mainWindow.oscStatusFilterComboBox.currentText())

    def on_obsStatusFilterComboBox_currentIndexChanged(self):
        self.__updatePackageFilter("status",
                                   self.mainWindow.obsStatusFilterComboBox.currentText())

    def on_chrootStatusComboBox_currentIndexChanged(self):
        self.__updatePackageFilter("chRootStatus",
                                   self.mainWindow.chrootStatusComboBox.currentText())

    def __loadPkgModel(self, projectName):
        """
        Create a new PackageModel instance for `projectName`.
        May take a little time.
        """
        self.__pkgModel = PackageModel(self.manager, projectName)

    def getCurrentProject(self):
        """
        Get the current project managed by the PackageManager.
        """
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
            self.mainWindow.packageTableView.setModel(self.__pkgModel)
            self.mainWindow.packageWidget.setEnabled(self.__project is not None)
        if self.currentPackage() is not None:
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        else:
            self.__fileManager.setCurrentPackage(None, None)
        self.initializePackageFilters()
        self.refresh()

    def on_packageTableView_activated(self, index):
        if index.isValid():
            self.__fileManager.setCurrentPackage(self.__project, self.currentPackage())
        self.refresh()

    def refresh(self):
        """
        Refresh the PackageManager.
        """
        if self.__pkgModel != None:
            self.__pkgModel.refresh()
        self.__fileManager.refresh()
        self.updateLabels()
        self.updateButtons()
        self.mainWindow.packageTableView.resizeColumnToContents(PackageModel.ObsRevColumn)
        self.mainWindow.packageTableView.resizeColumnToContents(PackageModel.OscRevColumn)

    def updateLabels(self):
        """
        Update the package-related labels of the OBS project tab.
        """
        package = self.currentPackage()
        project = self.getCurrentProject()
        if package is not None:
            self.mainWindow.packageNameLabelValue.setText(package)
            packageTitle = self.manager.getPackageParameter(project, package, "title")
            description = self.manager.getPackageParameter(project, package, "description")

            self.mainWindow.packageTitleLabel.setText(packageTitle)
            self.mainWindow.packageDescriptionLabel.setText(description)
            pkgDir = self.manager.getPackageParameter(project, package,
                                                      parameter="oscPackageDirectory")
            self.mainWindow.packagePathLineEdit.setText(pkgDir)
        else:
            self.mainWindow.packageNameLabelValue.setText("No package selected")
            self.mainWindow.packageTitleLabel.setText("")
            self.mainWindow.packageDescriptionLabel.setText("")
            self.mainWindow.packagePathLineEdit.setText("")

    def updateButtons(self):
        """
        Activate/deactivate the package-related buttons of the
        OBS project tab, according to the package statuses.
        """
        mw = self.mainWindow

        package = self.currentPackage()
        project = self.getCurrentProject()

        if package is not None and project is not None:
            patchMode = self.manager.getPackageParameter(project, package, "patchMode")
        else:
            patchMode = True

        chrootInit = (project is not None and
                      self.manager.isChRootInit(project))
        installed = (chrootInit and
                     package is not None and
                     (self.manager.isInstalledInChRoot(project, package) or not patchMode))

        mw.rpmPrepButton.setEnabled(chrootInit)
        mw.rpmBuildButton.setEnabled(installed)
        mw.rpmInstallButton.setEnabled(installed)
        mw.rpmBuildRpmButton.setEnabled(installed)

        patchIsInitialized = (package is not None and
                              self.manager.patchIsInit(project, package) and
                              patchMode)
        mw.generatePatchButton.setEnabled(installed and not patchIsInitialized and patchMode)
        mw.modifyPatchButton.setEnabled(installed and patchIsInitialized and patchMode)

        if package is not None and project is not None:
            if patchMode:
                mw.PatchMode_checkBox.setCheckState(PySide.QtCore.Qt.CheckState(PySide.QtCore.Qt.Checked))
                mw.PatchMode_checkBox.setEnabled(1)
            else:
                mw.PatchMode_checkBox.setCheckState(PySide.QtCore.Qt.CheckState(PySide.QtCore.Qt.Unchecked))
                mw.PatchMode_checkBox.setEnabled(0)

    def currentPackage(self):
        '''
        Get the name of the package that is currently selected in the
        package list. May return None.
        '''
        index = self.mainWindow.packageTableView.currentIndex()
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
        indices = self.mainWindow.packageTableView.selectedIndexes()
        if len(indices) < 1:
            indices.append(self.mainWindow.packageTableView.currentIndex())
        packages = set()
        for index in indices:
            if index.isValid():
                row = index.row()
                packageNameIndex = self.__pkgModel.createIndex(row, PackageModel.NameColumn)
                packageName = self.__pkgModel.data(packageNameIndex)
                packages.add(packageName)
        return list(packages)

    def selectAllPackages(self):
        """
        Select all packages of displayed in the package table view.
        """
        self.mainWindow.packageTableView.selectAll()

    def getPackageListFromServer(self):
        """
        Get a list of all packages of the current project on the server.
        This list is most probably longer than the list of local packages.
        """
        if self.getCurrentProject() is None:
            return list()
        server = self.manager.getProjectParameter(self.getCurrentProject(), "obsServer")
        prjObsName = self.manager.getProjectParameter(self.getCurrentProject(), "projectObsName")
        packageList = self.manager.getObsProjectPackageList(server, prjObsName)
        return packageList

    def __mapOnSelectedPackages(self,
                                method,
                                initialMessage,
                                loopMessage,
                                callback,
                                *args,
                                **kwargs):
        """
        Call `method(package, *args, **kwargs)` with package
        being successively each of the currently selected packages.
        `callback` will be called at the end of the process. If `callback`
        takes an argument, it will get the list of results of the
        different `method` calls. `initialMessage` will be displayed
        on the progress dialog before the beginning of the internal loop
        on selected packages. `loopMessage` will be displayed at each loop,
        and "%(arg)s" will be replaced by the name of package being
        processed.
        """
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            # no package selected, return
            return
        elif len(packagesNames) < 2:
            # just one package selected, show an infinite progress dialog
            progress = self.gui.getInfiniteProgressDialog()
        else:
            # several packages selected, show a standard progress dialog
            progress = self.gui.getProgressDialog()
            progress.setValue(0)
        runnable = ProgressRunnable2(progress)
        if initialMessage is not None:
            runnable.setDialogMessage(initialMessage)
        runnable.setFunctionToMap(method, packagesNames, loopMessage, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        if callback is not None:
            # detect if callback takes arguments in order to call
            # the appropriate finish signal
            argNum = len(inspect.getargspec(callback)[0])
            if argNum > 1:
                runnable.finished[object].connect(callback)
            else:
                runnable.finished.connect(callback)
        runnable.runOnGlobalInstance()

    def __callWithSelectedPackages(self,
                                   method,
                                   initialMessage,
                                   callback,
                                   *args,
                                   **kwargs):
        """
        Call `method(packages, *args, **kwargs)` with packages being
        the list of currently selected packages.
        `callback` will be called at the end of the process.
        If `callback` takes an argument, it will get the result of
        the call to `method`.
        `initialMessage` will be displayed on the progress dialog.
        """
        packagesNames = self.selectedPackages()
        if len(packagesNames) < 1:
            return

        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        if initialMessage is not None:
            runnable.setDialogMessage(initialMessage)
        runnable.setRunMethod(method, packagesNames, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        if callback is not None:
            # detect if callback takes arguments in order to call
            # the appropriate finish signal
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
        self.gui.runWizardToAddPackage(self.getCurrentProject(), newPackage=True)

    @popupOnException
    def on_importPackageButton_clicked(self):
        if self.getCurrentProject() is None:
            return
        self.gui.runWizardToAddPackage(self.getCurrentProject())

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

    def __handleRpmOperationResult(self, retValList):
        """
        Analyze the return values contained in `retValList`
        and display a message if one if different from 0.
        """
        message = None
        if len(retValList) == 1 and retValList[0] != 0:
            message = u"The last operation return code is %d.\n" % retValList[0]
        elif len(retValList) > 1:
            res = reduce(lambda x, y: abs(x) + abs(y), retValList)
            if res > 0:
                message = u"One of the last operations may have failed (return code != 0)\n"
        if message is not None:
            message += u"You should check the log to find any error."
            QMessageBox.warning(self.mainWindow,
                                u"Bad exit status",
                                message)
        self.__refreshStatus()

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
            questionString += u"</b> are already present in the project file system, "
            questionString += u"do you want to overwrite them ?"
            result = QMessageBox.question(self.mainWindow,
                                          u"Overwrite ?",
                                          questionString,
                                          buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                          defaultButton=QMessageBox.Yes)
            if result != QMessageBox.Yes:
                return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.buildPrep),
                                     None,
                                     u"Importing %(arg)s source in file system " +
                                     "and executing %%prep",
                                     self.__handleRpmOperationResult,
                                     projectName)

    @popupOnException
    def on_rpmBuildButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.buildRpm),
                                     None,
                                     u"Executing %%build section of %(arg)s",
                                     self.__handleRpmOperationResult,
                                     projectName)

    @popupOnException
    def on_rpmInstallButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.installRpm),
                                     None,
                                     u"Executing %%install section of %(arg)s",
                                     self.__handleRpmOperationResult,
                                     projectName)

    @popupOnException
    def on_rpmBuildRpmButton_clicked(self):
        projectName = self.getCurrentProject()
        if projectName is None:
            return
        self.__mapOnSelectedPackages(firstArgLast(self.manager.packageRpm),
                                     None,
                                     u"Packaging %(arg)s",
                                     self.__handleRpmOperationResult,
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
        self.__callWithSelectedPackages(firstArgLast(self.manager.updatePackage),
                                        u"Updating packages",
                                        self.__refreshStatus,
                                        project)

    @popupOnException
    def __createPatch(self, patchName):
        project = self.getCurrentProject()
        package = self.currentPackage()
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Creating patch...")
        runnable.setRunMethod(self.manager.createPatch,
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
            validator = QRegExpValidator(PATCH_NAME_REGEXP, le[0])
            le[0].setText(u".patch")
            le[0].setValidator(validator)
        dialog.textValueSelected.connect(self.__createPatch)
        dialog.show()

    @popupOnException
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

        self.__commitDialog = self.gui.loadWindow(u"commitMessageDialog.ui")
        self.__commitDialog.accepted.connect(self.__doCommit)
        self.__commitDialog.show()

    def __doCommit(self):
        message = self.__commitDialog.commitMessageTextEdit.toPlainText()
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Committing changes")
        runnable.setRunMethod(self.manager.addAndCommitChanges,
                              self.getCurrentProject(),
                              self.currentPackage(),
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
        self.__callWithSelectedPackages(firstArgLast(self.__refreshBothStatuses),
                                        u"Refreshing package status",
                                        self.refresh,
                                        self.getCurrentProject())

    @popupOnException
    def on_refreshOscStatusButton_clicked(self):
        """
        Called when user clicks on "refresh status" button.
        Refreshes both OBS and OSC statuses.
        """
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
