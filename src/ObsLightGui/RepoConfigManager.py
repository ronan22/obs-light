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

from PySide.QtCore import QObject
from PySide.QtGui import QComboBox, QLineEdit, QRadioButton

from Utils import popupOnException

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
    __projectComboBox = None
    __urlLineEdit = None
    __aliasLineEdit = None
    __fromProjectRadio = None
    __fromUrlRadio = None

    def __init__(self, gui, projectAlias):
        QObject.__init__(self)
        self.__gui = gui
        self.__projectAlias = projectAlias
        self.__obsLightManager = self.__gui.getObsLightManager()
        self.__configDialog = self.__gui.loadWindow("obsRepoConfig.ui")
        self.__loadFieldObjects()
        self.__loadProjectPossibilities()
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        self.__configDialog.show()

    def __loadFieldObjects(self):
        self.__projectComboBox = self.__configDialog.findChild(QComboBox,
                                                               "projectComboBox")
        self.__urlLineEdit = self.__configDialog.findChild(QLineEdit,
                                                           "repoUrlLineEdit")
        self.__aliasLineEdit = self.__configDialog.findChild(QLineEdit,
                                                             "repoAliasLineEdit")
        self.__fromProjectRadio = self.__configDialog.findChild(QRadioButton,
                                                                "repoFromProjectRadioButton")
        self.__fromUrlRadio = self.__configDialog.findChild(QRadioButton,
                                                            "repoFromUrlRadioButton")

    def __loadProjectPossibilities(self):
        projects = self.__obsLightManager.getLocalProjectList()
        self.__projectComboBox.addItems(projects)

    def getRepoAlias(self):
        return self.__aliasLineEdit.text()

    def getRepoUrl(self):
        return self.__urlLineEdit.text()

    def getProject(self):
        return self.__projectComboBox.currentText()

    def addFromUrl(self):
        return self.__fromUrlRadio.isChecked()

    @popupOnException
    def on_configDialog_accepted(self):
        if self.addFromUrl():
            if len(self.getRepoUrl()) > 0 and len(self.getRepoAlias()) > 0:
                self.__obsLightManager.addRepo(self.__projectAlias,
                                               repoUrl=self.getRepoUrl(),
                                               alias=self.getRepoAlias())
        else:
            if len(self.getProject()) > 0:
                self.__obsLightManager.addRepo(self.__projectAlias,
                                               fromProject=self.getProject())

    def on_configDialog_rejected(self):
        pass
