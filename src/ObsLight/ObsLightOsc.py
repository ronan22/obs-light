#
# Copyright 2011, Intel Inc.
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 3 oct. 2011

@author: ronan
'''



import os


from osc import conf
from osc import core
#from osc import build

from xml.etree import ElementTree

from ObsLightSubprocess import SubprocessCrt

class ObsLightOsc(object):
    '''
    ObsLightOsc interact with osc, when possible, do it directly by python API
    '''
    def __init__(self):
        '''
        init 
        '''
        self.__confFile = os.path.join(os.environ['HOME'], ".oscrc")
        self.__mySubprocessCrt = SubprocessCrt()
        
        if os.path.isfile(self.__confFile): 
            conf.get_config()
        
    def initConf(self,
                 api=None,
                 user=None,
                 passw=None,
                 aliases=None):
        '''
        init a configuation for a API.
        '''
        if not os.path.isfile(self.__confFile): 
            conf.write_initial_config(self.__confFile, {'apiurl':api, 'user' : user, 'pass' : passw })
        
        aOscConfigParser = conf.get_configParser(self.__confFile)

        if not (api in  aOscConfigParser.sections()):
            aOscConfigParser.add_section(api)

        aOscConfigParser.set(api, 'user', user)
        aOscConfigParser.set(api, 'pass', passw)
        aOscConfigParser.set(api, 'aliases', aliases)

        aOscConfigParser.set('general', 'su-wrapper', "sudo")
        
        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)
        if aFile: 
            aFile.close()

        
      
        
        
    def trustRepos(self,
                   api=None,
                   listDepProject=None):
        '''
        
        '''
        aOscConfigParser = conf.get_configParser(self.__confFile)
        
        if aOscConfigParser.has_option(api, "trusted_prj"):
            options = aOscConfigParser.get(api, "trusted_prj")
        else:
            options = ""
            
        res = options
        for depProject in listDepProject:
            if not depProject in res:
                res += " " + depProject
        
        aOscConfigParser.set(api, 'trusted_prj', res)
            
        aFile = open(self.__confFile, 'w')
        aOscConfigParser.write(aFile, True)
        if aFile: aFile.close()
        return 

    def getDepProject(self,
                      apiurl=None,
                      projet=None,
                      repos=None):
        '''
        
        '''
        url = apiurl + "/source/" + projet + "/_meta"
        aElement = ElementTree.fromstring(core.http_request("GET", url).read())
    
        result = []
        for project in aElement:
            if (project.tag == "repository") and (project.get("name") == repos):
                for path in project.getiterator():
                    if path.tag == "path":
                        result.append(path.get("project"))
        return result

    def getListPackage(self,
                       obsServer=None,
                       projectLocalName=None):
        '''
            return the list of a projectLocalName
        '''
        list_package = core.meta_get_packagelist(obsServer, projectLocalName)
        return list_package
    
    def CheckoutPackage(self,
                        obsServer=None,
                        projectLocalName=None,
                        package=None,
                        directory=None):
        '''
            check out a package
        '''
        os.chdir(directory)
        command = "osc -A " + obsServer + " co " + projectLocalName + " " + package
        self.__subprocess(command=command)

        
    def __subprocess(self, command=None, waitMess=False):
        '''
        
        '''
        return self.__mySubprocessCrt.execSubprocess(command=command, waitMess=waitMess)
        
        
    def getPackageStatus(self,
                         obsServer=None,
                         project=None,
                         package=None,
                         repos=None,
                         arch=None):
        '''
        Return the status of a package for a repos and arch
        The status can be:
        succeeded: Package has built successfully and can be used to build further packages.
        failed: The package does not build successfully. No packages have been created. Packages that depend on this package will be built using any previously created packages, if they exist.
        unresolvable: The build can not begin, because required packages are either missing or not explicitly defined.
        broken: The sources either contain no build description (eg specfile) or a source link does not work.
        blocked: This package waits for other packages to be built. These can be in the same or other projects.
        dispatching: A package is being copied to a build host. This is an intermediate state before building.
        scheduled: A package has been marked for building, but the build has not started yet.
        building: The package is currently being built.
        signing: The package has been built and is assigned to get signed.
        finished: The package has been built and signed, but has not yet been picked up by the scheduler. This is an intermediate state prior to 'succeeded' or 'failed'.
        disabled: The package has been disabled from building in project or package metadata.
        excluded: The package build has been disabled in package build description (for example in the .spec file) or does not provide a matching build description for the target.
        unknown: The scheduler has not yet evaluated this package. Should be a short intermediate state for new packages.
        '''
        url = obsServer + "/build/" + project + "/" + repos + "/" + arch + "/" + package + "/_status"
        fileXML = core.http_request("GET", url).read()
        aElement = ElementTree.fromstring(fileXML)
        return aElement.attrib["code"]
        
    def createChRoot(self,
                     #obsApi=None,doesn't work
                     chrootDir=None,
                     projectDir=None ,
                     repos=None,
                     arch=None,
                     specPath=None):
        '''
        create a chroot
        TODO: create chroot without build a package
        TODO: Build without a subprocess
        '''
        os.chdir(projectDir)

        #doesn't work
        #apiurl=obsApi
        #apts=optparse.OptionContainer()
        #opts ={}
        #opts['rsyncsrc']= None
        #opts['linksources']= None
        #opts['build_uid']= None
        #opts['oldpackages']= None
        #opts['userootforbuild']= None
        #opts['vm_type']= None
        #opts['overlay']= None
        #opts['disable_debuginfo']= None
        #opts['prefer_pkgs']= None
        #opts['no_changelog']= None
        #opts['icecream']= None
        #opts['disable_cpio_bulk_download']= None
        #opts['ccache']= None
        #opts['offline']= None
        #opts['define']= None
        #opts['preload']= None
        #opts['extra_pkgs']= ['vim', 'git', 'strace', 'iputils', 'yum', 'yum-utils', 'ncurses-devel', 'zypper']
        #opts['shell']= None
        #opts['jobs']= None
        #opts['clean']= None
        #opts['baselibs']= None
        #opts['debuginfo']= None
        #opts['noservice']= True
        #opts['nochecks']= None
        #opts['noinit']= None
        #opts['local_package']= None
        #opts['download_api_only']= None
        #opts['rsyncdest']= None
        #opts['alternative_project']= None
        #opts['keep_pkgs']= None
        #opts['without']= None
        #opts['no_verify']= True
        #opts['release']= None
        #opts['root']= chrootDir
        #opts['_with']= None
        #argv=(repos, arch, specPath)
            
        #build.main(apiurl=apiurl, opts=opts, argv=argv)
        
        command = "osc build --root=" + chrootDir + " -x vim -x git -x strace -x iputils -x yum -x yum-utils -x ncurses-devel -x zypper --noservice --no-verify " + repos + " " + arch + " " + specPath
        self.__subprocess(command=command, waitMess=True)

        
    def getListLocalProject(self, obsServer=None):
        '''
        return a list of the project of a OBS Server.
        '''
        return core.meta_get_project_list(obsServer)
    
    def getListRepos(self, apiurl):
        '''
        return the list of the repos of a OBS Server.
        '''
        url = apiurl + "/distributions"
        aElement = ElementTree.fromstring(core.http_request("GET", url).read())
     
        result = []
        for repos in aElement:
   
            name = ""
            project = ""
            reponame = ""
            repository = ""
            for distri in repos:
                if distri.tag == "name":
                    name = distri.text
                elif distri.tag == "project":
                    project = distri.text
                elif distri.tag == "reponame":
                    reponame = distri.text
                elif distri.tag == "repository":
                    repository = distri.text
            result.append([name, project, reponame, repository])
        return result
     
    def getListTarget(self,
                      obsServer=None,
                      projectObsName=None):
        '''
        return the list of Target of a projectObsProject for a OBS server.
        '''
        url = obsServer + "/build/" + projectObsName
        aElement = ElementTree.fromstring(core.http_request("GET", url).read())
        res = []
        for directory in aElement:
            for entry in directory.getiterator():
                res.append(entry.get("name"))
        return res
        
    def getListArchitecture(self,
                            obsServer=None,
                            projectObsName=None,
                            projectTarget=None):
        '''
        return the list of Archictecture of the target of the projectObsName for a OBS server.
        '''
        url = obsServer + "/build/" + projectObsName + "/" + projectTarget
        
        aElement = ElementTree.fromstring(core.http_request("GET", url).read())
        res = []
        for directory in aElement:
            for entry in directory.getiterator():
                res.append(entry.get("name"))
        return res
    
    def commitProject(self,
                      path=None,
                      message=None,
                      skip_validation=True):
        '''
        commit a project to the OBS server.
        '''
        os.chdir(path)
        command = "osc ci -m \"" + message + "\" "
        
        if skip_validation:
            command += "--skip-validation"
        self.__subprocess(command=command)

    def addremove (self, path=None):
        '''
        Adds new files, removes disappeared files
        '''
        os.chdir(path)
        command = "osc ar"
        self.__subprocess(command=command)
        
myObsLightOsc = ObsLightOsc()

