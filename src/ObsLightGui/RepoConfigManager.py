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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QThreadPool
from PySide.QtGui import QColor, QDialogButtonBox, QGraphicsColorizeEffect
from PySide.QtGui import QInputDialog, QLineEdit, QPushButton

from Utils import popupOnException, ProgressRunnable2

class RepoConfigManager(QObject):
    '''
    Manage the configuration of a repository about to be added to the chroot
    of a project. Simply asks user about repository url/alias or name of
    project to import repository from.
    '''

    __gui = None
    __projectAlias = None
    __obsLightManager = None

    __configDialog = None
    __urlLineEdit = None
    __aliasLineEdit = None
    __checkButton = None
    __repoConfigButtonBox = None

    __oldRepoAlias = None

    def __init__(self, gui, projectAlias):
        QObject.__init__(self)
        self.__gui = gui
        self.__projectAlias = projectAlias
        self.__obsLightManager = self.__gui.getObsLightManager()

    def __loadFieldObjects(self):
        self.__urlLineEdit = self.__configDialog.findChild(QLineEdit,
                                                           u"repoUrlLineEdit")
        self.__aliasLineEdit = self.__configDialog.findChild(QLineEdit,
                                                             u"repoAliasLineEdit")
        self.__checkButton = self.__configDialog.findChild(QPushButton,
                                                           "checkButton")
        self.__checkButton.clicked.connect(self.on_checkButton_clicked)
        self.__repoConfigButtonBox = self.__configDialog.findChild(QDialogButtonBox,
                                                                   "repoConfigButtonBox")
        self.__repoConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def importFromUrl(self):
        self.__configDialog = self.__gui.loadWindow(u"obsRepoConfig.ui")
        self.__loadFieldObjects()
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        self.__configDialog.show()
        self.__oldRepoAlias = None

    def importFromProject(self):
        projects = self.__obsLightManager.getLocalProjectList()
        selectedProject, accepted = QInputDialog.getItem(self.__gui.getMainWindow(),
                                                         "Select project",
                                                         "Project to import repository from:",
                                                         projects,
                                                         editable=False)
        if not accepted:
            return
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        runnable.setDialogMessage("Importing repository...")
        runnable.setRunMethod(self.__obsLightManager.addRepo,
                              self.__projectAlias,
                              fromProject=selectedProject)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def deleteRepo(self):
        repos = self.__obsLightManager.getChRootRepositories(self.__projectAlias)
        if repos is None or len(repos) < 1:
            return
        selectedAlias, accepted = QInputDialog.getItem(self.__gui.getMainWindow(),
                                                       "Select repository",
                                                       "Project repository to delete:",
                                                       repos.keys(),
                                                       editable=False)
        if not accepted:
            return
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        runnable.setDialogMessage("Deleting repository...")
        runnable.setRunMethod(self.__obsLightManager.deleteRepo,
                              self.__projectAlias,
                              selectedAlias)
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def modifyRepo(self):
        repos = self.__obsLightManager.getChRootRepositories(self.__projectAlias)
        if repos is None or len(repos) < 1:
            return
        selectedAlias, accepted = QInputDialog.getItem(self.__gui.getMainWindow(),
                                                       "Select repository",
                                                       "Project repository to modify:",
                                                       repos.keys(),
                                                       editable=False)
        if not accepted:
            return
        self.importFromUrl()
        self.__aliasLineEdit.setText(selectedAlias)
        self.__urlLineEdit.setText(repos[selectedAlias])
        self.__oldRepoAlias = selectedAlias

    def getRepoAlias(self):
        return self.__aliasLineEdit.text()

    def getRepoUrl(self):
        return self.__urlLineEdit.text()

    def on_checkButton_clicked(self):
        result = self.__obsLightManager.testServer(self.getRepoUrl())
        self.__repoConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(result)
        effect = QGraphicsColorizeEffect(self.__urlLineEdit)
        effect.setColor(QColor("green" if result else "red"))
        self.__urlLineEdit.setGraphicsEffect(effect)

    @popupOnException
    def on_configDialog_accepted(self):
        progress = self.__gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2()
        runnable.setProgressDialog(progress)
        if self.__oldRepoAlias is None:
            runnable.setDialogMessage("Importing repository in chroot...")
            runnable.setRunMethod(self.__obsLightManager.addRepo,
                                  self.__projectAlias,
                                  repoUrl=self.getRepoUrl(),
                                  alias=self.getRepoAlias())
        else:
            runnable.setDialogMessage("Modifying repository...")
            runnable.setRunMethod(self.__obsLightManager.modifyRepo,
                                  self.__projectAlias,
                                  self.__oldRepoAlias,
                                  newUrl=self.getRepoUrl(),
                                  newAlias=self.getRepoAlias())
        runnable.caughtException.connect(self.__gui.popupErrorCallback)
        QThreadPool.globalInstance().start(runnable)

    def on_configDialog_rejected(self):
        pass
