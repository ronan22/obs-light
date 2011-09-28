#!/usr/bin/env python

import sys
from os.path import join
from xml.etree import ElementTree

from osc import conf, core

def help():
    print "HELP\
Function : Tag a project in an OBS (remote obs are managed via a linked project)\
        It will create a tag file which constains the MD5 to represent the package revision.\
        The Tag file can be used as direct input for obs2obsCopy."

class PackageRevision(object):

    def __init__(self, packageName, rev, vrev):
        self.name = packageName
        self.rev = rev
        self.vrev = vrev

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = "%(srcmd5)40s | %(rev)6s | %(time)20s | %(name)s | %(version)s | %(user)s" % self.__dict__
        if "comment" in self.__dict__:
            s += " | " + self.comment
        return s


def compareRevs(rev1, rev2):
    return cmp(rev1.rev, rev2.rev)
    
def getPackageList(apiUrl, project):
    return core.meta_get_packagelist(apiUrl, project)

def getPackageRevisions(apiUrl, project, packageName):
    revisionsList = list()
    url = apiUrl + "/source/" + project + "/" + packageName + "/_history"
    xmlResult = core.http_request("GET", url).read()
    xmlRevisionLists = ElementTree.fromstring(xmlResult)
    for xmlRevisionList in xmlRevisionLists.iter("revisionlist"):
        for xmlRevision in xmlRevisionList.iter("revision"):
            revision = PackageRevision(packageName, xmlRevision.get("rev", 1), xmlRevision.get("vrev", 1))
            for field in xmlRevision.iter():
                revision.__dict__[field.tag] = field.text
            revisionsList.append(revision)
    revisionsList.sort(compareRevs, reverse=True)
    return revisionsList

if __name__ == '__main__':
    if len(sys.argv) != 4:
        help()
        sys.exit(1)
    
    apiUrl = sys.argv[1]
    project = sys.argv[2]
    outFile = sys.argv[3]
    aConf = conf.get_config()
    packageList = getPackageList(apiUrl, project)
    for packageName in packageList:
#        print "Looking for ", packageName, "revisions..."
        revisions = getPackageRevisions(apiUrl, project, packageName)
        print revisions[0]
