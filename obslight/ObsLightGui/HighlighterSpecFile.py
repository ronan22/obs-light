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
        
        Structure=QtGui.QTextCharFormat()
        Structure.setForeground(QtGui.QColor.fromRgb(cvStrToColor("4e9a06")))
        
        Identifier=QtGui.QTextCharFormat()
        Identifier.setForeground(QtGui.QColor.fromRgb(cvStrToColor("06989a")))
        
        String=Statement
        Function=Statement
        Operator=Statement
        specOpts=Operator
        specWWWlink=Statement
        Error=Statement
        specSectionMacro=Statement
        specGlobalMacro=Statement
        
        specDate=Statement
        Number=Statement
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
        specConfigure    =["\./configure"]
        specScriptArea = ["^%prep",
                          "^%check",
                          "^%build",
                          "^%install",
                          "^%clean",
                          "^%pre",
                          "^%postun",
                          "^%preun",
                          "^%post",
                          "^%files"]
        specDescriptionArea = ['^%description']
        specPackageArea = ['^%package']   
        specDescriptionOpts =[]           
        specEmail         =["<=<[A-Za-z0-9_.-]+@([A-Za-z0-9_-]+.)+[A-Za-z]+>>="]             
        specError       =[]               
        specFilesDirective =['%(attrib|defattr|attr|dir|config|docdir|doc|lang|verify|ghost)']            
        specFilesOpts      =[]            
        specLicense        =[]  
            
        specMacroNameLocal  =["(%|\$)\{*_arch\}*",
                              "(%|\$)\{*_binary_payload\}*",
                              "(%|\$)\{*_bindir\}*",
                              "(%|\$)\{*_build\}*",
                              "(%|\$)\{*_build_alias\}*",
                              "(%|\$)\{*_build_cpu\}*",
                              "(%|\$)\{*_builddir\}*",
                              "(%|\$)\{*_build_os\}*",
                              "(%|\$)\{*_buildshell\}*",
                              "(%|\$)\{*_buildsubdir\}*",
                              "(%|\$)\{*_vendor\}*",
                              "(%|\$)\{*_bzip2bin\}*",
                              "(%|\$)\{*_datadirapache2.service\}*",
                              "(%|\$)\{*_dbpath\}*",
                              "(%|\$)\{*_dbpath_rebuild\}*",
                              "(%|\$)\{*_defaultdocdir\}*",
                              "(%|\$)\{*_docdir\}*",
                              "(%|\$)\{*_excludedocs\}*",
                              "(%|\$)\{*_exec_prefix\}*",
                              "(%|\$)\{*_fixgroup\}*",
                              "(%|\$)\{*_fixowner\}*",
                              "(%|\$)\{*_fixperms\}*",
                              "(%|\$)\{*_ftpport\}*",
                              "(%|\$)\{*_ftpproxy\}*",
                              "(%|\$)\{*_gpg_path\}*",
                              "(%|\$)\{*_gzipbin\}*",
                              "(%|\$)\{*_host\}*",
                              "(%|\$)\{*_alias\}*",
                              "(%|\$)\{*_host_cpu\}*",
                              "(%|\$)\{*_host_os\}*",
                              "(%|\$)\{*_host_vendor\}*",
                              "(%|\$)\{*_httpport\}*",
                              "(%|\$)\{*_httpproxy\}*",
                              "(%|\$)\{*_includedir\}*",
                              "(%|\$)\{*_infodir\}*",
                              "(%|\$)\{*_install_langs\}*",
                              "(%|\$)\{*_script_path\}*",
                              "(%|\$)\{*_instchangelog\}*",
                              "(%|\$)\{*_langpatt\}*",
                              "(%|\$)\{*_lib\}*",
                              "(%|\$)\{*_libdir\}*",
                              "(%|\$)\{*_libexecdir\}*",
                              "(%|\$)\{*_localstatedir\}*",
                              "(%|\$)\{*_netsharedpath\}*",
                              "(%|\$)\{*_oldincludedir\}*",
                              "(%|\$)\{*_os\}*",
                              "(%|\$)\{*_pgpbin\}*",
                              "(%|\$)\{*_path\}*",
                              "(%|\$)\{*_prefix\}*",
                              "(%|\$)\{*_provides\}*",
                              "(%|\$)\{*_rpmdir\}*",
                              "(%|\$)\{*_rpmfilename\}*",
                              "(%|\$)\{*_sbindir\}*",
                              "(%|\$)\{*_sharedstatedir\}*",
                              "(%|\$)\{*_signature\}*",
                              "(%|\$)\{*_sourcedir\}*",
                              "(%|\$)\{*_source_payload\}*",
                              "(%|\$)\{*_specdir\}*",
                              "(%|\$)\{*_srcrpmdir\}*",
                              "(%|\$)\{*_sysconfdir\}*",
                              "(%|\$)\{*_alias\}*",
                              "(%|\$)\{*_target_cpu\}*",
                              "(%|\$)\{*_target_os\}*",
                              "(%|\$)\{*_platform\}*",
                              "(%|\$)\{*_vendor\}*",
                              "(%|\$)\{*_timecheck\}*",
                              "(%|\$)\{*_topdir\}*",
                              "(%|\$)\{*_usr\}*",
                              "(%|\$)\{*_usrsrc\}*",
                              "(%|\$)\{*_var\}*",
                              "(%|\$)\{*_vendor\}*"]           

        specMacroNameOther  =["(%|\$)\{*buildroot\}*",
                              "(%|\$)\{*buildsubdir\}*",
                              "(%|\$)\{*distribution\}*",
                              "(%|\$)\{*disturl\}*",
                              "(%|\$)\{*ix86\}*",
                              "(%|\$)\{*name\}*",
                              "(%|\$)\{*nil\}*",
                              "(%|\$)\{*optflags\}*",
                              "(%|\$)\{*perl_sitearch\}*",
                              "(%|\$)\{*release\}*",
                              "(%|\$)\{*requires_eq\}*",
                              "(%|\$)\{*vendor\}*",
                              "(%|\$)\{*version\}*"]           
        
        specMonth        =["Jan",
                           "Feb",
                           "Mar",
                           "Apr",
                           "Jun",
                           "Jul",
                           "Aug",
                           "Sep",
                           "Nov",
                           "Dec",
                           "January",
                           "February",
                           "March",
                           "May",
                           "June",
                           "July",
                           "August",
                           "September",
                           "October",
                           "November",
                           "December"]              
        specNumber       =['(^-=|[ t]-=|-)[0-9.-]*[0-9]']              
        specPackageOpts   =['s-ns*w']             
        specPercent      =[]              
        specSpecialChar  =[]
        #start with $foo ${foo} %foo %{foo}             
        specSpecialVariables =["(%|\$)\{*RPM_BUILD_ROOT\}*",
                               "(%|\$)\{*RPM_BUILD_DIR\}*",
                               "(%|\$)\{*_SOURCE_DIR\}*",
                               "(%|\$)\{*_OPT_FLAGS\}*",
                               "(%|\$)\{*LDFLAGS\}*",
                               "(%|\$)\{*CC\}*",
                               "(%|\$)\{*CC_FLAGS\}*",
                               "(%|\$)\{*CFLAGS\}*",
                               "(%|\$)\{*CXX\}*",
                               "(%|\$)\{*CXXFLAGS\}*",
                               "(%|\$)\{*CPPFLAGS\}*"]
                  
        specSpecialVariablesNames   =["RPM_BUILD",
                                      "ROOT",
                                      "RPM_BUILD_DIR",
                                      "RPM_SOURCE_DIR",
                                      "RPM_OPT_FLAGS",
                                      "LDFLAGS",
                                      "CC",
                                      "CC_FLAGS",
                                      "CPPNAME",
                                      "CFLAGS",
                                      "CXX",
                                      "CXXFLAGS",
                                      "CPPFLAGS"]   
        specTarCommand        =[]         
        specURL            =['((https{0,1}|ftp)://|(www[23]{0,1}\.|ftp\.))[A-Za-z0-9._/~:,#-]+']     
        specURLMacro      =['((https{0,1}|ftp)://|(www[23]{0,1}\.|ftp\.))[A-Za-z0-9._/~:,#%\{\}-]+']
        
        specVariables     =[]         
        specWeekday       =["Mon","Tue","Thu","Fri","Sat","Sun"]           
        specListedFilesBin  =['/s=bin/']           
        specListedFilesDoc  =['/(man\d*|doc|info)>']           
        specListedFilesEtc  =['specListedFilesBin',
                              'specListedFilesLib',
                              'specListedFilesDoc',
                              'specListedFilesEtc',
                              'specListedFilesShare',
                              'specListedFilesPrefix',
                              'specVariables',
                              'specSpecialChar'] 
                                        
        specListedFilesLib   =['/(lib|include)/']          
        specListedFilesPrefix =['/(usr|local|opt|X11R6|X11)/']         
        specListedFilesShare  =['/share/']  
        
               
        self.highlightingRules = []
        
#  "main types color definitions
        self.highlightingRules.extend( (QtCore.QRegExp(i),Structure) for i in specSehIftion)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),Macro) for i in specSectionMacro )              
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
        self.highlightingRules.extend( (QtCore.QRegExp(i),Structure) for i in specScriptArea)
        self.highlightingRules.extend( (QtCore.QRegExp(i),Structure) for i in specDescriptionArea)
        self.highlightingRules.extend( (QtCore.QRegExp(i),Structure) for i in specPackageArea)
                          
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specDescriptionOpts)            
        self.highlightingRules.extend( (QtCore.QRegExp(i),specWWWlink) for i in specEmail)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Error) for i in specError)                      
#        self.highlightingRules.extend( (QtCore.QRegExp(i),specSectionMacro) for i in specFilesDirective)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specFilesOpts)                  
        self.highlightingRules.extend( (QtCore.QRegExp(i),String) for i in specLicense)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Identifier) for i in specMacroNameLocal)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),Identifier) for i in specMacroNameOther)             
        self.highlightingRules.extend( (QtCore.QRegExp(i),specDate) for i in specMonth)                      
        self.highlightingRules.extend( (QtCore.QRegExp(i),Number) for i in specNumber)                     
        self.highlightingRules.extend( (QtCore.QRegExp(i),specOpts) for i in specPackageOpts)                
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specPercent)                    
        self.highlightingRules.extend( (QtCore.QRegExp(i),Special) for i in specSpecialChar)                
        self.highlightingRules.extend( (QtCore.QRegExp(i),Identifier) for i in specSpecialVariables)           
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
            
            
            
            
            