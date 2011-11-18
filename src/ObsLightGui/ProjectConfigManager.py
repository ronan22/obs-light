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

from PySide.QtCore import QObject, QRegExp, QThreadPool, Signal
from PySide.QtGui import QComboBox, QLineEdit, QRegExpValidator, QTextEdit

from Utils import popupOnException, QRunnableImpl

class ProjectConfigManager(QObject):
    '''
    Manages the project configuration dialog.
    '''

    __gui = None
    __projectAlias = None
    __obsLightManager = None
    __configDialog = None

    __localNameField = None
    __obsNameField = None
    __serverCBox = None
    __targetCBox = None
    __archCBox = None
    __titleLineEdit = None
    __descriptionTextEdit = None

    finished = Signal(bool)
    __projectObsNameEdited = False

    def __init__(self, gui, projectAlias=None):
        QObject.__init__(self)
        self.__gui = gui
        self.__projectAlias = projectAlias
        self.__obsLightManager = self.__gui.getObsLightManager()
        self.__configDialog = self.__gui.loadWindow("obsProjectConfig.ui")
        self.__loadFieldObjects()
        self.__loadInitialFieldValues()
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        self.__configDialog.show()

    def __isNewProject(self):
        return self.__projectAlias is None

    def __loadFieldObjects(self):
        self.__localNameField = self.__configDialog.findChild(QLineEdit,
                                                              "projectLocalNameLineEdit")
        # obslight do not like whitespace characters
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp("\\S+"))
        self.__localNameField.setValidator(noSpaceValidator)
        self.__obsNameField = self.__configDialog.findChild(QLineEdit,
                                                            "projectObsNameLineEdit")
        self.__obsNameField.textEdited.connect(self.handleObsNameEdited)
        self.__obsNameField.editingFinished.connect(self.handleObsNameEditingFinished)
        self.__serverCBox = self.__configDialog.findChild(QComboBox,
                                                          "projectServerComboBox")
        self.__serverCBox.currentIndexChanged.connect(self.handleObsNameEditingFinished)
        self.__targetCBox = self.__configDialog.findChild(QComboBox,
                                                          "projectTargetComboBox")
        self.__targetCBox.currentIndexChanged.connect(self.handleTargetIndexChanged)
        self.__archCBox = self.__configDialog.findChild(QComboBox,
                                                        "projectArchitectureComboBox")
        self.__titleLineEdit = self.__configDialog.findChild(QLineEdit,
                                                             "projectTitleLineEdit")
        self.__descriptionTextEdit = self.__configDialog.findChild(QTextEdit,
                                                                   "projectDescriptionTextEdit")

    def __loadInitialFieldValues(self):
        self.__serverCBox.clear()
        self.__serverCBox.addItems(self.__obsLightManager.getObsServerList(reachable=True))

        if not self.__isNewProject():
            # load project local name
            self.__localNameField.setText(self.__projectAlias)
            self.__localNameField.setReadOnly(True)
            # load OBS server list and select appropriate current server
            obsServerAlias = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                                        "obsServer")
            lineIndex = self.__serverCBox.findText(obsServerAlias)
            if lineIndex >= 0:
                self.__serverCBox.setCurrentIndex(lineIndex)
            self.__serverCBox.setEnabled(False)
            # load project OBS name
            projectObsName = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                                        "projectObsName")
            self.__obsNameField.setText(projectObsName)
            self.__obsNameField.setReadOnly(True)
            # load target list and select appropriate current target
            self.__loadTargetPossibilities()
            target = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                                "projectTarget")
            lineIndex = self.__targetCBox.findText(target)
            if lineIndex >= 0:
                self.__targetCBox.setCurrentIndex(lineIndex)
            # load arch list and select appropriate current arch
            self.__loadArchPossibilities()
            arch = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                              "projectArchitecture")
            lineIndex = self.__archCBox.findText(arch)
            if lineIndex >= 0:
                self.__archCBox.setCurrentIndex(lineIndex)
            # load project title
            title = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                               "projectTitle")
            self.__titleLineEdit.setText(title)
            self.__titleLineEdit.setEnabled(True)
            # load project description
            description = self.__obsLightManager.getProjectParameter(self.__projectAlias,
                                                                     "description")
            self.__descriptionTextEdit.setText(description)
            self.__descriptionTextEdit.setEnabled(True)

    def __loadTargetPossibilities(self):
        '''
        Load the target possibilities into the target ComboBox,
        according to the current server and project.
        May take some time, so you should run it asynchronously.
        '''
        self.__targetCBox.clear()
        if len(self.getCurrentServerAlias()) > 0 and len(self.getCurrentProjectObsName()) > 0:
            targets = self.__obsLightManager.getTargetList(self.getCurrentServerAlias(),
                                                           self.getCurrentProjectObsName())
            self.__targetCBox.addItems(targets)

    def __loadArchPossibilities(self):
        '''
        Load the architecture possibilities into the arch ComboBox,
        according to the current server, project and target.
        May take some time, so you should run it asynchronously.
        '''
        self.__archCBox.clear()
        if len(self.getCurrentTarget()) > 0:
            archs = self.__obsLightManager.getArchitectureList(self.getCurrentServerAlias(),
                                                               self.getCurrentProjectObsName(),
                                                               self.getCurrentTarget())
            self.__archCBox.addItems(archs)

    def handleObsNameEdited(self, _ignore):
        self.__projectObsNameEdited = True

    def handleObsNameEditingFinished(self):
        if self.__projectObsNameEdited:
            self.__projectObsNameEdited = False
            task = QRunnableImpl()
            task.run = self.__loadTargetPossibilities
            QThreadPool.globalInstance().start(task)

    def handleTargetIndexChanged(self):
        task = QRunnableImpl()
        task.run = self.__loadArchPossibilities
        QThreadPool.globalInstance().start(task)

    def getCurrentServerAlias(self):
        return self.__serverCBox.currentText()

    def getCurrentProjectLocalName(self):
        return self.__localNameField.text()

    def getCurrentProjectObsName(self):
        return self.__obsNameField.text()

    def getCurrentTarget(self):
        return self.__targetCBox.currentText()

    def getCurrentArch(self):
        return self.__archCBox.currentText()

    def getCurrentTitle(self):
        return self.__titleLineEdit.text()

    def getCurrentDescription(self):
        return self.__descriptionTextEdit.toPlainText()

    @popupOnException
    def on_configDialog_accepted(self):
        if self.__isNewProject():
            self.__obsLightManager.addProject(self.getCurrentServerAlias(),
                                              self.getCurrentProjectObsName(),
                                              self.getCurrentTarget(),
                                              self.getCurrentArch(),
                                              projectLocalName=self.getCurrentProjectLocalName())
        else:
            # Currently we can't relocate a project.
#            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                  "projectObsName",
#                                                  self.getCurrentProjectObsName())
#            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                  "obsServer",
#                                                  self.getCurrentServerAlias())
            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       "projectTarget",
                                                       self.getCurrentTarget())
            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       "projectArchitecture",
                                                       self.getCurrentArch())
            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       "projectTitle",
                                                       self.getCurrentTitle())
            self.__obsLightManager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       "description",
                                                       self.getCurrentDescription())
        self.finished.emit(True)

    def on_configDialog_rejected(self):
        self.finished.emit(False)