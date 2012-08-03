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
Created on 2 juil. 2012

@author: Florent Vennetier
'''

from ObsLightPrintManager import getLogger

class ObsLightObject(object):
    """
    Mixin class currently providing `logger`.
    """

    def __init__(self):
        self.__logger = getLogger()

    @property
    def logger(self):
        """
        Get a reference to the main OBS Light logger.
        """
        return self.__logger
