'''
Created on 17 juin 2011

@author: rmartret
'''
import os
import sys
import pickle
import subprocess



class LocalRepository(object):
    '''
    classdocs
    '''


    def __init__(self,path=None,url=None,name=None,listRPM=None):
        '''
        TO DO
        '''
        
        self.__repositoryName=name
        self.__creationDate=None
        self.__BaseReposUrl=url
        self.__PathRepos=path
        self.__reposID=None
        self.__reposVersion=None
        self.__repositoryStatus=None
        
        if (listRPM!=None) :
            self.__listRPM=listRPM
        else:
            self.__listRPM={}
        
        self.__listGroupRPM={}
        
        self.__valideRepository=False
        
        
        self.__Urltype={}
        self.__Urltype["source"]="source"
        self.__Urltype["ia32"]="ia32/packages"
        self.__Urltype["armv7hl"]="armv7hl/packages"
        
        self.__listRPM={}
        self.__listRPM["source"]={}
        self.__listRPM["ia32"]={}
        self.__listRPM["armv7hl"]={}
        
        self.__listRPMFile="listRPMConfig"
        
        self.__listDependence={}
        self.__listDependence["ia32"]={}
        self.__listDependence["armv7hl"]={}
        self.__listDependence["source"]={}

        self.__listDependenceFile="listRPMDependenceConfig"

        self.__listProvides={}
        self.__listProvides["ia32"]={}
        self.__listProvides["armv7hl"]={}
        
        self.__listLibFile="listRPMProvidesConfig"

        self.__load()


    def __save(self):
        """
        
        """        
        file=open(self.__PathRepos+os.sep+self.__listRPMFile,'w')
        pickle.dump(self.__listRPM,file)    
        
        file=open(self.__PathRepos+os.sep+self.__listDependenceFile,'w')
        pickle.dump(self.__listDependence,file)
        
        file=open(self.__PathRepos+os.sep+self.__listLibFile,'w')
        pickle.dump(self.__listProvides,file)
        
        

        
    def __load(self):
        """
        
        """
        if os.path.isfile(self.__PathRepos+os.sep+self.__listRPMFile):
            file=open(self.__PathRepos+os.sep+self.__listRPMFile,'r')
            self.__listRPM=pickle.load(file)
            
        if os.path.isfile(self.__PathRepos+os.sep+self.__listDependenceFile):
            file=open(self.__PathRepos+os.sep+self.__listDependenceFile,'r')
            self.__listDependence=pickle.load(file)
            
        if os.path.isfile(self.__PathRepos+os.sep+self.__listLibFile):
            file=open(self.__PathRepos+os.sep+self.__listLibFile,'r')
            self.__listProvides=pickle.load(file)
        
        
    def check(self):
        """
        
        """
        self.__listRPM["source"]={}
        self.__listRPM["ia32"]={}
        self.__listRPM["armv7hl"]={}
        
        self.__listDependence["ia32"]={}
        self.__listDependence["armv7hl"]={}
        self.__listDependence["source"]={}

        self.__listProvides["ia32"]={}
        self.__listProvides["armv7hl"]={}     
           
        r1=self.__checkRPMSource("source")
        r2=self.__checkRPMSource("ia32")
        r3=self.__checkRPMSource("armv7hl")

        r4=self.__checkDependence("source")
        r5=self.__checkDependence("ia32")
        r6=self.__checkDependence("armv7hl")
        

        r7=self.__checkProvides("ia32")
        r8=self.__checkProvides("armv7hl")
        
        
        self.__save()
        return r1|r2|r3|r4|r5|r6|r7|r8 
        
    def __checkProvides(self,type=None):
        """
        
        """
        self.__listProvides[type]["lib"]={}
        self.__listProvides[type]["rpm"]={}
            
        for rpmName in self.__listRPM[type].keys():
            
            for arpm in self.__listRPM[type][rpmName]:
                version=arpm["version"]
                path=arpm["path"]

                command=("rpm -qp --provides "+path).split()
                p=subprocess.Popen(command , shell=False,stdout=subprocess.PIPE)
                p.wait()
                res=p.stdout.readlines()
                
                for dep in set(res):
                    dep=dep.replace("\n","").replace(" ","")
                    
                    islib=dep.count("=")
                    if (islib==0):
                        lib=dep
                        
                        if not (lib in self.__listProvides[type]["lib"].keys()):
                            self.__listProvides[type]["lib"][lib]=[]
                              
                        self.__listProvides[type]["lib"][lib].append([rpmName,version])
                        
                    elif (islib==1):
                        [aName,aVersion]=dep.split("=")
                        if not aName.startswith("font"):
                            if not (aName in self.__listProvides[type]["rpm"].keys()):
                                self.__listProvides[type]["rpm"][aName]={}
                                
                            if not aVersion in self.__listProvides[type]["rpm"][aName].keys():
                                self.__listProvides[type]["rpm"][aName][aVersion]=[]
                                
                            self.__listProvides[type]["rpm"][aName][aVersion].append([rpmName,version])   
                    
                    else:
                        print "ERROR in __checkDependence"
                        print dep
                
                
        return 0
        
    def __checkDependence(self,type=None):
        """
        
        """
        for rpmName in self.__listRPM[type].keys():
            
            if not rpmName in self.__listDependence[type]:
                self.__listDependence[type][rpmName]={}
                

            for arpm in self.__listRPM[type][rpmName]:
                version=arpm["version"]
                path=arpm["path"]

                self.__listDependence[type][rpmName][version]={}
                
                self.__listDependence[type][rpmName][version]["lib"]=[]
                self.__listDependence[type][rpmName][version]["rpm"]=[]
                
                
                command=("rpm -qpR "+path).split()
                p=subprocess.Popen(command , shell=False,stdout=subprocess.PIPE)
                p.wait()
                res=p.stdout.readlines()
                

                for dep in set(res):
                    dep=dep.replace("\n","").replace(" ","")
                    
                    islib=dep.count("=")
                    if (islib==0):
                        lib=dep
                        
                        self.__listDependence[type][rpmName][version]["lib"].append(lib)
                        
                    elif (islib==1):
                        [aName,aVersion]=dep.split("=")
                        self.__listDependence[type][rpmName][version]["rpm"].append([aName,aVersion])
                        
                    else:
                        print "ERROR in __checkDependence"
                        print dep
                
        return 0
        
        
    def __checkRPMSource(self,type=None):
        """
        
        """
        for root ,dir,files in os.walk(self.__PathRepos+os.sep+self.__Urltype[type]):
            #print "root",root,"dir",dir,"files",files
            for file in files:
                if file.endswith(".rpm"):
                    afile=file.split(".rpm")[0]
                    
                    arch=afile[afile.rfind(".")+1:]
                    afile=afile[:afile.rfind(".")]
                    
                    packageVersion=afile[afile.rfind("-")+1:]
                    
                    afile=afile[:afile.rfind("-")]
                    version=afile[afile.rfind("-")+1:]
                    
                    afile=afile[:afile.rfind("-")]
                    name=afile
                    
                    rpmDef={}
                    rpmDef["version"]=version
                    rpmDef["packageVersion"]=packageVersion
                    rpmDef["path"]=root+os.sep+file
                    
                    if not name in self.__listRPM[type].keys():
                        self.__listRPM[type][name]=[]
                        
                    self.__listRPM[type][name].append(rpmDef)
                          
        return 0        
    

        
    def getBaseReposUrl(self):
        """
        
        """
        return self.__BaseReposUrl
        
    def getPathRepos(self):
        """
        
        """
        return self.__PathRepos
        
    def getRepositoryName(self):
        """
        Return the name of the repository.
        """
        return self.__repositoryName
    
    def isValideRepository(self):
        """
        Return if the repository is a valide repository.
        """
        return self.__valideRepository
    
    
    def getRepositoryInfo(self):
        """
        
        """
        return ["repositoryName: "+str(self.__repositoryName),"path :"+str(self.__PathRepos),"url :"+str(self.__BaseReposUrl)]
    
    def setUrlToRepositoty(self,url=None):
        """
        
        """
        self.__BaseReposUrl=url
        return 0
    
    def setPathToRepositoty(self,path=None):
        """
        
        """
        self.__PathRepos=path
        return 0
    
    
    def getRPMPath(self, architecture=None,rpm=None):
        
        
        res= self.__listRPM[architecture][rpm]
        
        if len(res)>1:
            print "error ",rpm
            
        else:
            return res[0]["path"]
        
        
    
    def upDateRepository(self):
        """
        
        """
        print "upDateRepository"
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    