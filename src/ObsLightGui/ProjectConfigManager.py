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

from PySide.QtCore import QObject, QThreadPool, Signal
from PySide.QtGui import QDialogButtonBox, QRegExpValidator
from PySide.QtGui import QCompleter

from ObsLight.ObsLightErr import OBSLightBaseError
from ObsLight.ObsLightUtils import isNonEmptyString
from Utils import popupOnException, colorizeWidget, removeEffect, ProgressRunnable2
from Utils import PROJECT_ALIAS_REGEXP
from ObsLightGuiObject import ObsLightGuiObject

class ProjectConfigManager(QObject, ObsLightGuiObject):
    '''
    Manages the OBS project configuration dialog.
    '''

    finished = Signal(bool)

    def __init__(self, gui, projectAlias=None):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectAlias = projectAlias
        self.__configDialog = self.gui.loadWindow(u"obsProjectConfig.ui")
        self.__projectObsNameEdited = False

        # obslight do not like whitespace characters
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(PROJECT_ALIAS_REGEXP)
        self.__configDialog.projectLocalNameLineEdit.setValidator(noSpaceValidator)

        self.__obsNameCompleter = None
        self.__loadInitialFieldValues()
        self.__makeConnections()
        if self.__isNewProject():
            self.handleServerChanged()
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.rejected.connect(self.on_configDialog_rejected)
        obsProjectConfigButtonBox = self.__configDialog.obsProjectConfigButtonBox
        obsProjectConfigButtonBox.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self.__configDialog.show()
        self.__undefaultButtons()


    def __undefaultButtons(self):
        for button in self.__configDialog.obsProjectConfigButtonBox.buttons():
            button.setAutoDefault(False)
            button.setDefault(False)

    def __isNewProject(self):
        return self.__projectAlias is None

    def __loadAliasField(self):
        self.__configDialog.projectLocalNameLineEdit.setText(self.__projectAlias)
        self.__configDialog.projectLocalNameLineEdit.setReadOnly(True)

    def __preselectActualServer(self):
        obsServerAlias = self.manager.getProjectParameter(self.__projectAlias,
                                                                    u"obsServer")
        lineIndex = self.__configDialog.projectServerComboBox.findText(obsServerAlias)
        if lineIndex >= 0:
            self.__configDialog.projectServerComboBox.setCurrentIndex(lineIndex)
        self.__configDialog.projectServerComboBox.setEnabled(False)

    def __loadObsNameField(self):
        projectObsName = self.manager.getProjectParameter(self.__projectAlias, u"projectObsName")
        self.__configDialog.projectObsNameLineEdit.setText(projectObsName)
        self.__configDialog.projectObsNameLineEdit.setReadOnly(True)

    def __preselectActualTarget(self):
        target = self.manager.getProjectParameter(self.__projectAlias, u"projectTarget")
        lineIndex = self.__configDialog.projectTargetComboBox.findText(target)
        if lineIndex >= 0:
            self.__configDialog.projectTargetComboBox.setCurrentIndex(lineIndex)

    def __preselectActualArch(self):
        arch = self.manager.getProjectParameter(self.__projectAlias, u"projectArchitecture")
        lineIndex = self.__configDialog.projectArchitectureComboBox.findText(arch)
        if lineIndex >= 0:
            self.__configDialog.projectArchitectureComboBox.setCurrentIndex(lineIndex)

    def __loadProjectTitle(self):
        title = self.manager.getProjectParameter(self.__projectAlias, u"title")
        self.__configDialog.projectTitleLineEdit.setText(title)
        self.__configDialog.projectTitleLineEdit.setEnabled(True)

    def __loadProjectDescription(self):
        description = self.manager.getProjectParameter(self.__projectAlias, u"description")
        self.__configDialog.projectDescriptionTextEdit.setText(description)
        self.__configDialog.projectDescriptionTextEdit.setEnabled(True)

    def __loadServerList(self, serverList):
        self.__configDialog.projectServerComboBox.clear()
        self.__configDialog.projectServerComboBox.addItems(serverList)

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
        scd = self.__configDialog
        if self.__isNewProject():
            scd.projectObsNameLineEdit.textEdited.connect(self.handleObsNameEdited)
            scd.projectObsNameLineEdit.editingFinished.connect(self.handleObsNameEditingFinished)
            scd.projectObsNameLineEdit.returnPressed.connect(self.handleObsNameReturnPressed)
            scd.projectServerComboBox.currentIndexChanged.connect(self.handleServerChanged)
        scd.projectTargetComboBox.currentIndexChanged.connect(self.handleTargetIndexChanged)

    def __loadTargetPossibilities(self):
        '''
        Load the target possibilities into the target ComboBox,
        according to the current server and project.
        May take some time, so you should run it asynchronously.
        '''
        self.__configDialog.projectArchitectureComboBox.clear()
        self.__configDialog.projectTargetComboBox.clear()
        if len(self.getCurrentServerAlias()) > 0 and len(self.getCurrentProjectObsName()) > 0:
            try:
                targets = self.manager.getObsProjectParameter(self.getCurrentServerAlias(),
                                                              self.getCurrentProjectObsName(),
                                                              parameter="repository")
                self.__configDialog.projectTargetComboBox.addItems(targets)
                removeEffect(self.__configDialog.projectObsNameLineEdit)
            except BaseException:
                colorizeWidget(self.__configDialog.projectObsNameLineEdit, 'red')

    def __loadArchPossibilities(self):
        '''
        Load the architecture possibilities into the arch ComboBox,
        according to the current server, project and target.
        May take some time, so you should run it asynchronously.
        '''
        self.__configDialog.projectArchitectureComboBox.clear()
        if len(self.getCurrentTarget()) > 0:
            archs = self.manager.getObsProjectParameter(serverApi=self.getCurrentServerAlias(),
                                                       obsproject=self.getCurrentProjectObsName(),
                                                       parameter="arch")

            self.__configDialog.projectArchitectureComboBox.addItems(archs)

    def handleObsNameEdited(self, _ignore):
        self.__projectObsNameEdited = True

    def handleServerChanged(self):
        try:
            projectList = self.manager.getObsServerProjectList(self.getCurrentServerAlias())
            self.__obsNameCompleter = QCompleter(projectList, self.__configDialog)
            self.__configDialog.projectObsNameLineEdit.setCompleter(self.__obsNameCompleter)
        except OBSLightBaseError:
            self.__configDialog.projectObsNameLineEdit.setCompleter(None)
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
        return self.__configDialog.projectServerComboBox.currentText()

    def getCurrentProjectLocalName(self):
        return self.__configDialog.projectLocalNameLineEdit.text()

    def getCurrentProjectObsName(self):
        return self.__configDialog.projectObsNameLineEdit.text()

    def getCurrentTarget(self):
        return self.__configDialog.projectTargetComboBox.currentText()

    def getCurrentArch(self):
        return self.__configDialog.projectArchitectureComboBox.currentText()

    def getCurrentTitle(self):
        return self.__configDialog.projectTitleLineEdit.text()

    def getCurrentDescription(self):
        return self.__configDialog.projectDescriptionTextEdit.toPlainText()

    def validate(self):
        localName = self.getCurrentProjectLocalName()
        validated = True
        if (not isNonEmptyString(localName) or
                self.__isNewProject() and self.manager.isALocalProject(localName)):
            colorizeWidget(self.__configDialog.projectLocalNameLineEdit, "red")
            validated = False
        else:
            removeEffect(self.__configDialog.projectLocalNameLineEdit)

        if not isNonEmptyString(self.getCurrentProjectObsName()):
            colorizeWidget(self.__configDialog.projectObsNameLineEdit, "red")
            validated = False
        else:
            removeEffect(self.__configDialog.projectObsNameLineEdit)

        if not isNonEmptyString(self.getCurrentTarget()):
            colorizeWidget(self.__configDialog.projectTargetComboBox, "red")
            validated = False
        else:
            removeEffect(self.__configDialog.projectTargetComboBox)

        if not isNonEmptyString(self.getCurrentArch()):
            colorizeWidget(self.__configDialog.projectArchitectureComboBox, "red")
            validated = False
        else:
            removeEffect(self.__configDialog.projectArchitectureComboBox)

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
