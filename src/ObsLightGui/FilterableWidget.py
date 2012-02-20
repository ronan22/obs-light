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
from PySide.QtGui import QAbstractItemView

class FilterableWidget(object):
    """
    This class manages the filtering of a QListWidget.
    When the user enters text in the provided QLineEdit, QListWidget
    entries not matching this text are hidden (but keep their selection
    state).
    """

    filterLineEdit = None
    filterableListWidget = None

    def __init__(self, filterLineEdit, filterableListWidget, multiSelection=False):
        """
        Initialize the FilterableWidget with `filterLineEdit`
        (`QtGui.QLineEdit`) as source for the filter, `filterableListWidget`
        (`QtGui.QListWidget`) as the widget to filter items.
        If `multiSelection` is True, set the selection mode of
        `filterableListWidget` to `QAbstractItemView.MultiSelection`.
        """
        self.filterLineEdit = filterLineEdit
        self.filterableListWidget = filterableListWidget
        if multiSelection:
            self.filterableListWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.filterLineEdit.textEdited.connect(self.on_filterLineEdit_textEdited)

    def on_filterLineEdit_textEdited(self, newFilter):
        """
        Do filter the `QtGui.QListWidget` entries using `newFilter` as
        filter and `Qt.MatchContains` as filtering mode.
        """
        for i in range(self.filterableListWidget.count()):
            item = self.filterableListWidget.item(i)
            item.setHidden(True)
        for item in self.filterableListWidget.findItems(newFilter, Qt.MatchContains):
            item.setHidden(False)
