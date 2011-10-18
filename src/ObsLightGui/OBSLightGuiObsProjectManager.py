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

from PySide.QtCore import QObject
from PySide.QtGui import QPushButton, QListView, QLineEdit, QComboBox

from ObsProjectListModel import ObsProjectListModel

class ObsProjectManager(QObject):
    '''
    classdocs
    '''
    __gui = None
    __obsProjectsListView = None
    __obsProjectListModel = None
    __newObsProjectButton = None
    __projectConfigDialogs = []

    def __init__(self, gui):
        '''
        Constructor
        '''
        QObject.__init__(self)
        self.__obsProjectListModel = ObsProjectListModel(None)
        self.__gui = gui
        self.__obsProjectsListView = gui.mainWindow.findChild(QListView, "obsProjectsListView")
        self.__obsProjectsListView.setModel(self.__obsProjectListModel)
        self.__newObsProjectButton = gui.mainWindow.findChild(QPushButton, "newObsProjectButton")
        self.__newObsProjectButton.clicked.connect(self.on_newObsProjectButton_clicked)
        self.__modifyObsProjectButton = gui.mainWindow.findChild(QPushButton, "modifyObsProjectButton")
        self.__modifyObsProjectButton.clicked.connect(self.on_modifyObsProjectButton_clicked)
        self.__deleteObsProjectButton = gui.mainWindow.findChild(QPushButton, "deleteObsProjectButton")
        self.__deleteObsProjectButton.clicked.connect(self.on_deleteObsProjectButton_clicked)
        
    def on_newObsProject(self):
        sender = self.sender()
        projectNameLineEdit = sender.findChild(QLineEdit, "projectNameLineEdit")
        projectServerComboBox = sender.findChild(QComboBox, "projectServerComboBox")
        projectTargetComboBox = sender.findChild(QComboBox, "projectTargetComboBox")
        projectArchitectureComboBox = sender.findChild(QComboBox, "projectArchitectureComboBox")
        
        self.__obsProjectListModel.addProject(projectNameLineEdit.text(),
                                              projectServerComboBox.currentText(),
                                              projectTargetComboBox.currentText(),
                                              projectArchitectureComboBox.currentText())
        self.__projectConfigDialogs.remove(sender)
        self.__gui.mainWindow.setEnabled(True)
        
    def on_modifyObsProject(self):
        sender = self.sender()
        projectNameLineEdit = sender.findChild(QLineEdit, "projectNameLineEdit")
        projectServerComboBox = sender.findChild(QComboBox, "projectServerComboBox")
        projectTargetComboBox = sender.findChild(QComboBox, "projectTargetComboBox")
        projectArchitectureComboBox = sender.findChild(QComboBox, "projectArchitectureComboBox")
        
        self.__obsProjectListModel.modifyProject(projectNameLineEdit.text(),
                                              projectServerComboBox.currentText(),
                                              projectTargetComboBox.currentText(),
                                              projectArchitectureComboBox.currentText())
        self.__projectConfigDialogs.remove(sender)
        self.__gui.mainWindow.setEnabled(True)
        
        
    def on_projectConfigDialog_rejected(self):
        sender = self.sender()
        self.__projectConfigDialogs.remove(sender)
        self.__gui.mainWindow.setEnabled(True)
        
    def on_newObsProjectButton_clicked(self):
        newProjectDialog = self.__gui.loadWindow("obsProjectConfig.ui")
        newProjectDialog.accepted.connect(self.on_newObsProject)
        newProjectDialog.rejected.connect(self.on_projectConfigDialog_rejected)
        self.__gui.mainWindow.setEnabled(False)
        newProjectDialog.show()
        self.__projectConfigDialogs.append(newProjectDialog)
        
    def on_modifyObsProjectButton_clicked(self):
        modifyProjectDialog = self.__gui.loadWindow("obsProjectConfig.ui")
        modifyProjectDialog.accepted.connect(self.on_modifyObsProject)
        modifyProjectDialog.rejected.connect(self.on_projectConfigDialog_rejected)
        projectNameField = modifyProjectDialog.findChild(QLineEdit, "projectNameLineEdit")
        projectData = self.__obsProjectListModel.data(self.__obsProjectsListView.currentIndex(), ObsProjectListModel.dataRole)
        projectNameField.setText(projectData["name"])
        projectNameField.setReadOnly(True)
        self.__gui.mainWindow.setEnabled(False)
        modifyProjectDialog.show()
        self.__projectConfigDialogs.append(modifyProjectDialog)
        
    def on_deleteObsProjectButton_clicked(self):
        projectData = self.__obsProjectListModel.data(self.__obsProjectsListView.currentIndex(), ObsProjectListModel.dataRole)
        self.__obsProjectListModel.deleteProject(projectData["name"])
