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
Created on 3 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Qt

from ObsLightGuiObject import ObsLightGuiObject
from KickstartRepositoriesModel import KickstartRepositoriesModel

class MicProjectManager(QObject, ObsLightGuiObject):
    # pylint: disable-msg=E0202, E1101

    __projectName = ""
    __repoModel = None

    def __init__(self, gui, name):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__projectName = name
        self.__repoModel = KickstartRepositoriesModel(self.manager, self.name)

    def __loadUi(self):
        self.__loadImageType()
        self.__loadArchitecture()
        self.mainWindow.kickstartRepositoriesTableView.setModel(self.repositoryModel)

    def __loadImageType(self):
        imageTypes = self.manager.getAvailableMicProjectImageTypes(self.name)
        self.mainWindow.imageTypeComboBox.clear()
        self.mainWindow.imageTypeComboBox.addItems(imageTypes)
        index = self.mainWindow.imageTypeComboBox.findText(self.imageType,
                                                           Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.imageTypeComboBox.setCurrentIndex(index)

    def __loadArchitecture(self):
        architectures = self.manager.getAvailableMicProjectArchitectures(self.name)
        self.mainWindow.architectureComboBox.clear()
        self.mainWindow.architectureComboBox.addItems(architectures)
        index = self.mainWindow.architectureComboBox.findText(self.architecture,
                                                              Qt.MatchFixedString)
        if index >= 0:
            self.mainWindow.architectureComboBox.setCurrentIndex(index)

    @property
    def name(self):
        return self.__projectName

    @property
    def imageType(self):
        return self.manager.getMicProjectImageType(self.name)

    @imageType.setter
    def imageType(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectImageType(self.name, value)

    @property
    def architecture(self):
        return self.manager.getMicProjectArchitecture(self.name)

    @architecture.setter
    def architecture(self, value): # pylint: disable-msg=E0102
        self.manager.setMicProjectArchitecture(self.name, value)

    @property
    def repositoryModel(self):
        return self.__repoModel

    def refresh(self):
        self.__loadUi()

    def createImage(self):
        self.manager.createImage(self.name)
