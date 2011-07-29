#!/usr/bin/python
# Authors Ronan Le Martret (Intel OTC)
# ronan@fridu.net
# Date 25 July 2011
# License GLPv2


__LICENSE__="GLPv2"
__VERSION__="1.0"
__SILENCEMODE__=0
__DEBUGMODE__=0
__VERBOSEMODE__=0

import sys
import os
import signal
import socket
import StringIO

try:
    import gzip
except:
    print >>sys.stderr, "you must install python gzip"
    sys.exit(0)

try:
    import urllib
except:
    print >>sys.stderr, "you must install python urllib"
    sys.exit(0)

try:
    from xml.etree import ElementTree
except:
    print >>sys.stderr, "you must install python xml"
    sys.exit(0)

try:
    import httplib
except:
    print >>sys.stderr, "you must install python httplib"
    sys.exit(0)

try:
    from urlparse import urlparse
except:
    print >>sys.stderr, "you must install python urlparse"
    sys.exit(0)

def signal_handler(signal, frame):
    if (signal==2):
        print >>sys.stderr,"user escape..."
    else:
        print  >>sys.stderr,"kill process..."

    sys.exit(0)
        
        
        
        
signal.signal(signal.SIGINT, signal_handler)


def obsextractgroups(URL_to_published_repo,target_dir_includes_files=None):
    #init target_dir_includes_files
    if target_dir_includes_files==None:
        target_dir_includes_files=os.curdir
    else:
        if not os.path.isdir(target_dir_includes_files):
            if __VERBOSEMODE__:
                printProcess("target_dir_includes_files will be create") 
            try:
                os.makedirs(target_dir_includes_files)
            except:
                print  >>sys.stderr,"You have not the Write access to the folder."
                print  >>sys.stderr,target_dir_includes_files
                sys.exit(0)

    #Test if URL_to_published_repo exist and is local or not
    localwork=0
    if os.path.isdir(URL_to_published_repo):
        if __VERBOSEMODE__:
            printProcess("URL_to_published_repo is local") 
        localwork=1
    elif checkHost(URL_to_published_repo):
        if checkURL(URL_to_published_repo):
            if __VERBOSEMODE__:
                printProcess("URL_to_published_repo is not local")
            localwork=0
        else:
            print >>sys.stderr, "URL-to-published-repo is not a valid URL"
            print >>sys.stderr,URL_to_published_repo
            sys.exit(1)
    else:
        print >>sys.stderr, "URL-to-published-repo have not a valid Host"
        print >>sys.stderr,URL_to_published_repo
        sys.exit(1)
        
    #find the xml file(s)
    xmlResult=None 
    if localwork==1:
        result=[]
        for root, dirs, files in os.walk(URL_to_published_repo):
            for f in files:

                if "group.xml" in f:
                    result.append((f,root+os.sep+f))
                    
        if len(result)==0:
            print >>sys.stderr, "no group in URL-to-published-repo"
            sys.exit(2)
        else:
            pathfile=result[0][1]
            if len(result)>1:
                printProcess("Warning more than 1 result find.")
                for f in result:
                    printProcess("\t"+f[0])
                    
            if __VERBOSEMODE__:
                printProcess(pathfile+" is use for the process.")
                
        if pathfile.endswith(".gz"):
            f=open(pathfile,'r')
            tmp=StringIO.StringIO()
            tmp.write(f.read())
            f.close()
            tmp.seek(0,0)
            xmlResult=gzip.GzipFile(fileobj=tmp).read()
            
        else:
            filehandle=open(pathfile,'r')
            xmlResult=filehandle.read()
            filehandle.close()
    else:
        (scheme, netloc, path, params, query, fragment) = urlparse(URL_to_published_repo)
        if ":" in netloc:
            (host,port)=netloc.split(":")
        else:
            host=netloc
            port="80"
        
        result=[]
        for root, dirs, files in walkURL(host,port,path):
            #print root
            for f in files:
                #print "\t",f
                if "group.xml" in f:
                    result.append((f,root+f))
                    
        if len(result)==0:
            print >>sys.stderr, "no group in URL-to-published-repo"
            sys.exit(2)
        else:
            pathfile=result[0][1]
            if len(result)>1:
                printProcess("Warning more than 1 result find.")
                for f in result:
                    printProcess("\t"+f[0])
                    
            if __VERBOSEMODE__:
                printProcess(pathfile+" is use for the process.")
        
        
        if ".gz" in pathfile:
            filehandle=urllib.urlopen("http://"+pathfile)
            gzResult= filehandle.read()
            filehandle.close()
            tmp=StringIO.StringIO()
            tmp.write(gzResult)
            tmp.seek(0,0)
            xmlResult=gzip.GzipFile(fileobj=tmp).read()

        else:
            filehandle=urllib.urlopen("http://"+pathfile)
            xmlResult= filehandle.read()
            filehandle.close()
            
            
            
    if xmlResult==None:
        print >>sys.stderr, "ERROR read file process"
        sys.exit(0)
    
    if __DEBUGMODE__==1:
        debugPath=target_dir_includes_files+os.sep+"group.xml"
        
        if debugPath!=pathfile:
            f=open(debugPath,'w')
            f.write(xmlResult)
            f.close()

    aElement=ElementTree.fromstring(xmlResult)
    dicoStat={}
    
    for group in aElement:
        if group.tag=="group":

            groupName=None
            listPk=[]
            
            for g in group.getchildren():
                if (g.tag=="name"):
                    groupName= g.text
                elif (g.tag=="packagelist"):
                    for p in g.getchildren():
                        listPk.append( p.text)
                else:
                    pass
                
            if groupName!=None:
                dicoStat[groupName]=str(len(listPk))
                
                f=open(target_dir_includes_files+os.sep+groupName.replace(" ","_")+".grp-ks",'w')
                for p in listPk:
                    f.write(p+"\r\n")
                f.close()
                               
    printProcess("Number of Groups:\t"+str(len(dicoStat.keys())))
    printProcess("")
    printProcess("Group name\tNumbers of packages")
    for k in dicoStat.keys():
        printProcess(k+"\t"+dicoStat[k])             

        


def walkURL(host, port,path):
    conn=httplib.HTTPConnection(host,port=port) 
    conn.connect()   
    conn.request('GET',path)  
    response=conn.getresponse().read()
    
    root=host+":"+port+path
    dirs=[]
    files=[]

    result=[]
    DirectoryListing=0
    for line in response.split("\n"):
        if "[DIR]" in line :
            parse= line.split("<a href=\"")
            d= parse[-1].split("\">")[0]
            if not d in path:
                dirs.append(d)
                
                result.extend(walkURL(host,port, path+d))    
        elif "[   ]" in line :
            parse= line.split("<a href=\"")
            f= parse[-1].split("\">")[0]
            files.append(f) 
        elif "\"Directory Listing\"" in line:
            DirectoryListing=1
        elif DirectoryListing==1:
            #print "<tr><td class=\"n\"><a href=\"" in line
            if ("<td class=\"t\">Directory</td>" in line) &(not "Parent Directory" in line):
                parse= line.split("<a href=\"")
                d= parse[-1].split("\">")[0]
                if not d in path:
                    dirs.append(d)
                    
                    result.extend(walkURL(host, port,path+d))
            elif "<tr><td class=\"n\"><a href=\"" in line :
                parse= line.split("<a href=\"")
                f= parse[-1].split("\">")[0]
                #print f
                files.append(f) 
            
            
            
            
            
    result.append((root,dirs,files))

    return result


def help():
    print """HELP obsextractgroups
Function :      Parse the group.xml file (even it's a .gz file), in a Meego's repos,
                and save the lists of rpm for each group into files,
                with the name of the group for name.
                
Usage:          obsextractgroups [option] URL-to-published-repo [target-dir-includes-files]
    [option]:
        -s silent mode
        -d debug mode, copy the group.xml in the target-dir-includes-files.
        -v verbose mode.
        URL-to-published-repo: must be a valid repository
        target-dir-includes-files: is optional, by default the value is the current directory
  
Example1: Remote
      ./obsextractgroups.py -v -d http://repo.meego.com/MeeGo/releases/1.2.0/repos/oss/ia32/ ./result/

Example2: Remote (note: here the port is 82)
      ./obsextractgroups.py http://128.124.118.140:82/home%3a/ronan%3a/MeeGo%3a/1.2/  

Example3: Local 
      ./obsextractgroups.py -s ./repos/

  version:"""+__VERSION__+"""   License:+"""+ __LICENSE__   
  
    sys.exit(0)

def printProcess(value):
    if __SILENCEMODE__==0:
        print value


def checkURL(url):
    try:
        filehandle=urllib.urlopen(url)
    except:
        return 0
     
    if filehandle.code==200:
        return 1
    else:
        return 0
    
def checkHost(url):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    if ":" in netloc:
        (host,port)=netloc.split(":")
    else:
        host=netloc
        port="80"
         
    if __VERBOSEMODE__:
        printProcess("HOST:"+host) 
    try:
        IP=socket.gethostbyname(host)
    
        if __VERBOSEMODE__:
            printProcess("HOST IP:"+IP+" port:"+port)
        
        return 1
    except socket.error, e:
        return 0





if __name__ == '__main__':
    if (len(sys.argv)>6) | (len(sys.argv)==1):
        help()
    elif ("help" in sys.argv[1]) |("-h" in sys.argv[1]):
        help()
    else:
        URL_to_published_repo=None
        target_dir_includes_files=None
        for i in range(1,len(sys.argv)):
            value=sys.argv[i]
            if (len(value)==1)&(value!="."):
                help()   
            elif value=="-v":
                __VERBOSEMODE__=1   
            elif value=="-s":
                __SILENCEMODE__=1
            elif value=="-d":
                __DEBUGMODE__=1
            elif URL_to_published_repo==None:
                URL_to_published_repo=value
            elif target_dir_includes_files==None:
                target_dir_includes_files=value
            else:
                help()
        if URL_to_published_repo==None:
            help()
            
        obsextractgroups(URL_to_published_repo,target_dir_includes_files)
            
        
        