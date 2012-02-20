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
Created on 27 sept. 2011

@author: Florent Vennetier
'''

from PySide.QtGui import QFileDialog, QMessageBox

from Utils import ProgressRunnable2, popupOnException
from PackageManager import PackageManager
from RepoConfigManager import RepoConfigManager
from ProjectConfigManager import ProjectConfigManager

from ObsLightGuiObject import ObsLightGuiObject
from ProjectsManagerBase import ProjectsManagerBase

class ObsProjectsManager(ObsLightGuiObject, ProjectsManagerBase):
    '''
    Manages the local project list widget and project-related buttons
    of the main window.
    '''

    def __init__(self, gui):
        """
        Initialize the ObsProjectsManager.
        `gui` must be a reference to the main `Gui` instance.
        """
        ObsLightGuiObject.__init__(self, gui)
        ProjectsManagerBase.__init__(self,
                                     self.mainWindow.obsProjectsListWidget,
                                     self.manager.getLocalProjectList)
        self.__projectConfigManager = None
        self.__repoConfigManager = None
        self.loadProjectList()
        self.projectListWidget.currentTextChanged.connect(self.on_projectSelected)
        self.__packageManager = PackageManager(self.gui)
        self.__connectButtons()

    def __connectButtons(self):
        """
        Connect project-related, chroot-related and repository-related
        buttons of the OBS project tab to the appropriate methods.
        """
        mw = self.mainWindow
        mw.newObsProjectButton.clicked.connect(self.gui.runWizard)
        mw.modifyObsProjectButton.clicked.connect(self.on_modifyObsProjectButton_clicked)
        mw.deleteObsProjectButton.clicked.connect(self.on_deleteObsProjectButton_clicked)
        mw.loadObsProjectButton.clicked.connect(self.on_importObsProjectButton_clicked)
        mw.saveObsProjectButton.clicked.connect(self.on_exportObsProjectButton_clicked)
        mw.newChrootButton.clicked.connect(self.on_newChrootButton_clicked)
        mw.openChrootButton.clicked.connect(self.on_openChrootButton_clicked)
        mw.deleteChrootButton.clicked.connect(self.on_deleteChrootButton_clicked)
        mw.addRepoInChrootButton.clicked.connect(self.on_addRepoInChrootButton_clicked)
        mw.deleteRepositoryButton.clicked.connect(self.on_deleteRepoButton_clicked)
        mw.modifyRepositoryButton.clicked.connect(self.on_modifyRepoButton_clicked)
        mw.importRepoInChrootButton.clicked.connect(self.on_importRepoInChrootButton_clicked)

    @popupOnException
    def on_modifyObsProjectButton_clicked(self):
        projectName = self.currentProject
        if projectName is None:
            return
        self.__projectConfigManager = ProjectConfigManager(self.gui, projectName)
        self.__projectConfigManager.finished.connect(self.on_projectConfigManager_finished)

    @popupOnException
    def on_deleteObsProjectButton_clicked(self):
        projectName = self.currentProject
        if projectName is None:
            return
        result = QMessageBox.question(self.mainWindow,
                                      "Are you sure ?",
                                      "Are you sure you want to delete %s project ?"
                                        % projectName,
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Deleting project...")
        runnable.setRunMethod(self.manager.removeProject, projectName)
        runnable.finished.connect(self.refresh)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_importObsProjectButton_clicked(self):
        filePath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        u"Select project to import")
        if len(filePath) < 1:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Importing project...")
        runnable.setRunMethod(self.manager.importProject, filePath)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refresh)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_exportObsProjectButton_clicked(self):
        project = self.currentProject
        if project is None:
            return
        filePath, _filter = QFileDialog.getSaveFileName(self.mainWindow,
                                                        u"Select file to export")
        if len(filePath) < 1:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Exporting project...")
        runnable.setRunMethod(self.manager.exportProject, project, filePath)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refresh)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_projectConfigManager_finished(self, success):
        if success:
            self.loadProjectList()
            self.on_projectSelected(None)

    @popupOnException
    def on_newChrootButton_clicked(self):
        projectName = self.currentProject
        if projectName is None or self.manager.isChRootInit(projectName):
            return
        runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
        runnable.setDialogMessage(u"Creating project file system...")
        runnable.setRunMethod(self.manager.createChRoot,
                              projectName)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refreshProject)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_openChrootButton_clicked(self):
        projectName = self.currentProject
        if projectName is None or not self.manager.isChRootInit(projectName):
            return

        currentPackage = self.__packageManager.currentPackage()
        runnable = ProgressRunnable2()
        if currentPackage is None:
            runnable.setRunMethod(self.manager.goToChRoot,
                                  projectName,
                                  detach=True)
        else:
            runnable.setRunMethod(self.manager.goToChRoot,
                                  projectName,
                                  currentPackage,
                                  detach=True)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refreshProject)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_deleteChrootButton_clicked(self):
        projectName = self.currentProject
        if projectName is not None:
            result = QMessageBox.question(self.mainWindow,
                                      "Are you sure ?",
                                      "Are you sure you want to delete %s's file system ?"
                                        % projectName,
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            progress = self.gui.getInfiniteProgressDialog()
            runnable = ProgressRunnable2(progress)
            runnable.setDialogMessage(u"Deleting file system")
            runnable.setRunMethod(self.manager.removeChRoot, projectName)
            runnable.finished.connect(self.refreshProject)
            runnable.caughtException.connect(self.gui.popupErrorCallback)
            runnable.runOnGlobalInstance()

    @popupOnException
    def on_addRepoInChrootButton_clicked(self):
        projectName = self.currentProject
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.importFromUrl()

    @popupOnException
    def on_deleteRepoButton_clicked(self):
        projectName = self.currentProject
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.deleteRepo()

    @popupOnException
    def on_modifyRepoButton_clicked(self):
        projectName = self.currentProject
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.modifyRepo()

    @popupOnException
    def on_importRepoInChrootButton_clicked(self):
        projectName = self.currentProject
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.importFromProject()

    def on_projectSelected(self, _project):
        self.refreshProject()

    def refreshProject(self):
        """
        Refresh the project, package and chroot views.
        """
        project = self.currentProject
        self.__packageManager.setCurrentProject(project)
        self.updateProjectLabels()
        self.updateChrootPathAndButtons()

    @popupOnException
    def updateProjectLabels(self):
        '''
        Update the different labels according to project parameters.
        '''
        project = self.currentProject
        if project is not None:
            projectLink = self.manager.getProjectWebPage(project)
            projectObsName = self.manager.getProjectParameter(project, "projectObsName")
            target = self.manager.getProjectParameter(project, "projectTarget")
            repoLink = self.manager.getProjectRepository(project)
            projectTitle = self.manager.getProjectParameter(project, "title")
            projectDescription = self.manager.getProjectParameter(project, "description")

            self.mainWindow.projectLabelValue.setText(project)
            self.mainWindow.projectTitleLabel.setText(projectTitle)
            self.mainWindow.projectDescriptionLabel.setText(projectDescription)
            self.mainWindow.projectPageLinkLabel.setText(u'<a href="%s">%s</a>' % (projectLink,
                                                                                   projectObsName))
            self.mainWindow.projectRepoPageLinkLabel.setText(u'<a href="%s">%s</a>' % (repoLink,
                                                                                       target))
            self.mainWindow.saveObsProjectButton.setEnabled(True)
        else:
            self.mainWindow.saveObsProjectButton.setEnabled(False)

    @popupOnException
    def updateChrootPathAndButtons(self):
        '''
        Update the chroot path displayed in the main window
        with the one of the currently selected project.
        Enable/disable some buttons according to the state
        of the chroot.
        '''
        project = self.currentProject
        if project is not None:
            isChrootInit = self.manager.isChRootInit(project)
            if isChrootInit:
                chrootPath = self.manager.getChRootPath(project)
                self.mainWindow.chrootPathLineEdit.setText(chrootPath)

                self.mainWindow.newChrootButton.setEnabled(False)
                self.mainWindow.openChrootButton.setEnabled(True)
            else:
                self.mainWindow.newChrootButton.setEnabled(True)
                self.mainWindow.openChrootButton.setEnabled(False)
                self.mainWindow.chrootPathLineEdit.setText("")

            self.mainWindow.addRepoInChrootButton.setEnabled(isChrootInit)
            self.mainWindow.importRepoInChrootButton.setEnabled(isChrootInit)
            self.mainWindow.deleteRepositoryButton.setEnabled(isChrootInit)
            self.mainWindow.modifyRepositoryButton.setEnabled(isChrootInit)

            self.mainWindow.deleteChrootButton.setEnabled(isChrootInit)
