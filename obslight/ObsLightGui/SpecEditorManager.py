# -*- coding: utf8 -*-
#
# Copyright 2012, Intel Inc.
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
Created on 12 dec. 2012

@author: Ronan Le Martret
'''
from FileManagerModel import FileManagerModel
from HighlighterSpecFile import Highlighter

from PySide import  QtGui

class SpecEditorManager(FileManagerModel):
    
    def __init__(self, gui, manager):
        FileManagerModel.__init__(self, gui, manager)
        mw = self.mainWindow
        mw.SaveSpecFile.clicked.connect(self.on_SaveSpecFile_clicked)
        mw.UpdateSpecFile.clicked.connect(self.on_UpdateSpecFile_clicked)
#        mw.LoadSpecFile.clicked.connect(self.on_LoadSpecFile_clicked)
        self.setupEditor()
        
        
    def setupEditor(self):
        font = QtGui.QFont()

        font.setFamily("Courier")

        font.setFixedPitch(True)

        font.setPointSize(10)


        self.mainWindow.SpecFileBrowser.setFont(font)

        self.highlighter = Highlighter(self.mainWindow.SpecFileBrowser.document())
        
        
    def on_SaveSpecFile_clicked(self):
        newSpecText= self.mainWindow.SpecFileBrowser.toPlainText()
        self.manager.setPackageParameter( self.__project, self.__package, "saveSpec",newSpecText)
    
    def on_UpdateSpecFile_clicked(self):
        self.manager.setPackageParameter( self.__project, self.__package, "updateSpec",None)
        self.loadSpecFile(self.__project, self.__package)
#    def on_LoadSpecFile_clicked(self):

#        print "on_LoadSpecFile_clicked"
    
    def loadSpecFile(self,project, package):
        self.__project=project
        self.__package=package
        
        self.mainWindow.SpecFileBrowser.setText(self.manager.getPackageParameter( project, package, "SpecTxt"))
        self.mainWindow.SpecFilePathLinkLabel.setText(self.manager.getPackageParameter( project, package, "specFilePath"))
        
        
        