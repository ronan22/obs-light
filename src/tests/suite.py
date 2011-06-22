import StringIO
import sys
import os


#sys.path.append("/home/me/mypy") 

cwdPath=os.getcwd()
i=cwdPath.rindex(os.sep)
sys.path.append(cwdPath[:i])


import TestAddProject


sferr = StringIO.StringIO()
sys.stderr=sferr

TestAddProject.testRun(sferr)






