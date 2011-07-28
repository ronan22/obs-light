'''
Created on 22 juil. 2011

@author: rmartret
'''
import sys



class SPEC_Parse:
    def __init__(self,path=None):

        self.__prepFlag="%prep"
        self.__buildFlag="%build"
        self.__installFlag="%install"
        self.__cleanFlag="%clean"
        self.__kernel_variant_preunFlag="%kernel_variant_preun" 
        self.__kernel_variant_postFlag="%kernel_variant_post"
        self.__changelogFlag="%changelog"

        self.__initList=[""]
        self.__prepList=["",self.__prepFlag,""]
        self.__buildList=["",self.__buildFlag,""]
        self.__installList=["",self.__installFlag,""]
        self.__cleanList=["",self.__cleanFlag,""]
        self.__kernel_variant_preunList=["",self.__kernel_variant_preunFlag,""]
        self.__kernel_variant_postList=["",self.__kernel_variant_postFlag,""] 
        self.__changelogList=["",self.__changelogFlag,""]

        if path != None:
            self.parseFile(path)

        
            
    def parseFile(self,path=None):
        if path != None:
            tmpLineList=[]
            
            f=open(path,'r')
            for line in f:
                tmpLineList.append(line)
            f.close()    
            endAt=len(tmpLineList)
            
            par=range(len(tmpLineList))
            par.reverse()
            for i in par:
                if tmpLineList[i].startswith(self.__prepFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__initList = tmpLineList[:lastIndex]
                    self.__prepList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    break
                    
                elif tmpLineList[i].startswith(self.__buildFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__buildList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    
                elif tmpLineList[i].startswith(self.__installFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__installList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    
                elif tmpLineList[i].startswith(self.__cleanFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__cleanList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    
                elif tmpLineList[i].startswith(self.__kernel_variant_preunFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__kernel_variant_preunList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    
                elif tmpLineList[i].startswith(self.__kernel_variant_postFlag):
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__kernel_variant_postList = tmpLineList[lastIndex:endAt]
                    endAt=lastIndex
                    
                elif tmpLineList[i].startswith(self.__changelogFlag):                                                                                           
                    lastIndex=self.__findLastIndex(tmpLineList,i)
                    self.__changelogList = tmpLineList[lastIndex:]
                    endAt=lastIndex
                    
        else:
            print "ERROR"
    
    def addpatch(self,file):
        patchID=100
        
        for line in self.__prepList:
            if line.startswith("Patch"):
                id=int(line.split(":")[0].replace("Patch", ""))
                if id>=patchID:
                    patchID+=1
        
        self.__prepList.append("Patch"+str(patchID)+": "+file)
    
    
    
    def __findLastIndex(self,list,index):
        tmpIndex=index-1

        while (1):

            if (tmpIndex>=0):
                if list[tmpIndex].startswith('#') | list[tmpIndex].startswith('\r') |list[tmpIndex].startswith('\n'):
                    tmpIndex-=1
                else:
                    return tmpIndex+1
            else:
                print "__findLastIndex ERROR"
                return 0
        
    def savefile(self,path=None):
        if path!=None:
            f=open(path,'w')
            
            for l in [ self.__initList,self.__prepList,self.__buildList,self.__installList,self.__cleanList,self.__kernel_variant_preunList,self.__kernel_variant_postList,self.__changelogList]:
                for line in l:
                    f.write(line)
            f.close()  
            
            
            

if __name__ == '__main__':
    s=SPEC_Parse( sys.argv[1])
    s.addpatch("test.patch")
    s.savefile(path+".sav")
    
    
    
    
    
    
    
    
    
    
    
    
    
    