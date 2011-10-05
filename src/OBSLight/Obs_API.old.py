#!/usr/bin/python
# Authors Ronan Le Martret (Intel OTC)
# ronan@fridu.net
# Date 8 Aug 2011
# License GLPv2

# This Python script 
#    list of the packages of a project, 
#    get the status, and so, if the status is "failed", rebuild the package.</code>



from osc import conf
from osc import core
from xml.etree import ElementTree


def rebuildBlock(apiurl,prj,repos,arch):
    apiurl="http://128.224.218.253:81"
    prj="test"
    repos="Remote_MeeGo_1.2.0"
    arch="armv8el"

    conf.get_config()
    
    list_repos=core.get_repositories_of_project(apiurl, prj)
    list_package=core.meta_get_packagelist(apiurl, prj)

    for package in list_package:
        url=apiurl+"/build/"+prj+"/"+repos+"/"+arch+"/"+package+"/_status"
        try:
            fileXML=core.http_request("GET", url).read()
            aElement=ElementTree.fromstring(fileXML)
        except:
            print "--------------------------------------------------"
            print    fileXML
            print "--------------------------------------------------"
        code=aElement.attrib["code"]
    
        if (code=="failed")or(code=="unresolvable") :
            print "package",package,
            print "\t\t\t\tcode",code,
            print "\t\trebuild"
            core.rebuild(apiurl, prj, package, repos, arch)


def getListHost():
    conf.get_config()
    return  conf.config["api_host_options"].keys()

def getListRepos(apiurl):
    conf.get_config()
    url=apiurl+"/distributions"
    aElement=ElementTree.fromstring(core.http_request("GET", url).read())
    
    result=[]
    for repos in aElement:
        print "repos.attrib.keys()",repos.attrib.keys()
        
        name=""
        project=""
        reponame=""
        repository=""
        for distri in repos:
            print distri.tag,distri.text
            if distri.tag=="name":
                name=distri.text
            elif distri.tag=="project":
                project=distri.text
            elif distri.tag=="reponame":
                reponame=distri.text
            elif distri.tag=="repository":
                repository=distri.text
        result.append([name,project,reponame,repository])
    return result



    
    
if __name__ == '__main__':
    rebuildBlock(0,0,0,0)
    
    
        
        
    
    
    
    
    
    
    