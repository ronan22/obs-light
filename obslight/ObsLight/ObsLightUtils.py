import os
import inspect

def isNonEmptyString(theString):
    return isinstance(theString, basestring) and len(theString) > 0

def isBool(theBool):
    return  theBool in [True, False]

def isASpecFile(aFile):
    return aFile.endswith(".spec")

def getLineno():
    return inspect.currentframe().f_back.f_lineno

def getFilteredFileList(directory):
    """
    Get list of files of `directory` without those starting with '.'
    or ending with '~'.
    """
    if not os.path.isdir(directory):
        return None

    filteredFileList = []
    for f in os.listdir(directory):
        absPath = os.path.join(directory, f)
        if (os.path.isfile(absPath) and not f.startswith('.') and not f.endswith('~')):
            filteredFileList.append(f)
    return filteredFileList

# Implementation taken from http://hetland.org
def levenshtein(a, b):
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

def findBinaryPath(binary):
    """
    Find the absolute path of `binary`.
    Raise EnvironmentError if not available.
    """
    if os.environ.has_key("PATH"):
        paths = os.environ["PATH"].split(":")
    else:
        paths = []
        if os.environ.has_key("HOME"):
            paths += [os.environ["HOME"] + "/bin"]
        paths += ["/usr/local/sbin", "/usr/local/bin",
                  "/usr/sbin", "/usr/bin", "/sbin", "/bin"]

    for path in paths:
        bin_path = "%s/%s" % (path, binary)
        if os.path.exists(bin_path):
            return bin_path
    raise EnvironmentError("Command '%s' is not available." % binary)

def micIsAvailable():
    """Check if MIC is available."""
    try:
        import mic
        return True
    except ImportError:
        return False
