from ctypes import WinDLL, CDLL
import ctypes

dll = WinDLL('python_test_lib.dll', winmode=0)

testInt = 10
print("type ", type(testInt))
result = dll.testInt(testInt)
print("result ", result)

test = 3.6
print("type ", type(test))
result = dll.testFloat(test)
print("result ", result)

