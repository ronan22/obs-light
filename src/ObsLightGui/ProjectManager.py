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

from PySide.QtCore import QObject, QThreadPool, Qt
from PySide.QtGui import QPushButton, QListWidget, QLineEdit, QLabel
from PySide.QtGui import QFileDialog, QMessageBox

from Utils import  ProgressRunnable, ProgressRunnable2, popupOnException
from PackageManager import PackageManager
from RepoConfigManager import RepoConfigManager
from ProjectConfigManager import ProjectConfigManager

from ObsLightGuiObject import ObsLightGuiObject

class ProjectManager(QObject, ObsLightGuiObject):
    '''
    Manages the local project list widget and project-related buttons
    of the main window.
    '''
    __obsProjectsListWidget = None
    __newObsProjectButton = None
    __modifyObsProjectButton = None
    __deleteObsProjectButton = None
    __loadObsProjectButton = None
    __saveObsProjectButton = None
    __newChrootButton = None
    __deleteChrootButton = None
    __addRepoInChrootButton = None
    __deleteRepoButton = None
    __modifyRepoButton = None
    __importRepoInChrootButton = None
    __projectLinkLabel = None
    __projectRepoLinkLabel = None
    __projectTitleLabel = None
    __projectLabel = None
    __chrootPathLineEdit = None
    __projectConfigManager = None
    __repoConfigManager = None
    __packageManager = None
    __statusBar = None

    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        mainWindow = self.mainWindow
        self.__obsProjectsListWidget = mainWindow.findChild(QListWidget,
                                                            u"obsProjectsListWidget")
        self.__obsProjectsListWidget.currentTextChanged.connect(self.on_projectSelected)
        self.loadProjectList()
        self.__packageManager = PackageManager(self.gui)
        self.__newObsProjectButton = mainWindow.findChild(QPushButton,
                                                          u"newObsProjectButton")
        self.__newObsProjectButton.clicked.connect(self.gui.runWizard)
        self.__modifyObsProjectButton = mainWindow.findChild(QPushButton,
                                                             u"modifyObsProjectButton")
        self.__modifyObsProjectButton.clicked.connect(self.on_modifyObsProjectButton_clicked)
        self.__deleteObsProjectButton = mainWindow.findChild(QPushButton,
                                                             u"deleteObsProjectButton")
        self.__deleteObsProjectButton.clicked.connect(self.on_deleteObsProjectButton_clicked)
        self.__loadObsProjectButton = mainWindow.findChild(QPushButton,
                                                           u"loadObsProjectButton")
        self.__loadObsProjectButton.clicked.connect(self.on_importObsProjectButton_clicked)
        self.__saveObsProjectButton = mainWindow.findChild(QPushButton,
                                                           u"saveObsProjectButton")
        self.__saveObsProjectButton.clicked.connect(self.on_exportObsProjectButton_clicked)

        self.__newChrootButton = mainWindow.findChild(QPushButton,
                                                      u"newChrootButton")
        self.__newChrootButton.clicked.connect(self.on_newChrootButton_clicked)
        self.__openChrootButton = mainWindow.findChild(QPushButton,
                                                       u"openChrootButton")
        self.__openChrootButton.clicked.connect(self.on_openChrootButton_clicked)
        self.__deleteChrootButton = mainWindow.findChild(QPushButton,
                                                         u"deleteChrootButton")
        self.__deleteChrootButton.clicked.connect(self.on_deleteChrootButton_clicked)

        self.__addRepoInChrootButton = mainWindow.findChild(QPushButton,
                                                            u"addRepoInChrootButton")
        self.__addRepoInChrootButton.clicked.connect(self.on_addRepoInChrootButton_clicked)
        self.__deleteRepoButton = mainWindow.findChild(QPushButton,
                                                       "deleteRepositoryButton")
        self.__deleteRepoButton.clicked.connect(self.on_deleteRepoButton_clicked)
        self.__modifyRepoButton = mainWindow.findChild(QPushButton,
                                                       "modifyRepositoryButton")
        self.__modifyRepoButton.clicked.connect(self.on_modifyRepoButton_clicked)
        self.__importRepoInChrootButton = mainWindow.findChild(QPushButton,
                                                               u"importRepoInChrootButton")
        self.__importRepoInChrootButton.clicked.connect(self.on_importRepoInChrootButton_clicked)
        self.__projectLinkLabel = mainWindow.findChild(QLabel,
                                                       u"projectPageLinkLabel")
        self.__projectRepoLinkLabel = mainWindow.findChild(QLabel,
                                                           u"projectRepoPageLinkLabel")
        self.__projectDescriptionLabel = mainWindow.findChild(QLabel,
                                                              u"projectDescriptionLabel")
        self.__projectTitleLabel = mainWindow.findChild(QLabel,
                                                        u"projectTitleLabel")
        self.__projectLabel = mainWindow.findChild(QLabel,
                                                   u"projectLabelValue")
        self.__chrootPathLineEdit = mainWindow.findChild(QLineEdit,
                                                         u"chrootPathLineEdit")

    def loadProjectList(self):
        '''
        Load (or reload) the local project list in the obsProjectsListWidget.
        '''
        lastCurrentProject = self.getCurrentProjectName()
        projectList = self.manager.getLocalProjectList()
        self.__obsProjectsListWidget.clear()
        self.__obsProjectsListWidget.addItems(projectList)
        if lastCurrentProject is not None and lastCurrentProject in projectList:
            self.setCurrentProject(lastCurrentProject)

    def setCurrentProject(self, projectName):
        items = self.__obsProjectsListWidget.findItems(projectName,
                                                       Qt.MatchExactly)
        if len(items) > 0:
            self.__obsProjectsListWidget.setCurrentItem(items[0])

    def getCurrentProjectName(self):
        '''
        Get the name of the project selected in the UI, or None.
        '''
        item = self.__obsProjectsListWidget.currentItem()
        if item is None:
            return None
        project = item.text()
        if project is not None and len(project) < 1:
            project = None
        return project

    @popupOnException
    def on_modifyObsProjectButton_clicked(self):
        projectName = self.getCurrentProjectName()
        if projectName is None:
            return
        self.__projectConfigManager = ProjectConfigManager(self.gui, projectName)
        self.__projectConfigManager.finished.connect(self.on_projectConfigManager_finished)

    @popupOnException
    def on_deleteObsProjectButton_clicked(self):
        projectName = self.getCurrentProjectName()
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
        progress.setLabelText(u"Deleting project...")
        progress.show()
        runnable = ProgressRunnable(self.manager.removeProject, projectName)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_importObsProjectButton_clicked(self):
        filePath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        u"Select project to import")
        if len(filePath) < 1:
            return
        progress = self.gui.getInfiniteProgressDialog()
        progress.setLabelText(u"Importing project...")
        progress.show()
        runnable = ProgressRunnable(self.manager.importProject, filePath)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_exportObsProjectButton_clicked(self):
        project = self.getCurrentProjectName()
        if project is None:
            return
        filePath, _filter = QFileDialog.getSaveFileName(self.mainWindow,
                                                        u"Select file to export")
        if len(filePath) < 1:
            return
        progress = self.gui.getInfiniteProgressDialog()
        progress.setLabelText(u"Importing project...")
        progress.show()
        runnable = ProgressRunnable(self.manager.exportProject, project, filePath)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_projectConfigManager_finished(self, success):
        if success:
            self.loadProjectList()
            self.on_projectSelected(None)

    @popupOnException
    def on_newChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
        if projectName is None or self.manager.isChRootInit(projectName):
            return
        runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
        runnable.setDialogMessage(u"Creating chroot...")
        runnable.setRunMethod(self.manager.createChRoot,
                              projectName)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished.connect(self.refreshProject)
        runnable.runOnGlobalInstance()

    @popupOnException
    def on_openChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
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
        projectName = self.getCurrentProjectName()
        if projectName is not None:
            result = QMessageBox.question(self.mainWindow,
                                      "Are you sure ?",
                                      "Are you sure you want to delete %s's chroot ?"
                                        % projectName,
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            progress = self.gui.getInfiniteProgressDialog()
            progress.setLabelText("Delete chroot")
            progress.show()
            runnable = ProgressRunnable(self.manager.removeChRoot,
                                        projectName)
            runnable.setProgressDialog(progress)
            runnable.finishedWithException.connect(self.gui.popupErrorCallback)
            runnable.finished.connect(self.refreshProject)
            QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_addRepoInChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.importFromUrl()

    @popupOnException
    def on_deleteRepoButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.deleteRepo()

    @popupOnException
    def on_modifyRepoButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.modifyRepo()

    @popupOnException
    def on_importRepoInChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__repoConfigManager = RepoConfigManager(self.gui, projectName)
        self.__repoConfigManager.importFromProject()

    def on_projectSelected(self, _project):
        self.refreshProject()

    def refreshProject(self):
        project = self.getCurrentProjectName()
        self.__packageManager.setCurrentProject(project)
        self.updateProjectLabels()
        self.updateChrootPathAndButtons()

    def refresh(self):
        self.loadProjectList()

    @popupOnException
    def updateProjectLabels(self):
        '''
        Update the different labels according to project parameters.
        '''
        project = self.getCurrentProjectName()
        if project is not None:
            projectLink = self.manager.getProjectWebPage(project)
            projectObsName = self.manager.getProjectParameter(project,
                                                                 u"projectObsName")
            target = self.manager.getProjectParameter(project, u"projectTarget")
            repoLink = self.manager.getProjectRepository(project)
            projectTitle = self.manager.getProjectParameter(project, u"projectTitle")
            projectDescription = self.manager.getProjectParameter(project, u"description")

            self.__projectLabel.setText(project)
            self.__projectTitleLabel.setText(projectTitle)
            self.__projectDescriptionLabel.setText(projectDescription)
            self.__projectLinkLabel.setText(u'<a href="%s">%s</a>' % (projectLink,
                                                                      projectObsName))
            self.__projectRepoLinkLabel.setText(u'<a href="%s">%s</a>' % (repoLink,
                                                                          target))
            self.__saveObsProjectButton.setEnabled(True)
        else:
            self.__saveObsProjectButton.setEnabled(False)

    @popupOnException
    def updateChrootPathAndButtons(self):
        '''
        Update the chroot path displayed in the main window
        with the one of the currently selected project.
        Enable/disable some buttons according to the state
        of the chroot.
        '''
        project = self.getCurrentProjectName()
        if project is not None:
            isChrootInit = self.manager.isChRootInit(project)
            if isChrootInit:
                chrootPath = self.manager.getChRootPath(project)
                self.__chrootPathLineEdit.setText(chrootPath)

                self.__newChrootButton.setEnabled(False)
                self.__openChrootButton.setEnabled(True)
            else:
                self.__newChrootButton.setEnabled(True)
                self.__openChrootButton.setEnabled(False)
                self.__chrootPathLineEdit.setText("")

            self.__addRepoInChrootButton.setEnabled(isChrootInit)
            self.__importRepoInChrootButton.setEnabled(isChrootInit)
            self.__deleteRepoButton.setEnabled(isChrootInit)
            self.__modifyRepoButton.setEnabled(isChrootInit)

            self.__deleteChrootButton.setEnabled(isChrootInit)
