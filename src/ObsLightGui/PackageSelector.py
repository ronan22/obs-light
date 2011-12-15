# -*- coding: utf8 -*-
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
Created on 15 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Qt, Signal
from PySide.QtGui import QLineEdit, QListWidget

class PackageSelector(QObject):
    u"""
    Show a dialog containing a package list and a text field to enter
    a package name filter.
    """
    __gui = None

    __packageSelectionDialog = None
    __packagesListWidget = None
    __filterLineEdit = None

    packagesSelected = Signal((list))

    def __init__(self, gui):
        QObject.__init__(self)
        self.__gui = gui
        self.__loadWidgets()
        self.__makeConnections()

    def __loadWidgets(self):
        self.__packageSelectionDialog = self.__gui.loadWindow(u"obsPackageSelector.ui")
        self.__filterLineEdit = self.__packageSelectionDialog.findChild(QLineEdit,
                                                                        u"filterLineEdit")
        self.__packagesListWidget = self.__packageSelectionDialog.findChild(QListWidget,
                                                                            u"packagesListWidget")

    def __makeConnections(self):
        self.__packageSelectionDialog.accepted.connect(self.on_packageSelectionDialog_accepted)
        self.__filterLineEdit.textEdited.connect(self.on_filterLineEdit_textEdited)

    def getFilterText(self):
        u"""
        Get the current filter text.
        """
        return self.__filterLineEdit.text()

    def showPackageSelectionDialog(self, packageList):
        u"""
        Show the package selection dialog, filled with items
        of `packageList`. Returns immediately if list is empty.
        """
        if packageList is None or len(packageList) < 1:
            return
        self.__filterLineEdit.clear()
        self.__packagesListWidget.clear()
        self.__packageSelectionDialog.show()
        self.__packagesListWidget.addItems(packageList)

    def on_filterLineEdit_textEdited(self, newFilter):
        for i in range(self.__packagesListWidget.count()):
            item = self.__packagesListWidget.item(i)
            item.setHidden(True)
        for item in self.__packagesListWidget.findItems(newFilter, Qt.MatchContains):
            item.setHidden(False)

    def on_packageSelectionDialog_accepted(self):
        items = self.__packagesListWidget.selectedItems()
        packages = set()
        for item in items:
            packageName = item.text()
            packages.add(packageName)

        self.packagesSelected.emit(list(packages))
