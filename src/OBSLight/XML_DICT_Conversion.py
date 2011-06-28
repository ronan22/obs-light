'''

@author of the original version located at

http://code.activestate.com/recipes/573463-converting-xml-to-dictionary-and-back/

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

from xml.etree import ElementTree

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


    