from ctypes import *


#class ProjectorCorrectApi(object):
#def __init__(self):
cpplib = CDLL("ProjCalLibApi/pro_correction.dll", winmode=0)
cpplib.doubleTest.argtypes = [c_double]
cpplib.doubleTest.restype = c_double
rst = cpplib.doubleTest(3.6)
print("doubleTest return value ", rst)


