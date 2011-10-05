#!/usr/bin/env python
# Authors Dominig ar Foll (Intel OTC) (first versions in Bash)
#         Florent Vennetier (Intel OTC) (third version in Python)
# Date 04 October 2011
# Version 3.1
# License GPLv2
#
# Credit Thanks to Yan Yin for providing the initial version used as a base
#

import sys
import urllib
import urllib2
import urlparse

from osc import conf, core

def help(progName="obs2obscopy"):
    print """HELP
Function : Copy a project from an OBS to an OBS, using as input a package list
           with the desired MD5 to represent the package revision.
           If target package is already at the correct revision, its copy
           is ignored. Running the script several time is possible until zero
           errors is acheived.
           A log file named <MD5_FILE>.log is created for everyrun.

Usage:     %s obs-alias source_prj target_prj md5_file
       or  %s obs-alias source_prj other-obs-alias target_prj md5_file
           md5_file is created by the script obstag

Example1: Local copy
       %s http://myObs.mynetwork:81 MyMeeGo:1.2:oss myTest:MeeGo:1.2:oss my_revision_tag.md5
Example2: Remote copy (by link)
       %s http://myObs.mynetwork:81 meego.com:MeeGo:1.2:oss myobs:MeeGo:1.2:oss my_revision_tag.md5
           where meego.com is a local projet which is a link to a remote OBS public api
Example3: Remote copy
       %s http://api.pub.meego.com Project:MINT:Testing http://myObs.mynetwork:81 myTest:MINT:Testing my_revision_tag.md5

Return code:
          0 success
          1 some packages not copied
          2 wrong number of arguments
          3 problem reading MD5 file or writing log file
          4 network error
          5 interrupted by user

Version 3.1  License GPLv2"""  % (progName, progName, progName, progName, progName)


def makeurl(baseurl, l, query=[]):
    """
    Replacement for `osc.core.makeurl` which preserves the "path"
    part of the url.
    """

#    if conf.config['verbose'] > 1:
#        print 'makeurl:', baseurl, l, query,

    if type(query) == type(list()):
        query = '&'.join(query)
    elif type(query) == type(dict()):
        query = urllib.urlencode(query)

    scheme, netloc, path = urlparse.urlsplit(baseurl)[0:3]
    if len(path) > 0:
        l.insert(0, path)
    finalurl = urlparse.urlunsplit((scheme, netloc, '/'.join(l), query, ''))
    if conf.config['verbose'] > 1:
        print "->", finalurl
    return finalurl


def copyproject(apiUrl, srcProjectName, dstApiUrl, dstProjectName, tagFilePath):
    totalPkg = 0
    existPkg = 0
    copiedPkg = 0
    goodPkg = 0
    failPkg = 0

    conf.get_config()
    core.makeurl = makeurl

    logFilePath = tagFilePath + ".log"
    try:
        logFile = open(logFilePath, "wu")
    except IOError as e:
        print >> sys.stderr, "Cannot open", logFilePath, ":", e.strerror
        sys.exit(3)
    try:
        tagFile = open(tagFilePath, "ru")
    except IOError as e:
        print >> sys.stderr, "Cannot open", tagFilePath, ":", e.strerror
        print >> logFile, "Cannot open", tagFilePath, ":", e.strerror
        sys.exit(3)
    message = "Copying revision version of source packages as defined in "
    message += tagFilePath
    print message
    print >> logFile, message

    print "info : Checking connectivity with target project...",
    sys.stdout.flush()
    try:
        core.meta_get_packagelist(dstApiUrl, dstProjectName)
    except KeyboardInterrupt:
        raise
    except urllib2.HTTPError as e:
        print
        message = "Error: Target project '%s' cannot be reached: %s"\
            % (dstProjectName, str(e))
        print >> sys.stderr, message
        print >> logFile, message
        sys.exit(4)
    except urllib2.URLError as e:
        print
        message = "Error: Target project '%s' cannot be reached: %s"\
            % (dstProjectName, str(e.reason))
        print >> sys.stderr, message
        print >> logFile, message
        sys.exit(4)
    print "OK"

    print "info : Checking connectivity with source project...",
    sys.stdout.flush()
    try:
        core.meta_get_packagelist(apiUrl, srcProjectName)
    except KeyboardInterrupt:
        raise
    except urllib2.HTTPError as e:
        print
        message = "Error: Source project '%s' cannot be reached: %s"\
            % (srcProjectName, str(e))
        print >> sys.stderr, message
        print >> logFile, message
        sys.exit(4)
    except urllib2.URLError as e:
        print
        message = "Error: Source project '%s' cannot be reached: %s"\
            % (srcProjectName, str(e.reason))
        print >> sys.stderr, message
        print >> logFile, message
        sys.exit(4)
    print "OK"
    
    for line in tagFile:
        parts = line.split("|", 4) # only first 4 fields are relevant

        md5 = parts[0].strip()
        if len(parts) < 4 or parts[0].startswith("#"):
            continue
        elif len(md5) < 1:
            md5 = "latest"

        totalPkg += 1
        pkgName = parts[3].strip()
        
        packagePresent = False
        try:
            fileList = core.meta_get_filelist(dstApiUrl, dstProjectName,
                                              pkgName, revision=md5)
            if len(fileList) > 0:
                packagePresent = True
        except KeyboardInterrupt:
            raise
        except urllib2.HTTPError as e:
            if e.code == 404 or e.code == 400:
                packagePresent = False
            else:
                message = "Error: Cannot list files of project '%s': %s"\
                    % (pkgName, str(e))
                print >> sys.stderr, message
                print >> logFile, message
                continue
        except Exception as e:
            message = "Error: Cannot list files of project '%s': %s"\
                % (pkgName, str(e))
            print >> sys.stderr, message
            print >> logFile, message
            continue

        if not packagePresent:
            copiedPkg += 1
            message = "info : Copying %s from %s" % (pkgName, srcProjectName)
            print message,
            print >> logFile, message,

            packageIsLink = False
            try:
                fileList = core.meta_get_filelist(apiUrl, srcProjectName, pkgName)
                if "_link" in fileList:
                    print " is a link... ",
                    print >> logFile, " is a link... ",
                    packageIsLink = True
            except Exception as e:
                message = "Error checking if %s is a link: %s" % (pkgName, str(e))
                print >> sys.stderr, message
                print >> logFile, message

            try:
                core.copy_pac(apiUrl, srcProjectName, pkgName,
                              dstApiUrl, dstProjectName, pkgName,
                              client_side_copy=(apiUrl != dstApiUrl),
                              revision=(None if packageIsLink else md5),
                              expand=packageIsLink)
                # I don't know if it can fail without returning an exception.
                # And we can't analyse the return value because it is sometimes
                # "Done." and sometimes an XML string (depending on the
                # value of parameter client_side_copy).
                goodPkg += 1
                print "DONE"
                print >> logFile, "DONE"
                
            except Exception as e:
                failPkg += 1
                print "FAILED: %s" % str(e)
                print >> logFile, "FAILED"

        else:
            existPkg += 1
            print "info : %s is already present on %s" \
                % (pkgName, dstProjectName)
            print >> logFile, "info : %s is already present on %s" \
                % (pkgName, dstProjectName)
    
    tagFile.close()

    print "Final reports"
    print "   Total packages requested     = %s" % totalPkg
    print "   Packages existing on target  = %s" % existPkg
    print "   Packages needed copying      = %s" % copiedPkg
    print "   Packages copied              = %s" % goodPkg
    print "   Packages in error            = %s" % failPkg

    print >> logFile, "Final reports"
    print >> logFile, "   Total packages requested     = %s" % totalPkg
    print >> logFile, "   Packages existing on target  = %s" % existPkg
    print >> logFile, "   Packages needed copying      = %s" % copiedPkg
    print >> logFile, "   Packages copied              = %s" % goodPkg
    print >> logFile, "   Packages in error            = %s" % failPkg
    logFile.close()
    print "Log file available in %s" % logFilePath
    if failPkg != 0:
        sys.exit(1)


if __name__ == '__main__':
    try:
        if len(sys.argv) == 5:
            # Use same OBS URL as source and destination
            copyproject(sys.argv[1], sys.argv[2], sys.argv[1],
                 sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 6:
            copyproject(sys.argv[1], sys.argv[2], sys.argv[3],
                 sys.argv[4], sys.argv[5])
        else:
            help(sys.argv[0])
            sys.exit(2)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupted by user..."
        sys.exit(5)
