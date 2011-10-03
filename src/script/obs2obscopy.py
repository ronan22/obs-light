#!/usr/bin/env python
# Authors Dominig ar Foll (Intel OTC) (first versions in Bash)
#         Florent Vennetier (Intel OTC) (third version in Python)
# Date 30 September 2011
# Version 3.0
# License GPLv2
#
# Credit Thanks to Yan Yin for providing the initial version used as a base
#

import sys
import subprocess

def help(progName="obs2obscopy"):
    print """HELP
Function : copy a project from an OBS to an OBS.
           using as input a package list with the desired MD5 to represent the package revision
           if target pakage is already at the correct revision, its copy is ignored
           running the script several time is possible until zero errors is acheived
           A log file named $MD5_FILE.log is created for everyrun.

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
          1 wrong number of arguments
          2 problem reading MD5 file
          3 network error
          4 interrupted by user

Version 3.0  License GPLv2"""  % (progName, progName, progName, progName, progName)

def main(apiUrl, srcProjectName, dstApiUrl, dstProjectName, tagFilePath):
    try:
        tagFile = open(tagFilePath, "ru")
    except IOError as e:
        print >> sys.stderr, "Cannot open", tagFilePath, ":", e.strerror
        sys.exit(2)


    print "info : Checking connectivity with remote source and local target ... "
    # TODO: read stdout to check if osc is asking for credentials
    osc = subprocess.Popen(["osc", "-A", dstApiUrl, "ls", dstProjectName],
                           stdout=subprocess.PIPE)
    osc.communicate()
    if osc.returncode != 0:
        print >> sys.stderr, "Error: Local destination project 'osc -A %s ls %s' cannot be reached"\
            % (apiUrl, dstProjectName)
        sys.exit(3)
    # TODO: read stdout to check if osc is asking for credentials
    osc = subprocess.Popen(["osc", "-A", apiUrl, "ls", srcProjectName],
                           stdout=subprocess.PIPE)
    osc.communicate()
    if osc.returncode != 0:
        print >> sys.stderr, "Error: Remote project 'osc -A %s ls %s' cannot be reached"\
            % (apiUrl, srcProjectName)
        sys.exit(3)

    for line in tagFile:
        parts = line.split("|", 4)
        md5 = parts[0].strip()
        if parts[0].startswith("#"):
            continue
        pkgName = parts[3].strip()

        osc = subprocess.Popen(["osc", "-A", dstApiUrl, "ls",
                                "--revision=%s" % md5, dstProjectName, pkgName],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        osc.communicate()
        if osc.returncode != 0:
            print "info : Copying %s from %s" % (pkgName, srcProjectName),
            osc = subprocess.Popen(["osc", "-A", apiUrl, "copypac",
                                    "--revision=%s" % md5, srcProjectName,
                                    pkgName, "-t", dstApiUrl, dstProjectName],
                                   stdout=subprocess.PIPE)
            osc.communicate()
            if osc.returncode == 0:
                print "DONE"
            else:
                print "FAILED"
        else:
            print "info : %s is already present on %s" % (pkgName,
                                                          dstProjectName)
    
    tagFile.close()
    

if __name__ == '__main__':
    try:
        if len(sys.argv) == 5:
            # Use same OBS URL as source and destination
            main(sys.argv[1], sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 6:
            main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        else:
            help(sys.argv[0])
            sys.exit(1)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupted by user..."
        sys.exit(4)
