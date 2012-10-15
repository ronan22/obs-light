# coding=utf-8
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
"""
Utilities to dialog with an OBS server.

@author: Florent Vennetier
"""

import os
import re
import subprocess
from tempfile import NamedTemporaryFile

import Utils
from Config import getConfig

OSCRC_TEMPLATE = """[general]
# URL to access API server, e.g. https://build.api.meego.com
apiurl = __PROTOCOL__://__HOST__:__PORT__
verbose=0
use_keyring=0
su-wrapper=sudo

[__PROTOCOL__://__HOST__:__PORT__]
# Default user and password on OBS Light OBS appliances
user=Admin
pass=opensuse
# Without that, osc will ask user if he wants to import the certificate,
# but due to buffering, the question is sometimes not displayed.
sslcertck=0
"""

FAKEOBS_META = """<project name="__FAKEOBS_LINK_NAME__">
  <title>Fake OBS running on localhost</title>
  <description/>
  <remoteurl>http://localhost:__PORT__/public</remoteurl>
  <person role="maintainer" userid="Admin"/>
  <person role="bugowner" userid="Admin"/>
</project>
"""

FAKEOBS_LINK_NAME = "fakeobs"

def readObsApiConfig(path):
    """
    Search for FRONTEND_PROTOCOL, FRONTEND_HOST and FRONTEND_PORT
    in `path` and return their values as a tuple.
    """
    with open(path, "r") as myFile:
        config = myFile.read()
    host = re.search(r"^FRONTEND_HOST\s*=\s*['\"]{1}([a-zA-Z0-9\-]*)['\"]{1}",
                     config, re.M).group(1)
    port = re.search(r"^FRONTEND_PORT\s*=\s*([0-9]*)",
                     config, re.M).group(1)
    protocol = re.search(r"^FRONTEND_PROTOCOL\s*=\s*['\"]{1}([a-zA-Z]*)['\"]{1}",
                         config, re.M).group(1)
    return protocol, host, port

def makeOscConfigFile(protocol, host, port, templatePath=None):
    """
    Create a temporary osc configuration file, suitable to
    contact an OBS Light server as Admin.
    """
    if templatePath is not None:
        with open(templatePath, "r") as templateFile:
            template = templateFile.read()
    else:
        template = OSCRC_TEMPLATE
    template = template.replace("__PROTOCOL__", protocol)
    template = template.replace("__HOST__", host)
    template = template.replace("__PORT__", port)
    with NamedTemporaryFile(prefix="localhost.oscrc",
                            delete=False) as tmpFile:
        tmpFile.write(template)
        return tmpFile.name

def createFakeObsLink(oscConfigPath=None):
    """
    Create the link to the fakeobs API on the OBS running on localhost.
    `oscConfigPath` may be the path to the osc configuration of
    an administrator of the OBS server.
    """
    conf = getConfig()
    tempFileUsed = False
    try:
        if oscConfigPath is None:
            webUiConfigPath = conf.getPath(
                "obs_webui_configuration_file",
                "/srv/www/obs/webui/config/environments/production.rb")
            protocol, host, port = readObsApiConfig(webUiConfigPath)
            tempFileUsed = True
            oscConfigPath = makeOscConfigFile(protocol, host, port)

        res = Utils.callSubprocess(["osc", "-c", oscConfigPath, "ls"],
                                   stdout=subprocess.PIPE)
        if res != 0:
            msg = "Could not contact OBS API"
            raise IOError(msg)

        res = Utils.callSubprocess(["osc", "-c", oscConfigPath,
                                    "meta", "prj", FAKEOBS_LINK_NAME],
                                   stdout=subprocess.PIPE)
        if res == 0:
            return "'%s' remote link already exists!" % FAKEOBS_LINK_NAME

        apiPort = conf.getPort("api_port", 8001)
        meta = FAKEOBS_META.replace("__PORT__", str(apiPort))
        meta = meta.replace("__FAKEOBS_LINK_NAME__", FAKEOBS_LINK_NAME)
        myProc = subprocess.Popen(["osc", "-c", oscConfigPath,
                                   "meta", "prj", "-F", "-", FAKEOBS_LINK_NAME],
                                  stdin=subprocess.PIPE)
        myProc.communicate(meta)
        res = myProc.wait()
        if res != 0:
            msg = "Failed to create '%s' project link!" % FAKEOBS_LINK_NAME
            raise IOError(msg)

    finally:
        if tempFileUsed:
            os.remove(oscConfigPath)
