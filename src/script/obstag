#!/usr/bin/env python
# Authors Dominig ar Foll (Intel OTC) (first versions in Bash)
#         Florent Vennetier (Intel OTC) (third version in Python)
# Date 29 September 2011
# Version 3.0
# License GPLv2

import sys
import time

from os.path import join
from urllib2 import URLError, HTTPError
from xml.etree import ElementTree

from osc import conf, core


def help(progName="obstag"):
    print """HELP
Function : Tag a project in an OBS (remote obs are managed via a linked project)
        It will create a tag file which constains the MD5 to represent
        the package revision. The tag file can be used as direct input
        for obs2obsCopy.

Usage:   """ + progName + """ obs-alias project-name md5_file-name
Example: """ + progName + """ http://myObs.mynetwork:81 meego.com:MeeGo:1.2:oss my_revision_tag.md5

        meego.com can be a local projet which is a link to a remote OBS
        public API. Public API does NOT provide log info and in that case
        revision info will be empty. obs2obscopy will then copy the current
        release.

Version 3.0   License GLPv2"""


class PackageRevision(object):
    """
    Reflects the content of a <revision> tag as returned by a 
    'GET /source/<project>/<package>/_history' call on an OBS project package.
    """

    def __init__(self, packageName, rev, vrev):
        self.name = packageName
        self.rev = rev
        self.vrev = vrev
        self.srcmd5 = ""
        self.time = "0"
        self.version = ""
        self.user = ""
        self.comment = "<no message>"

    def __str__(self):
        """
        Simply calls self.__repr__()
        """
        return self.__repr__()

    def __repr__(self):
        """
        Returns a string suitable for obs2obscopy input
        """
        date = time.localtime(int(self.time))
        s = "%(srcmd5)40s | %(rev)6s | " % self.__dict__
        s += "%20s | " % time.strftime("%Y-%m-%d %H:%M:%S", date)
        s += "%(name)s | %(version)s |%(user)s |%(comment)s " % self.__dict__
        return s

    def __cmp__(self, other):
        if self.name == other.name:
            return cmp(int(self.rev) or 0, int(other.rev) or 0)
        else:
            return cmp(self.name, other.name)
        

class ObsProject(object):

    def __init__(self, apiUrl, projectName):
        self.name = projectName
        self.apiUrl = apiUrl
        self.obsConfig = conf.get_config()

    def getPackageList(self):
        """
        Returns the list of all package names of this project.
        Can raise `urllib2.HTTPError`, `urllib2.URLError` or `ElementTree.ParseError`.
        """
        # The following method does not work on public repositories :
        #   core.meta_get_packagelist(self.apiUrl, self.name)
        # This is why we have to use the WEB API and parse XML ourselves.
        url = self.apiUrl + "/source/" + self.name + "/"
        xmlResult = core.http_request("GET", url).read()
        packageList = list()
        xmlPackageDir = ElementTree.fromstring(xmlResult)
        for packageEntry in xmlPackageDir.iter("entry"):
            packageList.append(packageEntry.get("name"))
        return packageList

    def getPackageRevisions(self, packageName):
        """
        Returns a list of `PackageRevision` of packageName.
        Can raise `urllib2.HTTPError`, `urllib2.URLError` or `ElementTree.ParseError`.
        """
        revisionsList = list()
        url = self.apiUrl + "/source/" + self.name + "/"
        url += packageName + "/_history"

        xmlResult = core.http_request("GET", url).read()
        
        xmlRevisionLists = ElementTree.fromstring(xmlResult)
        for xmlRevisionList in xmlRevisionLists.iter("revisionlist"):
            for xmlRevision in xmlRevisionList.iter("revision"):
                revision = PackageRevision(packageName,
                                           xmlRevision.get("rev", 1),
                                           xmlRevision.get("vrev", 1))
                for field in xmlRevision.iter():
                    revision.__dict__[field.tag] = field.text
                revisionsList.append(revision)
        
        revisionsList.sort(reverse=True)
        return revisionsList


def main(apiUrl, projectName, outFilePath):
    try:
        outFile = open(outFilePath, "wu+", 1)
    except IOError as err:
        print >> sys.stderr, "Cannot write", outFilePath, ":", err.strerror
        sys.exit(3)

    print >> outFile, "# This is a revision Tag file from an OBS project created by obstag."
    print >> outFile, "# That MD5 Tag is directly usable by obs2obscopy script."
    print >> outFile, "#"
    print >> outFile, "# Created :", time.strftime("%a, %b %d %H:%M:%S %Z %Y")
    print >> outFile, "# Project name : %s" % projectName
    print >> outFile, "#"
    print >> outFile, "# %38s | %6s | %20s | %s | %s |%s |%s " \
                  % ("pkgMd5", "pkgRev", "pkgDate", "pkgName", "pkgVersion",
                     "pkgOwner", "pkgComment")
    print >> outFile, "#"
    obsProject = ObsProject(apiUrl, projectName)

    packageList = list()
    try:
        packageList = obsProject.getPackageList()
    except HTTPError as e:
        print >> sys.stderr, "An error occured while retrieving package list: ", str(e)
        sys.exit(1)
    except URLError:
        print >> sys.stderr, "The URL you gave seems to be invalid or unreachable:", apiUrl
        sys.exit(1)
    except ElementTree.ParseError:
        print >> sys.stdout, "An error occured while parsing package list:", str(pe)
        sys.exit(2)

    if len(packageList) < 1:
        print "No package found in project %s !", projectName
        sys.exit(0)


    print "Creating a revision tag of source packages as present in ", projectName
    packagesTaggedNumber = 0
    try:
        for packageName in packageList:
            try:
                revisions = obsProject.getPackageRevisions(packageName)
                if len(revisions) > 0:
                    print >> outFile, revisions[0]
                    # 'print' writes an unwanted space between the dots
                else:
                    rev = PackageRevision(packageName, "", "")
                    print >> outFile, rev
                sys.stdout.write(".")
                sys.stdout.flush()
                packagesTaggedNumber += 1
            except ElementTree.ParseError as pe:
                print >> sys.stdout, "An error occured while parsing revision"\
                    + " list of package ", packageName, ":", str(pe)
    except HTTPError as e:
        print >> sys.stderr, "An error occured while retrieving package list:",
        print >> sys.stderr, str(e)
        sys.exit(1)
    except URLError:
        print >> sys.stderr, "The URL you gave seems to be invalid or",
        print >> sys.stderr, " unreachable:", self.apiUrl
        sys.exit(1)

    outFile.close()

    print "\nFinal reports"
    print "   Total number packages tagged = ", packagesTaggedNumber
    print "   %s created" % outFilePath



if __name__ == '__main__':
    if len(sys.argv) != 4:
        help(sys.argv[0])
        sys.exit(1)
    apiUrl = sys.argv[1]
    projectName = sys.argv[2]
    outFilePath = sys.argv[3]
    try:
        main(apiUrl, projectName, outFilePath)
    except KeyboardInterrupt:
        print >> sys.stderr, "Interrupted by user..."
