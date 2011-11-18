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
Created on 27 sept. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QThreadPool
from PySide.QtGui import QPushButton, QListWidget, QLineEdit, QLabel
from PySide.QtGui import QFileDialog

from Utils import  ProgressRunnable, popupOnException
from PackageManager import PackageManager
from RepoConfigManager import RepoConfigManager
from ProjectConfigManager import ProjectConfigManager

class ProjectManager(QObject):
    '''
    Manages the local project list widget and project-related buttons
    of the main window.
    '''
    __gui = None
    __obsProjectsListWidget = None
    __newObsProjectButton = None
    __modifyObsProjectButton = None
    __deleteObsProjectButton = None
    __importObsProjectButton = None
    __exportObsProjectButton = None
    __createChrootButton = None
    __addRepoInChrootButton = None
    __importRpmButton = None
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
        self.__gui = gui
        mainWindow = gui.getMainWindow()
        self.__obsProjectsListWidget = mainWindow.findChild(QListWidget,
                                                            "obsProjectsListWidget")
        self.__obsProjectsListWidget.currentTextChanged.connect(self.on_projectSelected)
        self.loadProjectList()
        self.__packageManager = PackageManager(self.__gui)
        self.__newObsProjectButton = mainWindow.findChild(QPushButton,
                                                          "newObsProjectButton")
        self.__newObsProjectButton.clicked.connect(self.on_newObsProjectButton_clicked)
        self.__modifyObsProjectButton = mainWindow.findChild(QPushButton,
                                                             "modifyObsProjectButton")
        self.__modifyObsProjectButton.clicked.connect(self.on_modifyObsProjectButton_clicked)
        self.__deleteObsProjectButton = mainWindow.findChild(QPushButton,
                                                             "deleteObsProjectButton")
        self.__deleteObsProjectButton.clicked.connect(self.on_deleteObsProjectButton_clicked)
        self.__importObsProjectButton = mainWindow.findChild(QPushButton,
                                                             "importObsProjectButton")
        self.__importObsProjectButton.clicked.connect(self.on_importObsProjectButton_clicked)
        self.__exportObsProjectButton = mainWindow.findChild(QPushButton,
                                                             "exportObsProjectButton")
        self.__exportObsProjectButton.clicked.connect(self.on_exportObsProjectButton_clicked)
        self.__createChrootButton = mainWindow.findChild(QPushButton,
                                                         "createChrootButton")
        self.__createChrootButton.clicked.connect(self.on_createChrootButton_clicked)
        self.__addRepoInChrootButton = mainWindow.findChild(QPushButton,
                                                            "addRepoInChrootButton")
        self.__addRepoInChrootButton.clicked.connect(self.on_addRepoInChrootButton_clicked)
        self.__importRpmButton = mainWindow.findChild(QPushButton, "importRpmButton")
        self.__importRpmButton.clicked.connect(self.on_importRpmButton_clicked)
        self.__projectLinkLabel = mainWindow.findChild(QLabel, "projectPageLinkLabel")
        self.__projectRepoLinkLabel = mainWindow.findChild(QLabel, "projectRepoPageLinkLabel")
        self.__projectDescriptionLabel = mainWindow.findChild(QLabel, "projectDescriptionLabel")
        self.__projectTitleLabel = mainWindow.findChild(QLabel, "projectTitleLabel")
        self.__projectLabel = mainWindow.findChild(QLabel, "projectLabelValue")
        self.__chrootPathLineEdit = mainWindow.findChild(QLineEdit, "chrootPathLineEdit")

    def loadProjectList(self):
        '''
        Load (or reload) the local project list in the obsProjectsListWidget.
        '''
        projectList = self.__gui.getObsLightManager().getLocalProjectList()
        self.__obsProjectsListWidget.clear()
        self.__obsProjectsListWidget.addItems(projectList)

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
    def on_newObsProjectButton_clicked(self):
        self.__projectConfigManager = ProjectConfigManager(self.__gui)
        self.__projectConfigManager.finished.connect(self.on_projectConfigManager_finished)

    @popupOnException
    def on_modifyObsProjectButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__projectConfigManager = ProjectConfigManager(self.__gui, projectName)
        self.__projectConfigManager.finished.connect(self.on_projectConfigManager_finished)

    @popupOnException
    def on_deleteObsProjectButton_clicked(self):
        projectName = self.getCurrentProjectName()
        obslightManager = self.__gui.getObsLightManager()
        progress = self.__gui.getProgressDialog()
        progress.setLabelText("Deleting project...")
        progress.show()
        runnable = ProgressRunnable(obslightManager.removeProject, projectName)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_importObsProjectButton_clicked(self):
        filePath, _filter = QFileDialog.getOpenFileName(self.__gui.getMainWindow(),
                                                        "Select project to import")
        if len(filePath) < 1:
            return
        obslightManager = self.__gui.getObsLightManager()
        progress = self.__gui.getProgressDialog()
        progress.setLabelText("Importing project...")
        progress.show()
        runnable = ProgressRunnable(obslightManager.importProject, filePath)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_exportObsProjectButton_clicked(self):
        project = self.getCurrentProjectName()
        if project is None:
            return
        filePath, _filter = QFileDialog.getSaveFileName(self.__gui.getMainWindow(),
                                                        "Select file to export")
        if len(filePath) < 1:
            return
        progress = self.__gui.getProgressDialog()
        progress.setLabelText("Importing project...")
        progress.show()
        obslightManager = self.__gui.getObsLightManager()
        runnable = ProgressRunnable(obslightManager.exportProject, project, filePath)
        runnable.setProgressDialog(progress)
        runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
        runnable.finished.connect(self.loadProjectList)
        QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_projectConfigManager_finished(self, success):
        if success:
            self.loadProjectList()
            self.on_projectSelected(None)

    @popupOnException
    def on_createChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
        obslightManager = self.__gui.getObsLightManager()
        if projectName is not None:
            if obslightManager.isChRootInit(projectName):
                currentPackage = self.__packageManager.currentPackage()
                runnable = None
                if currentPackage is None:
                    runnable = ProgressRunnable(obslightManager.goToChRoot, projectName,
                                                detach=True)
                else:
                    runnable = ProgressRunnable(obslightManager.goToChRoot, projectName,
                                                currentPackage, detach=True)

                runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
                runnable.finished.connect(self.refresh)
                QThreadPool.globalInstance().start(runnable)
            else:
                progress = self.__gui.getProgressDialog()
                progress.setLabelText("Creating chroot")
                progress.show()
                runnable = ProgressRunnable(obslightManager.createChRoot, projectName)
                runnable.setProgressDialog(progress)
                runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
                runnable.finished.connect(self.refresh)
                QThreadPool.globalInstance().start(runnable)

    @popupOnException
    def on_addRepoInChrootButton_clicked(self):
        projectName = self.getCurrentProjectName()
        self.__repoConfigManager = RepoConfigManager(self.__gui, projectName)

    @popupOnException
    def on_importRpmButton_clicked(self):
        projectName = self.getCurrentProjectName()
        packageName = self.__packageManager.currentPackage()
        if projectName is not None and packageName is not None:
            obslightManager = self.__gui.getObsLightManager()
            progress = self.__gui.getProgressDialog()
            progress.setLabelText("Importing source in chroot")
            progress.show()
            runnable = ProgressRunnable(obslightManager.addPackageSourceInChRoot,
                                        projectName, packageName)
            runnable.setProgressDialog(progress)
            runnable.finishedWithException.connect(self.__gui.obsLightErrorCallback2)
            QThreadPool.globalInstance().start(runnable)

    def on_projectSelected(self, _project):
        project = self.getCurrentProjectName()
        self.__packageManager.setCurrentProject(project)
        self.refresh()

    def refresh(self):
        self.updateProjectLabels()
        self.updateChrootPathAndButtons()

    @popupOnException
    def updateProjectLabels(self):
        '''
        Update the different labels according to project parameters.
        '''
        project = self.getCurrentProjectName()
        if project is not None:
            obslightManager = self.__gui.getObsLightManager()
            projectLink = obslightManager.getProjectWebPage(project)
            projectObsName = obslightManager.getProjectParameter(project,
                                                                 "projectObsName")
            target = obslightManager.getProjectParameter(project, "projectTarget")
            repoLink = obslightManager.getProjectRepository(project)
            projectTitle = obslightManager.getProjectParameter(project, "projectTitle")
            projectDescription = obslightManager.getProjectParameter(project, "description")

            self.__projectLabel.setText(project)
            self.__projectTitleLabel.setText(projectTitle)
            self.__projectDescriptionLabel.setText(projectDescription)
            self.__projectLinkLabel.setText('<a href="%s">%s</a>' % (projectLink,
                                                                     projectObsName))
            self.__projectRepoLinkLabel.setText('<a href="%s">%s</a>' % (repoLink,
                                                                         target))
            self.__exportObsProjectButton.setEnabled(True)
        else:
            self.__exportObsProjectButton.setEnabled(False)

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
            obslightManager = self.__gui.getObsLightManager()
            if obslightManager.isChRootInit(project):
                chrootPath = obslightManager.getChRootPath(project)
                self.__chrootPathLineEdit.setText(chrootPath)
                self.__createChrootButton.setText("Open chroot")
                self.__addRepoInChrootButton.setEnabled(True)
                self.__importRpmButton.setEnabled(True)
            else:
                self.__createChrootButton.setText("Create chroot")
                self.__addRepoInChrootButton.setEnabled(False)
                self.__importRpmButton.setEnabled(False)
