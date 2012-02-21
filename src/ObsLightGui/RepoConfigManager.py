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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QThreadPool
from PySide.QtGui import QDialogButtonBox, QInputDialog

from Utils import popupOnException, ProgressRunnable2, colorizeWidget
from ObsLightGuiObject import ObsLightGuiObject

class RepoConfigManager(QObject, ObsLightGuiObject):
    """
    Manage the configuration of a repository about to be added to the file system
    of a project. Simply asks user about repository url/alias or name of
    project to import repository from.
    """

    def __init__(self, gui, projectAlias):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectAlias = projectAlias
        self.__configDialog = None
        self.__oldRepoAlias = None

    def importFromUrl(self):
        """
        Run this method in order to add a repository from an URL.
        """
        self.__configDialog = self.gui.loadWindow(u"obsRepoConfig.ui")
        self.__configDialog.checkButton.clicked.connect(self.on_checkButton_clicked)
        self.__configDialog.repoConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        self.__configDialog.show()
        self.__oldRepoAlias = None

    def importFromProject(self):
        """
        Run this method in order to add the repository of another OBS project.
        """
        projects = self.manager.getLocalProjectList()
        selectedProject, accepted = QInputDialog.getItem(self.mainWindow,
                                                         "Select project",
                                                         "Project to import repository from:",
                                                         projects,
                                                         editable=False)
        if not accepted:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        runnable.setDialogMessage("Importing repository...")
        runnable.setRunMethod(self.manager.addRepo,
                              self.__projectAlias,
                              fromProject=selectedProject)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def deleteRepo(self):
        """
        Run this method to remove a repository from the project file system.
        """
        repos = self.manager.getChRootRepositories(self.__projectAlias)
        if repos is None or len(repos) < 1:
            return
        selectedAlias, accepted = QInputDialog.getItem(self.mainWindow,
                                                       "Select repository",
                                                       "Project repository to delete:",
                                                       repos.keys(),
                                                       editable=False)
        if not accepted:
            return
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        runnable.setDialogMessage("Deleting repository...")
        runnable.setRunMethod(self.manager.deleteRepo,
                              self.__projectAlias,
                              selectedAlias)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def modifyRepo(self):
        """
        Run this method to modify the URL or alias of a repository.
        """
        repos = self.manager.getChRootRepositories(self.__projectAlias)
        if repos is None or len(repos) < 1:
            return
        selectedAlias, accepted = QInputDialog.getItem(self.mainWindow,
                                                       "Select repository",
                                                       "Project repository to modify:",
                                                       repos.keys(),
                                                       editable=False)
        if not accepted:
            return
        self.importFromUrl()
        self.__configDialog.repoAliasLineEdit.setText(selectedAlias)
        self.__configDialog.repoUrlLineEdit.setText(repos[selectedAlias])
        self.__oldRepoAlias = selectedAlias

    def getRepoAlias(self):
        return self.__configDialog.repoAliasLineEdit.text()

    def getRepoUrl(self):
        return self.__configDialog.repoUrlLineEdit.text()

    def on_checkButton_clicked(self):
        urlColor = "green"
        aliasColor = "green"
        alias = self.getRepoAlias()
        url = self.getRepoUrl()
        scd = self.__configDialog

        resultUrl = self.manager.testUrl(url)
        if not resultUrl:
            if self.manager.testHost(url):
                urlColor = "orange"
            else:
                urlColor = "red"
        else:
            url, alias = self.manager.testRepo(url, alias)
            if url != None:
                scd.repoUrlLineEdit.setText(url)
            if alias != None:
                scd.repoAliasLineEdit.setText(alias)
            if (url is not None) and (not len(url) < 1):
                resultUrl = self.manager.testUrlRepo(url)
                if not resultUrl:
                    urlColor = "orange"
            else:
                urlColor = "red"
                resultUrl = False

        currentRepos = self.manager.getChRootRepositories(self.__projectAlias)

        resultAlias = not (alias is None or
                          len(alias) < 1 or
                          (alias in currentRepos and alias != self.__oldRepoAlias))

        if not resultAlias :
            aliasColor = "red"

        colorizeWidget(scd.repoUrlLineEdit, urlColor)
        colorizeWidget(scd.repoAliasLineEdit, aliasColor)
        scd.repoConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(resultUrl and
                                                                       resultAlias)

    @popupOnException
    def on_configDialog_accepted(self):
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        if self.__oldRepoAlias is None:
            runnable.setDialogMessage("Importing repository in project file system...")
            runnable.setRunMethod(self.manager.addRepo,
                                  self.__projectAlias,
                                  repoUrl=self.getRepoUrl(),
                                  alias=self.getRepoAlias())
        else:
            runnable.setDialogMessage("Modifying repository...")
            runnable.setRunMethod(self.manager.modifyRepo,
                                  self.__projectAlias,
                                  self.__oldRepoAlias,
                                  newUrl=self.getRepoUrl(),
                                  newAlias=self.getRepoAlias())
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def on_configDialog_rejected(self):
        pass
