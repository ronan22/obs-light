#!/usr/bin/python
#
# Copyright 2012, Intel Inc.
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
import sys
import traceback
import urllib2
import urlparse
from xml.etree import ElementTree
import SocketServer
import BaseHTTPServer

GET = "GET"

def queryToDict(query):
    queryDict = dict()
    queryParts = query.split('&')
    for queryPart in queryParts:
        subParts = queryPart.split('=')
        if len(subParts) == 1 and len(subParts[0]) > 0:
            queryDict[subParts[0]] = list()
        elif len(subParts) >= 2:
            values = queryDict.get(subParts[0], list())
            values.append(subParts[1])
            queryDict[subParts[0]] = values
    return queryDict

def getEntryNameList(xmlContent):
    nameList = []
    directoryList = ElementTree.fromstring(xmlContent)
    for directory in directoryList:
        for element in directory.iter("entry"):
            name = element.get("name")
            nameList.append(name)
    return nameList

class FakeObsWebUiRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    fakeobsUrl = "http://localhost:8001/public"
    preamble = (
"""<html>
  <head>
    <title>OBS Light's Fake OBS Web Interface</title>
  </head>
  <body>
""")
    footer = "</body>\n</html>\n"

    def do_GET(self):
        try:
            content = self.send_preamble(GET)
            content += self.send_content(GET)
            content += self.send_footer(GET)
#            contentsize = len(content)
#            contenttype = "text/html"
#            self.send_header("Content-type", contenttype)
#            self.send_header("Content-Length", contentsize)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_response(500)
            print "500: " + self.path
            traceback.print_exc(file=sys.stdout)
            self.end_headers()

    def send_preamble(self, action):
        return self.preamble

    def send_footer(self, action):
        return self.footer

    def send_content(self, action):
        pathToMethod = {"project": self.handleProjectRequest,
                        "packages": self.handlePackagesRequest}

        parsedPath = urlparse.urlparse(self.path)
        pathParts = parsedPath[2].split('/')
        queryDict = queryToDict(parsedPath[4])
        return pathToMethod.get(pathParts[1], self.getDefaultPage)(pathParts[2:], queryDict)


    def getDefaultPage(self, *args, **kwargs):
        return '<a href="/project/list_public">Project list<a>\n'

    def handleProjectRequest(self, pathParts, queryDict):
        if pathParts[0] == "list_public":
            return self.getPrettyProjectList()
        # TODO: factorize the following
        elif pathParts[0] == "packages":
            if queryDict.has_key("project"):
                return self.getPrettyPackageList(queryDict["project"][0])
        elif pathParts[0] == "prjconf":
            if queryDict.has_key("project"):
                return self.getProjectConfigOrMeta(queryDict["project"][0], "config")
        elif pathParts[0] == "meta":
            if queryDict.has_key("project"):
                return self.getProjectConfigOrMeta(queryDict["project"][0], "meta")

        return self.getDefaultPage()

    def handlePackagesRequest(self, pathParts, queryDict):
        return self.getDefaultPage()

    def getPrettyProjectList(self):
        """call /source, parse the result, format to HTML code"""
        url = "%s/source" % (self.fakeobsUrl)
        xmlRes = urllib2.urlopen(url).read()
        projectList = getEntryNameList(xmlRes)
        formattedList = "<ul>\n"
        for project in projectList:
            packageListUrl = "/project/packages?project=%s" % project
            prjconfUrl = "/project/prjconf?project=%s" % project
            metaUrl = "/project/meta?project=%s" % project
            formattedList += '  <li>\n  <a href="%s">%s</a>\n' % (packageListUrl, project)
            formattedList += '  (<a href="%s">config</a>, <a href="%s">meta</a>)\n' % (prjconfUrl,
                                                                                       metaUrl)
            formattedList += '</li>\n'
        formattedList += "</ul>\n"
        return "<h3>Projects</h3>\n<p>\n%s</p>\n" % formattedList

    def getPrettyPackageList(self, project):
        """call /source/<project>, parse the result, format to HTML code"""
        url = "%s/source/%s" % (self.fakeobsUrl, project)
        xmlRes = urllib2.urlopen(url).read()
        packageList = getEntryNameList(xmlRes)
        formattedList = "<ul>\n"
        for package in packageList:
            packageFilesUrl = "/package/files?package=%s&project=%s" % (package, project)
            formattedList += '  <li><a href="%s">%s</a></li>\n' % (packageFilesUrl, package)
        formattedList += "</ul>\n"
        return "<h3>Packages of %s</h3>\n<p>\n%s</p>\n" % (project, formattedList)

    def getProjectConfigOrMeta(self, project, what="config"):
        readableWhat = {"config": "project configuration",
                        "meta": "project meta informations"}
        url = "%s/source/%s/_%s" % (self.fakeobsUrl, project, what)
        rawContent = urllib2.urlopen(url).read()
        rawContent = rawContent.replace("<", "&lt").replace(">", "&gt")
        content = "<h3>%s %s</h3>\n<pre>\n" % (project, readableWhat[what])
        content += rawContent
        content += "</pre>\n"
        return content

class XFSPWebServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    else:
        PORT = 8000
        print "No port specified, using %d" % PORT

    httpd = XFSPWebServer(("0.0.0.0", PORT), FakeObsWebUiRequestHandler)
    httpd.serve_forever()
