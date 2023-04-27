from ctypes import *
import numpy as np

#cpplib = CDLL(".\\pro_correction.dll")
cpplib = CDLL("pro_correction.dll",winmode=0)
cpplib.doubleTest.argtypes = [c_double]
cpplib.doubleTest.restype = c_double
a =3.0
b =4.0

a1=np.array([0.1,0.2,3,4.6,5])
print(a1)
print(a1[3])

rst = cpplib.doubleTest(a)
print("rst: %s" ,rst)

rst = cpplib.doubleTest(a1[3])
print("rst2: %s" ,rst)

cpplib.doublePointTest.argtypes = [POINTER(c_double), POINTER(c_double)]
cpplib.doublePointTest.restype = c_double
d1 = c_double(100)
d2 = c_double(0)
rst = cpplib.doublePointTest(byref(d1),byref(d2))
print("rst:" ,rst)
print("d1:" ,d1)
print("d2:" ,d2)
