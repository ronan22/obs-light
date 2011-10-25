'''
Created on 24 oct. 2011

@author: meego
'''


VERBOSE=0
DEBUG=0

def obsLightPrint(text,isDebug=False,isVerbose=False ):
    '''
    
    '''
    if ((VERBOSE==1) and (isVerbose==1)) or ( (DEBUG==1) and (isDebug==1)) or (isDebug==False) and (isVerbose==False):
        print text

    