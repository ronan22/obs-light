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

class OBSLightBaseError(Exception):
    def __init__(self, args=()):
        Exception.__init__(self)
        self.args = args
    def __str__(self):
        return ''.join(self.args)


class SignalInterrupt(Exception):
    '''Exception raised on SIGTERM and SIGHUP.'''

class ArgError(OBSLightBaseError):
    '''Exception raised when there are a wrong number of arg'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

class ManagerError(OBSLightBaseError):
    '''Exception raised in Manager'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
    
class ObsLightObsServers(OBSLightBaseError):
    '''Exception raised in ObsServers'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg 

class ObsLightCommandLineError(OBSLightBaseError):
    '''Exception raised in ObsServers'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg 
   
        
class ObsLightProjectsError(OBSLightBaseError):
    '''Exception raised in ObsLightProjects'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
                          
                            
class ObsLightChRootError(OBSLightBaseError):
    ''''Exception raised in ChRoot'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg          
                            
class ObsLightSpec(OBSLightBaseError):
    ''''Exception raised in ObsLightChRootSpec'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg             
   
         
