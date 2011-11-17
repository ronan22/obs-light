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
    msg = ""
    def __init__(self, args=()):
        Exception.__init__(self)
        self.args = args
    def __str__(self):
        return ''.join(self.args) + " " + str(self.msg)


class SignalInterrupt(Exception):
    '''Exception raised on SIGTERM and SIGHUP.'''

class ArgError(OBSLightBaseError):
    '''Exception raised when there are wrong arguments'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class ArgNumError(ArgError):
    '''Exception raised when the number of arguments is wrong'''
    def __init__(self, msg=None, command=None, argNumber=None):
        self.command = command
        self.argNumber = argNumber
        ArgError.__init__(self, self.makeMessage(msg))

    def makeMessage(self, remark=None):
        message = "Wrong number of arguments"
        if self.argNumber is not None:
            message += " (%s)" % self.argNumber
        if self.command is not None:
            message += " for command '%s'" % self.command
        if remark is not None:
            message += ": " + remark
        return message


class ArgUnknownError(ArgError):
    def __init__(self, command, param):
        self.command = command
        self.param = param
        ArgError.__init__(self, self.makeMessage())

    def makeMessage(self):
        message = "Unknown parameter"
        if self.param is not None:
            message += " '%s'" % self.param
        if self.command is not None:
            message += " for command %s" % self.command
        return message


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
    ''''Exception raised in ObsLightSpec'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

class ObsLightPackageErr(OBSLightBaseError):
    ''''Exception raised in ObsLightPackage'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

class ObsLightOscErr(OBSLightBaseError):
    ''''Exception raised in ObsLightOsc'''
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

