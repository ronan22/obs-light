'''
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys
from os.path import dirname, join

from PySide.QtCore import QIODevice, QFile, QMetaObject
from PySide.QtGui import QApplication
from PySide.QtUiTools import QUiLoader

from OBSLight.OBSLightManager import OBSLightManager

class WindowLoader():
    _uiLoader = None
    _mainWindow = None
    
    def __init__(self):
        self._uiLoader = QUiLoader()
        
    def loadWindow(self, uiFile):
        path = join(dirname(__file__), "ui", uiFile)
        windowFile = QFile(path)
        windowFile.open(QIODevice.ReadOnly | QIODevice.Text)
        window = self._uiLoader.load(windowFile)
        windowFile.close()
        QMetaObject.connectSlotsByName(window)
        return window
        
    def loadMainWindow(self):
        self._mainWindow = self.loadWindow("obsLightMain.ui")
        self._mainWindow.show()


def main():
    app = QApplication(sys.argv)
    windowLoader = WindowLoader()
    windowLoader.loadMainWindow()
    return app.exec_()
