# Copyright (C) 2008 Novell Inc.  All rights reserved.
# This program is free software; it may be used, copied, modified
# and distributed under the terms of the GNU General Public Licence,
# either version 2, or (at your option) any later version.



class OBSLightBaseError(Exception):
    def __init__(self, args=()):
        Exception.__init__(self)
        self.args = args
    def __str__(self):
        return ''.join(self.args)


class SignalInterrupt(Exception):
    """Exception raised on SIGTERM and SIGHUP."""

class ArgError(OBSLightBaseError):
    """Exception raised when there are a wrong number of arg"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

class ManagerError(OBSLightBaseError):
    """Exception raised in Manager"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
        
class OBSLightProjectsError(OBSLightBaseError):
    """Exception raised in OBSLightProjects"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg

#added by Gustav        
class XMLExistenceError(OBSLightBaseError):
    """Exception raised if the XML file does not exist"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
        
#added by Gustav        
class XMLEmptyFileError(OBSLightBaseError):
    """Exception raised if the XML file is empty"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
    
#added by Gustav        
class XMLParseFileError(OBSLightBaseError):
    """Exception raised if the XML file is empty"""
    def __init__(self, msg):
        OBSLightBaseError.__init__(self)
        self.msg = msg
    



        
        