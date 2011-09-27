'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject
from PySide.QtGui import QPushButton, QListWidget, QLineEdit, QComboBox

class ObsProjectManager(QObject):
    '''
    classdocs
    '''
    __gui = None
    __obsProjectsListWidget = None
    __newObsProjectButton = None
    __projectConfigDialogs = []

    def __init__(self, gui):
        '''
        Constructor
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__obsProjectsListWidget = gui.mainWindow.findChild(QListWidget, "obsProjectsListWidget")
        self.__newObsProjectButton = gui.mainWindow.findChild(QPushButton, "newObsProjectButton")
        self.__newObsProjectButton.clicked.connect(self.on_newObsProjectButton_clicked)
        
    def on_newObsProject(self):
        sender = self.sender()
        projectNameLineEdit = sender.findChild(QLineEdit, "projectNameLineEdit")
        projectServerComboBox = sender.findChild(QComboBox, "projectServerComboBox")
        projectTargetComboBox = sender.findChild(QComboBox, "projectTargetComboBox")
        projectArchitectureComboBox = sender.findChild(QComboBox, "projectArchitectureComboBox")
        listEntry = projectNameLineEdit.text() + ": " + projectServerComboBox.currentText() + ", "
        listEntry += projectTargetComboBox.currentText() + ", " + projectArchitectureComboBox.currentText()
        print listEntry
        self.__obsProjectsListWidget.addItem(listEntry)
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
        
