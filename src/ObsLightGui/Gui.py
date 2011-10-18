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
