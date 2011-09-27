#!/usr/bin/env python
'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys
from os.path import dirname, join

from PySide.QtCore import QIODevice, QFile, QMetaObject
from PySide.QtGui import QApplication
from PySide.QtUiTools import QUiLoader

from OBSLightGuiObsProjectManager import ObsProjectManager

class Gui():
    application = None
    uiLoader = None
    mainWindow = None
    obsLightManager = None
    __obsProjectManager = None
    
    def __init__(self, obsLightManager=None):
        self.application = QApplication(sys.argv)
        self.uiLoader = QUiLoader()
        self.obsLightManager = obsLightManager
        
    def loadWindow(self, uiFile):
        path = join(dirname(__file__), "ui", uiFile)
        windowFile = QFile(path)
        windowFile.open(QIODevice.ReadOnly | QIODevice.Text)
        window = self.uiLoader.load(windowFile)
        windowFile.close()
        QMetaObject.connectSlotsByName(window)
        return window
        
    def loadMainWindow(self):
        self.mainWindow = self.loadWindow("obsLightMain.ui")
        self.mainWindow.show()

    def main(self):
        self.loadMainWindow()
        self.__obsProjectManager = ObsProjectManager(self)
        return self.application.exec_()


if __name__ == '__main__':
    gui = Gui()
    gui.main()
