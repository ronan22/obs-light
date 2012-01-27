import inspect

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0


def isBool(theBool):
    return  theBool in [True, False]


def getLineno():
    return inspect.currentframe().f_back.f_lineno

