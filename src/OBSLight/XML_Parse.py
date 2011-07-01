'''
Created on 21 juin 2011
@author: hellmann
'''

from xml.etree import ElementTree
from pprint import pprint
import sys, string, time, os
import obslighterr

class XML_Parse(object):
    
    def __init__(self, aFileName=None):
        '''
        Constructor
        '''
        self.__FileName=aFileName #Name of the XML file to be parsed
        self.__DicoStorage={} #The dictionary created from the XML file 
        self.__NameSpaceDict={} #The auxiliary dictionary containing namespaces 
        self.__Tree=None
                
    def getDicoStorage(self):
        return self.__DicoStorage
    
    def setDicoStorage(self,aDicoStorage):
        self.__DicoStorage=aDicoStorage
    
    def getNameSpaceDict(self):
        return self.__NameSpaceDict
    
    def setNameSpaceDict(self,aNameSpaceDict):
        self.__NameSpaceDict=aNameSpaceDict
     
    # Prints with the pprint command an object like dictionary to a file  
    def printObj(self,aFileName=None,aObj=None):

        MyFName = aFileName
        MyStdout = sys.stdout
        MyFDescr = open(MyFName, mode='wt')
        sys.stdout = MyFDescr
        pprint(aObj)
        sys.stdout = MyStdout
        MyFDescr.close()
          
    # Dumps the dictionary to a XML file with the help of the ElementTree.write function      
    def dumpXML(self,aFileName=None):
        
        MyFName_1=aFileName
        root = ConvertDictToXml(self.__DicoStorage)
        tree = ElementTree.ElementTree(root)
        tree.write(MyFName_1)
        
    def ExistsXMLVerif(self,aFileName=None):
                
        MyFileName = aFileName
        if not os.path.exists(MyFileName):
            raise obslighterr.XMLExistenceError("The XML file " + MyFileName + " does not exist")
        return 0
    
    def EmptyXMLVerif(self,aFileName=None):
        
        MyFileName = aFileName        
        if os.stat(MyFileName)[6]==0:
            raise obslighterr.XMLEmptyFileError("The XML file " + MyFileName + " is empty")
        return 0
    
    def StructureXMLVerif(self,aFileName=None):
        
        MyFileName = aFileName
        try:
            tree = ElementTree.parse(MyFileName)
        except:
            raise obslighterr.XMLParseFileError("The file " + MyFileName + " cannot not be parsed, probably does not respect XML standard")
        return 0

    def ConvertDictToXMLVerif(self,aDict=None,aXMLOutFile=None):             
                 
        MyDict = aDict
        try:      
            root = ConvertDictToXml(MyDict)
            tree = ElementTree.ElementTree(root)
        except:
            raise obslighterr.XMLDictToXMLError("The dictionary " + MyDict + " cannot not be converted to an XML file ")
        
        if aXMLOutFile != None:
        
            MyXMLOutFile = aXMLOutFile
            MyTempFName=MyXMLOutFile.replace('.xml','.temp.xml') 
            tree.write(MyTempFName) 
            
            MyCommand_1="xmllint --format '" + MyTempFName +  "' > '" + MyXMLOutFile + "'"
            MyCommand_2="rm -rf '" + MyTempFName + "'"
            os.system(MyCommand_1)
            os.system(MyCommand_2)
        
        return 0         
               
    # Parses the XML file and creates a dictionary            
    def parseXML(self, aFileName=None):
        
        MyFName = aFileName
        '''
        # Begin namespace treatment included
        MyFNameNmsp = MyFName.replace('.xml','.nmsp.xml')
        replaceString(MyFName, MyFNameNmsp,'xmlns=', 'xmlns:my=')
        self.__DicoStorage = ConvertXmlToDict(MyFNameNmsp)
        # End namespace treatment included
        '''
        self.__DicoStorage = ConvertXmlToDict(MyFName)      
    
    # Allows the modification of the dictionary   
    def modifyDict(self):
  
        #       
        # 1.possibility: self.__DicoStorage['comps']['group']['packagelist']['packagereq']['_text'] = 'red'
        # 2.possibility: self.__DicoStorage.comps.group[0].packagelist.packagereq[0]._text = 'red'
        
        return self.__DicoStorage
    

    
def replaceString(aInpFileName,aOutFileName,aInStr,aOutStr):

        '''
        This function allows the replacement of all occurrences 
        of a given string in a file via another string. The new 
        content is subsequently stored in a file. The name of the 
        output file can be the same as that of the input file.
        ''' 
        MyInpFileName = aInpFileName
        MyOutFileName = aOutFileName
        MyInpFDescr = open(MyInpFileName,'r')
        content = MyInpFDescr.read()              # read the entire input file into memory
        MyInpFDescr.close()
        MyOutFDescr = open(MyOutFileName, 'w')             
        MyOutFDescr.write(content.replace(aInStr, aOutStr))  # write the file with the text substitution
        MyOutFDescr.close()

'''
Copyright
@author of the original version located at

http://code.activestate.com/recipes/573463-converting-xml-to-dictionary-and-back/

of the class XmlDictObject and of the functions _ConvertDictToXmlRecurse, ConvertDictToXml, 
_ConvertXmlToDictRecurse, ConvertXmlToDict 

is Cory Fabre. It is distributed under the PSF license. 

Slight modifications have been introduced in the original code by Gustav Hellmann 
in June 2011.

Namely, a substring "attr_" is now added to the attributes when the input XML file 
is converted to the dictionary. Likewise, when converting the (modified) dictionary 
back to a XML, the "attr_" substring is deleted and the attributes are put on their 
original location within the XML file. Without these modifications the attributes 
would be treated like tag text during the reverse conversion Dictionary->XML, and 
the original presentation of the XML document would not be conserved. In a later 
version one may also create the dictionary keys "attrib" and "text". 
  
'''

class XmlDictObject(dict):
    """
    Adds object like functionality to the standard dictionary.
    """
    def __init__(self, initdict=None):
        if initdict is None:
            initdict = {}
        dict.__init__(self, initdict)
    def __getattr__(self, item):
        return self.__getitem__(item)
    def __setattr__(self, item, value):
        self.__setitem__(item, value)
    def __str__(self):
        if self.has_key('_text'):
            return self.__getitem__('_text')
        else:
            return ''

    @staticmethod
    def Wrap(x):
        """
        Static method to wrap a dictionary recursively as an XmlDictObject
        """

        if isinstance(x, dict):
            return XmlDictObject((k, XmlDictObject.Wrap(v)) for (k, v) in x.iteritems())
        elif isinstance(x, list):
            return [XmlDictObject.Wrap(v) for v in x]
        else:
            return x

    @staticmethod
    def _UnWrap(x):
        if isinstance(x, dict):
            return dict((k, XmlDictObject._UnWrap(v)) for (k, v) in x.iteritems())
        elif isinstance(x, list):
            return [XmlDictObject._UnWrap(v) for v in x]
        else:
            return x
        
    def UnWrap(self):
        """
        Recursively converts an XmlDictObject to a standard dictionary and returns the result.
        """
        return XmlDictObject._UnWrap(self)

def _ConvertDictToXmlRecurse(parent, dictitem):
    assert type(dictitem) is not type([])

    parent.attrib = {}
    if isinstance(dictitem, dict):
        for (tag, child) in dictitem.iteritems():
            if str(tag) == '_text':
                parent.text = str(child)
            elif 'attr_' in str(tag):
                my_dict = parent.attrib
                my_dict.update({str(tag).split('_')[1]:str(child)})               
                parent.attrib = my_dict
            elif type(child) is type([]):
                # iterate through the array and convert
                for listchild in child:
                    elem = ElementTree.Element(tag)
                    parent.append(elem)
                    _ConvertDictToXmlRecurse(elem, listchild)
            else: 
                elem = ElementTree.Element(tag)
                parent.append(elem)
                _ConvertDictToXmlRecurse(elem, child)
    else:
        parent.text = str(dictitem)
      

def ConvertDictToXml(xmldict):
    """
    Converts a dictionary to an XML ElementTree Element 
    """
    roottag = xmldict.keys()[0]
    root = ElementTree.Element(roottag)
    _ConvertDictToXmlRecurse(root, xmldict[roottag])
    return root

def _ConvertXmlToDictRecurse(node, dictclass):
    nodedict = dictclass()
    node_attr_in = dictclass()
    node_attr_out = dictclass()
    
    if len(node.items()) > 0:
        # if we have attributes, set them
        node_attr_in = dict(node.items())
        for (k,v) in node_attr_in.iteritems():
            node_attr_out ['attr_' + str(k)] = v 
        nodedict.update(node_attr_out)
           
    for child in node:
        # recursively add the element's children
        newitem = _ConvertXmlToDictRecurse(child, dictclass)
        if nodedict.has_key(child.tag):
            # found duplicate tag, force a list
            if type(nodedict[child.tag]) is type([]):
                # append to existing list
                nodedict[child.tag].append(newitem)
            else:
                # convert to list
                nodedict[child.tag] = [nodedict[child.tag], newitem]
        else:
            # only one, directly set the dictionary
            nodedict[child.tag] = newitem

    if node.text is None: 
        text = ''
    else: 
        text = node.text.strip()
    
    if len(nodedict) > 0:            
        # if we have a dictionary add the text as a dictionary value (if there is any)
        if len(text) > 0:
            nodedict['_text'] = text
    else:
        # if we don't have child nodes or attributes, just set the text
        nodedict = text
        
    return nodedict


def ConvertXmlToDict(root, dictclass=XmlDictObject):
    """
    Converts an XML file or ElementTree Element to a dictionary
    """
    if type(root) == type(''):
        root = ElementTree.parse(root).getroot()
    elif not isinstance(root, ElementTree.Element):
        raise TypeError, 'Expected ElementTree.Element or file path string'
   
    root =  ElementTree.ElementTree(root).getroot()
    return dictclass({root.tag: _ConvertXmlToDictRecurse(root, dictclass)})


def main():
         
    """
    exec the main 
    """
    IN_XML_FILE_NAME = '/home/hellmann/XML_files/input.xml' #The XML input file
    OUT_XML_FILE_NAME = '/home/hellmann/XML_files/output.xml' #The XML output file
    DICT_FILE_NAME = '/home/hellmann/XML_files/output.dict' #The dictionary obtained from the XML file
        
    MyOutFName=OUT_XML_FILE_NAME
    MyTempFName=MyOutFName.replace('.xml','.temp.xml') #The output XML file will be first written into a temp file
            
    aParseXML_cli = XML_Parse()        
    aParseXML_cli.parseXML(IN_XML_FILE_NAME)
    #For eventual modification of a dictionary
    #self.modifyDict()
    aParseXML_cli.printObj(DICT_FILE_NAME,aParseXML_cli.getDicoStorage())
    aParseXML_cli.dumpXML(MyTempFName)
            
    #The xmllint command will format the output XML file, in particular newlines will be added if necessary    
    MyCommand_1="xmllint --format '" + MyTempFName +  "' > '" + MyOutFName + "'"
    MyCommand_2="rm -rf '" + MyTempFName + "'"
    os.system(MyCommand_1)
    os.system(MyCommand_2)
            
    #return self.execute()
    return 0
        
if __name__ == '__main__':
    main()

    