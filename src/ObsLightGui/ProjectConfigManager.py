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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QRegExp, QThreadPool, Signal
from PySide.QtGui import QComboBox, QDialogButtonBox, QLineEdit, QRegExpValidator, QTextEdit
from PySide.QtGui import QCompleter

from ObsLight.ObsLightErr import OBSLightBaseError
from ObsLight.ObsLightUtils import isNonEmptyString
from Utils import popupOnException, colorizeWidget, removeEffect, ProgressRunnable2
from ObsLightGuiObject import ObsLightGuiObject

class ProjectConfigManager(QObject, ObsLightGuiObject):
    '''
    Manages the project configuration dialog.
    '''

    __projectAlias = None
    __obsNameCompleter = None

    __configDialog = None
    __configButtonBox = None

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
        ObsLightGuiObject.__init__(self, gui)
        self.__projectAlias = projectAlias
        self.__configDialog = self.gui.loadWindow(u"obsProjectConfig.ui")
        self.__loadFieldObjects()
        self.__loadInitialFieldValues()
        self.__makeConnections()
        if self.__isNewProject():
            self.handleServerChanged()
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        self.__configButtonBox.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self.__configDialog.show()
        self.__undefaultButtons()


    def __undefaultButtons(self):
        for button in self.__configButtonBox.buttons():
            button.setAutoDefault(False)
            button.setDefault(False)

    def __isNewProject(self):
        return self.__projectAlias is None

    def __loadFieldObjects(self):
        self.__configButtonBox = self.__configDialog.findChild(QDialogButtonBox,
                                                               u"obsProjectConfigButtonBox")
        self.__localNameField = self.__configDialog.findChild(QLineEdit,
                                                              u"projectLocalNameLineEdit")
        # obslight do not like whitespace characters
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"[^\\s:]+"))
        self.__localNameField.setValidator(noSpaceValidator)
        self.__obsNameField = self.__configDialog.findChild(QLineEdit,
                                                            u"projectObsNameLineEdit")
        self.__serverCBox = self.__configDialog.findChild(QComboBox,
                                                          u"projectServerComboBox")
        self.__targetCBox = self.__configDialog.findChild(QComboBox,
                                                          u"projectTargetComboBox")
        self.__archCBox = self.__configDialog.findChild(QComboBox,
                                                        u"projectArchitectureComboBox")
        self.__titleLineEdit = self.__configDialog.findChild(QLineEdit,
                                                             u"projectTitleLineEdit")
        self.__descriptionTextEdit = self.__configDialog.findChild(QTextEdit,
                                                                   u"projectDescriptionTextEdit")

    def __loadAliasField(self):
        self.__localNameField.setText(self.__projectAlias)
        self.__localNameField.setReadOnly(True)

    def __preselectActualServer(self):
        obsServerAlias = self.manager.getProjectParameter(self.__projectAlias,
                                                                    u"obsServer")
        lineIndex = self.__serverCBox.findText(obsServerAlias)
        if lineIndex >= 0:
            self.__serverCBox.setCurrentIndex(lineIndex)
        self.__serverCBox.setEnabled(False)

    def __loadObsNameField(self):
        projectObsName = self.manager.getProjectParameter(self.__projectAlias, u"projectObsName")
        self.__obsNameField.setText(projectObsName)
        self.__obsNameField.setReadOnly(True)

    def __preselectActualTarget(self):
        target = self.manager.getProjectParameter(self.__projectAlias, u"projectTarget")
        lineIndex = self.__targetCBox.findText(target)
        if lineIndex >= 0:
            self.__targetCBox.setCurrentIndex(lineIndex)

    def __preselectActualArch(self):
        arch = self.manager.getProjectParameter(self.__projectAlias, u"projectArchitecture")
        lineIndex = self.__archCBox.findText(arch)
        if lineIndex >= 0:
            self.__archCBox.setCurrentIndex(lineIndex)

    def __loadProjectTitle(self):
        title = self.manager.getProjectParameter(self.__projectAlias, u"title")
        self.__titleLineEdit.setText(title)
        self.__titleLineEdit.setEnabled(True)

    def __loadProjectDescription(self):
        description = self.manager.getProjectParameter(self.__projectAlias, u"description")
        self.__descriptionTextEdit.setText(description)
        self.__descriptionTextEdit.setEnabled(True)

    def __loadServerList(self, serverList):
        self.__serverCBox.clear()
        self.__serverCBox.addItems(serverList)

    def __loadKnownProjectValues(self):
        # load project local name
        self.__loadAliasField()
        # load OBS server list and select appropriate current server
        self.__preselectActualServer()
        # load project OBS name
        self.__loadObsNameField()
        # load target list and select appropriate current target
        self.__loadTargetPossibilities()
        self.__preselectActualTarget()
        # load arch list and select appropriate current arch
        self.__loadArchPossibilities()
        self.__preselectActualArch()
        # load project title
        self.__loadProjectTitle()
        # load project description
        self.__loadProjectDescription()

    def __loadInitialFieldValues(self):
        runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
        runnable.setDialogMessage("Loading...")
        runnable.setRunMethod(self.manager.getObsServerList, reachable=True)
        runnable.finished[object].connect(self.__loadServerList)
        if not self.__isNewProject():
            runnable.finished.connect(self.__loadKnownProjectValues)
        QThreadPool.globalInstance().start(runnable)

    def __makeConnections(self):
        if self.__isNewProject():
            self.__obsNameField.textEdited.connect(self.handleObsNameEdited)
            self.__obsNameField.editingFinished.connect(self.handleObsNameEditingFinished)
            self.__obsNameField.returnPressed.connect(self.handleObsNameReturnPressed)
            self.__serverCBox.currentIndexChanged.connect(self.handleServerChanged)
        self.__targetCBox.currentIndexChanged.connect(self.handleTargetIndexChanged)

    def __loadTargetPossibilities(self):
        '''
        Load the target possibilities into the target ComboBox,
        according to the current server and project.
        May take some time, so you should run it asynchronously.
        '''
        self.__archCBox.clear()
        self.__targetCBox.clear()
        if len(self.getCurrentServerAlias()) > 0 and len(self.getCurrentProjectObsName()) > 0:
            try:
                targets = self.manager.getObsProjectParameter(serverApi=self.getCurrentServerAlias(),
                                                       obsproject=self.getCurrentProjectObsName(),
                                                       parameter="repository")
                self.__targetCBox.addItems(targets)
                removeEffect(self.__obsNameField)
            except BaseException:
                colorizeWidget(self.__obsNameField, 'red')

    def __loadArchPossibilities(self):
        '''
        Load the architecture possibilities into the arch ComboBox,
        according to the current server, project and target.
        May take some time, so you should run it asynchronously.
        '''
        self.__archCBox.clear()
        if len(self.getCurrentTarget()) > 0:
            archs = self.manager.getObsProjectParameter(serverApi=self.getCurrentServerAlias(),
                                                       obsproject=self.getCurrentProjectObsName(),
                                                       parameter="arch")

            self.__archCBox.addItems(archs)

    def handleObsNameEdited(self, _ignore):
        self.__projectObsNameEdited = True

    def handleServerChanged(self):
        try:
            projectList = self.manager.getObsServerProjectList(self.getCurrentServerAlias())
            self.__obsNameCompleter = QCompleter(projectList, self.__configDialog)
            self.__obsNameField.setCompleter(self.__obsNameCompleter)
        except OBSLightBaseError:
            self.__obsNameField.setCompleter(None)
        self.handleObsNameEditingFinished()

    def handleObsNameEditingFinished(self):
        if self.__projectObsNameEdited:
            self.__projectObsNameEdited = False
            task = ProgressRunnable2()
            task.setRunMethod(self.__loadTargetPossibilities)
            QThreadPool.globalInstance().start(task)

    def handleObsNameReturnPressed(self):
        self.handleObsNameEdited(None)
        self.handleObsNameEditingFinished()

    def handleTargetIndexChanged(self):
        task = ProgressRunnable2()
        task.setRunMethod(self.__loadArchPossibilities)
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

    def validate(self):
        localName = self.getCurrentProjectLocalName()
        validated = True
        if (not isNonEmptyString(localName) or
                self.__isNewProject() and self.manager.isALocalProject(localName)):
            colorizeWidget(self.__localNameField, "red")
            validated = False
        else:
            removeEffect(self.__localNameField)

        if not isNonEmptyString(self.getCurrentProjectObsName()):
            colorizeWidget(self.__obsNameField, "red")
            validated = False
        else:
            removeEffect(self.__obsNameField)

        if not isNonEmptyString(self.getCurrentTarget()):
            colorizeWidget(self.__targetCBox, "red")
            validated = False
        else:
            removeEffect(self.__targetCBox)

        if not isNonEmptyString(self.getCurrentArch()):
            colorizeWidget(self.__archCBox, "red")
            validated = False
        else:
            removeEffect(self.__archCBox)

        if validated:
            self.__configDialog.accept()

    @popupOnException
    def on_configDialog_accepted(self):
        if self.__isNewProject():

            runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
            runnable.setDialogMessage("Importing project...")
            runnable.caughtException.connect(self.gui.popupErrorCallback)
            runnable.setRunMethod(self.manager.addProject,
                                  self.getCurrentServerAlias(),
                                  self.getCurrentProjectObsName(),
                                  self.getCurrentTarget(),
                                  self.getCurrentArch(),
                                  projectLocalName=self.getCurrentProjectLocalName())
            def emitFinished():
                self.finished.emit(True)
            runnable.finished.connect(emitFinished)
            QThreadPool.globalInstance().start(runnable)
        else:
            # Currently we can't relocate a project.
#            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                  "projectObsName",
#                                                  self.getCurrentProjectObsName())
#            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                  "obsServer",
#                                                  self.getCurrentServerAlias())
#            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                       u"projectTarget",
#                                                       self.getCurrentTarget())
#            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
#                                                       u"projectArchitecture",
#                                                       self.getCurrentArch())
            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       u"title",
                                                       self.getCurrentTitle())
            self.manager.setProjectParameter(self.getCurrentProjectLocalName(),
                                                       u"description",
                                                       self.getCurrentDescription())
            self.finished.emit(True)

    def on_configDialog_rejected(self):
        self.finished.emit(False)
