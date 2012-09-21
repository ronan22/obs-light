#
# Copyright 2011-2012, Intel Inc.
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
Created on 21 sept. 2012

@author: Ronan Le Martret 
'''
from ObsLightBuilderProject import ObsLightBuilderProject

class ObsLightProject(ObsLightBuilderProject):

    def __init__(self,
                 obsServers,
                 obsLightRepositories,
                 workingDirectory,
                 projectObsName=None,
                 projectLocalName=None,
                 obsServer=None,
                 projectTarget=None,
                 projectArchitecture=None,
                 projectTitle="",
                 description="",
                 fromSave={}):
        ObsLightProjectCore.__init__(self,
                             obsServers,
                             obsLightRepositories,
                             workingDirectory,
                             projectObsName=projectObsName,
                             projectLocalName=projectLocalName,
                             obsServer=obsServer,
                             projectTarget=projectTarget,
                             projectArchitecture=projectArchitecture,
                             projectTitle=projectTitle,
                             description=description,
                             fromSave=fromSave)
