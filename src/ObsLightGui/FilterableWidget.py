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
Created on 22 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import Qt

class FilterableWidget(object):

    filterLineEdit = None
    filterableListWidget = None

    def __init__(self, filterLineEdit, filterableListWidget):
        self.filterLineEdit = filterLineEdit
        self.filterableListWidget = filterableListWidget
        self.filterLineEdit.textEdited.connect(self.on_filterLineEdit_textEdited)

    def on_filterLineEdit_textEdited(self, newFilter):
        for i in range(self.filterableListWidget.count()):
            item = self.filterableListWidget.item(i)
            item.setHidden(True)
        for item in self.filterableListWidget.findItems(newFilter, Qt.MatchContains):
            item.setHidden(False)
