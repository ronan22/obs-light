# -*- coding: utf8 -*-
#
# Copyright 2011-2012, Intel Inc.
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
'''
Created on 28 nov. 2012

@author: Ronan Le Martret
'''


from PySide import  QtGui,QtCore

def cvStrToColor(val):
#    r=int(val[:2],16)
#    g=int(val[2:-2],16)
#    b=int(val[-2:],16)
    return int(val,16)
    


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        Comment = QtGui.QTextCharFormat()
        Comment.setForeground(QtGui.QColor.fromRgb(cvStrToColor("80a0ff")))
#        CommentFormat.setFontWeight(QtGui.QFont.Bold)
        
        Statement = QtGui.QTextCharFormat()
        Statement.setForeground(QtGui.QColor.fromRgb(cvStrToColor("c4a000")))

        Special =QtGui.QTextCharFormat()
        Special.setForeground(QtGui.QColor.fromRgb(cvStrToColor("c4a0ff")))
        
        
        String=Statement
        Function=Statement
        Operator=Statement
        specOpts=Operator
        specWWWlink=Statement
        Error=Statement
        specSectionMacro=Statement
        specGlobalMacro=Statement
        Identifier=Statement
        specDate=Statement
        
        
        Macro=QtGui.QTextCharFormat()
        Macro.setForeground(QtGui.QColor.fromRgb(cvStrToColor("75507b")))
        
#  "main types color definitions
        specSehIftion                  =[] 
        specSectionMacro               =['^%define\\b',
                                         '^%patch\d*',
                                         '^%setup\\b',
                                         '^%configure\\b',
                                         '^%GNUconfigure\\b',
                                         '^%find_lang\\b',
                                         '^%makeinstall\\b',
                                         '^%include\\b'] 
        
        specWWWlink                    =[] 
#        specOpts                       =[] 
        specGlobalMacro              =[] 

#       sh colors
        shComment = ['#.*$']                     
        shIf       =["\\bif\\b","\\bfi\\b"]                    
        shOperator  =['[><|!&;]','[!=]=']                   
        shQuote1    =["\'"]                   
        shQuote2    =["\""]                   
        shQuoteDelim =[]                  

#       spec colors
        specBlock     =["\\bdo\\b" ,"\\bdone\\b"]                 
        specColon     =[':']                 
        specCommand    =['^Prereq\\b',
                         '^Summary\\b',
                         '^Name\\b',
                         '^Version\\b',
                         '^Packager\\b',
                         '^Requires\\b',
                         '^Icon\\b',
                         '^URL\\b',
                         '^Source\d*\\b',
                         '^Patch\d*\\b',
                         '^refix\\b',
                         '^Packager\\b',
                         '^Group\\b',
                         '^License\\b',
                         '^Release\\b',
                         '^BuildRoot\\b',
                         '^Distribution\\b',
                         '^Vendor\\b',
                         '^Provides\\b',
                         '^ExclusiveArch\\b',
                         '^ExcludeArch\\b',
                         '^ExclusiveOS\\b',
                         '^Obsoletes\\b',
                         '^BuildArch\\b',
                         '^BuildArchitectures\\b',
                         '^BuildRequires\\b',
                         '^BuildConflicts\\b',
                         '^BuildPreReq\\b',
                         '^Conflicts\\b',
                         '^AutoRequires\\b',
                         '^AutoReq\\b',
                         '^AutoReqProv\\b',
                         '^AutoProv\\b',
                         '^Epoch\\b',
                         '^Recommends\\b',
                         '^Suggests\\b',
                         '^Freshens\\b',
                         '^EssentialFor\\b',
                         '^Supplements\\b',
                         '^Enhances\\b']   
                     
        specCommandOpts  =  ["\\s-\\w+","\\s--\\w[a-zA-Z_-]+"]
        specCommandSpecial  =[]           
        specComment=['^\\s*#.*$']                    
        specConfigure    =[]              
        specDate      =[]                 
        specDescriptionOpts =[]           
        specEmail         =[]             
        specError       =[]               
        specFilesDirective =[]            
        specFilesOpts      =[]            
        specLicense        =[]            
        specMacroNameLocal  =[]           
        specMacroNameOther  =[]           
        specMonth        =[]              
        specNumber       =[]              
        specPackageOpts   =[]             
        specPercent      =[]              
        specSpecialChar  =[]              
        specSpecialVariables =[]          
        specSpecialVariablesNames   =[]   
        specTarCommand        =[]         
        specURL            =[]            
        specURLMacro      =[]             
        specVariables     =[]             
        specWeekday       =[]             
        specListedFilesBin  =[]           
        specListedFilesDoc  =[]           
        specListedFilesEtc  =[]           
        specListedFilesLib   =[]          
        specListedFilesPrefix =[]         
        specListedFilesShare  =[]  
        
               
        self.highlightingRules = []
        
#  "main types color definitions
        self.highlightingRules.extend( (QtCore.QRegExp(i),Structure) for i in specSehIftion)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),Macro) for i in specSectionMacro )              
        self.highlightingRules.extend( (QtCore.QRegExp(i),PreProc) for i in specWWWlink  )                  
#        self.highlightingRules.extend( (QtCore.QRegExp(i),Operator) for i in specOpts     )                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),Identifier) for i in specGlobalMacro )               
        
#  "sh colors
        self.highlightingRules.extend( (QtCore.QRegExp(i),Comment) for i in shComment)                       
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in shIf)                           
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in shOperator)                     
        self.highlightingRules.extend( (QtCore.QRegExp(i),String) for i in shQuote1)                       
        self.highlightingRules.extend( (QtCore.QRegExp(i),String) for i in shQuote2)                       
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in shQuoteDelim)                   

#  "spec colors
        self.highlightingRules.extend( (QtCore.QRegExp(i),Function) for i in specBlock)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specColon)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specCommand)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specCommandOpts)
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specCommandSpecial)
        self.highlightingRules.extend( (QtCore.QRegExp(i),Comment) for i in specComment)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specConfigure)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),String) for i in specDate)                       
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specDescriptionOpts)            
        self.highlightingRules.extend( (QtCore.QRegExp(i),specWWWlink) for i in specEmail)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Error) for i in specError)                      
#        self.highlightingRules.extend( (QtCore.QRegExp(i),specSectionMacro) for i in specFilesDirective)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specFilesOpts)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),String) for i in specLicense)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specMacroNameLocal)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specMacroNameOther)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),specDate) for i in specMonth)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Number) for i in specNumber)                     
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specPackageOpts)                
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specPercent)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specSpecialChar)                
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specSpecialVariables)           
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specSpecialVariablesNames)      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specTarCommand)                 
        self.highlightingRules.extend( (QtCore.QRegExp(i),specWWWlink) for i in specURL)                        
        self.highlightingRules.extend( (QtCore.QRegExp(i),specWWWlink) for i in specURLMacro)                   
        self.highlightingRules.extend( (QtCore.QRegExp(i),Identifier) for i in specVariables)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),specDate) for i in specWeekday)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesBin)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesDoc)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesEtc)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesLib)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesPrefix)          
        self.highlightingRules.extend( (QtCore.QRegExp(i),Statement) for i in specListedFilesShare)           
        
        
#        keywordPatterns = ["\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
#                "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
#                "\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
#                "\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
#                "\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
#                "\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
#                "\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
#                "\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
#                "\\bvolatile\\b"]


        



#        classFormat = QtGui.QTextCharFormat()
#        classFormat.setFontWeight(QtGui.QFont.Bold)
#        classFormat.setForeground(QtCore.Qt.darkMagenta)
#        
#        self.highlightingRules.append((QtCore.QRegExp("\\bQ[A-Za-z]+\\b"),classFormat))
#
#        singleLineCommentFormat = QtGui.QTextCharFormat()
#        singleLineCommentFormat.setForeground(QtCore.Qt.red)
#        self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"), singleLineCommentFormat))
#
#        self.multiLineCommentFormat = QtGui.QTextCharFormat()
#        self.multiLineCommentFormat.setForeground(QtCore.Qt.red)
#
#        quotationFormat = QtGui.QTextCharFormat()
#        quotationFormat.setForeground(QtCore.Qt.darkGreen)
#        self.highlightingRules.append((QtCore.QRegExp("\".*\""),quotationFormat))
#
#        functionFormat = QtGui.QTextCharFormat()
#        functionFormat.setFontItalic(True)
#        functionFormat.setForeground(QtCore.Qt.blue)
#        self.highlightingRules.append((QtCore.QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),functionFormat))

#        self.commentStartExpression = QtCore.QRegExp("/\\*")
#        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

#        self.setCurrentBlockState(0)
#
#        startIndex = 0
#        if self.previousBlockState() != 1:
#            startIndex = self.commentStartExpression.indexIn(text)
#
#        while startIndex >= 0:
#            endIndex = self.commentEndExpression.indexIn(text, startIndex)
#
#            if endIndex == -1:
#                self.setCurrentBlockState(1)
#                commentLength = len(text) - startIndex
#            else:
#                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
#
#            self.setFormat(startIndex, commentLength,self.multiLineCommentFormat)
#            startIndex = self.commentStartExpression.indexIn(text,startIndex + commentLength)
            
            
            
            
            