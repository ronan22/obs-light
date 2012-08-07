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

FIRST_PAGE = """
<a href="/project/list_public">Project list<a>\n
"""
GLOBAL_HEADER = """
<html>
 <head>
  <title>OBS Light's Fake OBS Web Interface</title>
 </head>
 <body>
"""
GLOBAL_FOOTER = """
 </body>
</html>
"""
PACKAGE_FILES_HEADER = """
<h3>Files of %(package)s</h3>
<table border="1">
 <tr>
  <th>File</th>
  <th>Size</th>
  <th>MD5</th>
  <th>Modification time</th>
 </tr>
"""
PACKAGE_FILES_FOOTER = """
</table>
"""
PACKAGE_FILE_TEMPLATE = """
 <tr>
  <td align="left">%(name)s</td>
  <td align="right">%(size)s</td>
  <td align="right">%(md5)s</td>
  <td align="right">%(mtime)s</td>
 </tr>
"""
PROJECT_LIST_HEADER = """
<h3>Projects</h3>
<p>
 <ul>
"""
PROJECT_LIST_FOOTER = """
 </ul>
</p>
"""
PROJECT_ENTRY_TEMPLATE = """
  <li>
   <a href="%(packageListUrl)s">%(project)s</a> (<a href="%(prjconfUrl)s">config</a>, <a href="%(metaUrl)s">meta</a>)
  </li>
"""
PACKAGE_LIST_HEADER = """
<h3>Packages of %(project)s</h3>
<p>
 <ul>
"""
PACKAGE_LIST_FOOTER = """
 </ul>
</p>
"""
PACKAGE_ENTRY_TEMPLATE = """
  <li><a href="%(packageFilesUrl)s">%(package)s</a></li>
"""
TEXT_FILE_TEMPLATE = """
<h3>%(title)s</h3>
<pre>%(content)s</pre>
"""

def queryToDict(query):
    """
    Makes a dict from an HTTP query.
    With query:
      project=toto&package=foo&package=bar
    it will return:
      {"project": ["toto"], "package": ["foo", "bar"]}
    """
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
    """Makes a list of all "name" attributes of the XML tree"""
    nameList = []
    directoryList = ElementTree.fromstring(xmlContent)
    for directory in directoryList:
        for element in directory.iter("entry"):
            name = element.get("name")
            nameList.append(name)
    return nameList

def getEntriesAsDicts(xmlContent):
    """
    Make a dict from a string like the one returned by a request to
      /source/<project>/<package>
    """
    dictList = []
    directoryList = ElementTree.fromstring(xmlContent)
    for directory in directoryList:
        for element in directory.iter("entry"):
            entry = dict()
            for attribute in element.items():
                entry[attribute[0]] = attribute[1]
            dictList.append(entry)
    return dictList

class FakeObsWebUiRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    fakeobsUrl = "http://localhost:8001/public"

    def do_GET(self):
        try:
            content, code = self.get_content(GET)
            self.send_response(code)
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_response(500)
            print "500: " + self.path
            traceback.print_exc(file=sys.stdout)
            self.end_headers()

    def get_content(self, action):
        pathToMethod = {"project": self.handleProjectRequest,
                        "package": self.handlePackagesRequest}

        parsedPath = urlparse.urlparse(self.path)
        if parsedPath[2] == "/":
            return self.getDefaultPage()
        # path starts with '/' so first splitted element is always empty
        pathParts = parsedPath[2].split('/')[1:]
        queryDict = queryToDict(parsedPath[4])
        try:
            content, code = pathToMethod[pathParts[0]](pathParts[1:], queryDict)
        except KeyError as ke:
            return self.unknownRequest(pathParts[0])
        return GLOBAL_HEADER + content + GLOBAL_FOOTER, code

    def getDefaultPage(self, *args, **kwargs):
        return FIRST_PAGE, 200

    def unknownRequest(self, request):
        message = "Unknown request: %s" % request
        return message, 400

    def missingParameters(self, params):
        message = "Missing parameters: %s" % ", ".join(params)
        return message, 400

    def handleProjectRequest(self, pathParts, queryDict):
        # {"request": (function_to_call, [query_parameters], [other_parameters])}
        funcMap = {"list_public": (self.getPrettyProjectList, [], []),
                   "packages": (self.getPrettyPackageList, ["project"], []),
                   "prjconf": (self.getProjectConfigOrMeta, ["project"], ["config"]),
                   "meta": (self.getProjectConfigOrMeta, ["project"], ["meta"])}
        funcTuple = funcMap.get(pathParts[0])
        if funcTuple is None:
            return self.unknownRequest("/project/%s" % pathParts[0])
        else:
            # funcTuple[0] -> function
            # funcTuple[1] -> list of arguments to take in queryDict
            # funcTuple[2] -> list of extra arguments
            try:
                myArgs = [queryDict[x][0] for x in funcTuple[1]]
            except KeyError as ke:
                return self.missingParameters([ke.args[0]])
            myArgs.extend(funcTuple[2])
            content, code = funcTuple[0](*myArgs)
            return content, code

    def handlePackagesRequest(self, pathParts, queryDict):
        if pathParts[0] == "files":
            try:
                return self.getPrettyFilesList(queryDict["project"][0],
                                               queryDict["package"][0])
            except KeyError as ke:
                return self.missingParameters([ke.args[0]])
        else:
            return self.unknownRequest("/package/" + pathParts[0])
        return self.getDefaultPage()

    def getPrettyProjectList(self):
        """call /source, parse the result, format to HTML code"""
        url = "%s/source" % (self.fakeobsUrl)
        xmlRes = urllib2.urlopen(url).read()
        projectList = getEntryNameList(xmlRes)
        formattedList = PROJECT_LIST_HEADER
        for project in projectList:
            projectDict = {"project": project,
                           "packageListUrl": "/project/packages?project=%s" % project,
                           "prjconfUrl": "/project/prjconf?project=%s" % project,
                           "metaUrl": "/project/meta?project=%s" % project}
            formattedList += PROJECT_ENTRY_TEMPLATE % projectDict
        formattedList += PROJECT_LIST_FOOTER
        return formattedList, 200

    def getPrettyPackageList(self, project):
        """call /source/<project>, parse the result, format to HTML code"""
        url = "%s/source/%s" % (self.fakeobsUrl, project)
        xmlRes = urllib2.urlopen(url).read()
        packageList = getEntryNameList(xmlRes)
        formattedList = PACKAGE_LIST_HEADER % {"project": project}
        for package in packageList:
            packageFilesUrl = "/package/files?package=%s&project=%s" % (package, project)
            formattedList += PACKAGE_ENTRY_TEMPLATE % {"packageFilesUrl": packageFilesUrl,
                                                       "package": package}
        formattedList += PACKAGE_LIST_FOOTER
        return formattedList, 200

    def getProjectConfigOrMeta(self, project, what="config"):
        readableWhat = {"config": "project configuration",
                        "meta": "project meta informations"}
        url = "%s/source/%s/_%s" % (self.fakeobsUrl, project, what)
        fileContent = urllib2.urlopen(url).read()
        fileContent = fileContent.replace("<", "&lt").replace(">", "&gt")
        title = "%s %s" % (project, readableWhat[what])
        content = TEXT_FILE_TEMPLATE % {"title": title,
                                        "content": fileContent}
        return content, 200

    def getPrettyFilesList(self, project, package):
        """call /source/<project>/<package>, parse the result, format to HTML code"""
        url = "%s/source/%s/%s" % (self.fakeobsUrl, project, package)
        xmlRes = urllib2.urlopen(url).read()
        packages = getEntriesAsDicts(xmlRes)
        content = PACKAGE_FILES_HEADER % {"project": project, "package": package}
        for package in packages:
            content += PACKAGE_FILE_TEMPLATE % package
        content += PACKAGE_FILES_FOOTER
        return content, 200

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
