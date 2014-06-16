'''
Created on 12 июня 2014 г.

@author: volodja
'''


import unittest
import enum
from enum import unique


@unique
class TestEnum(enum.Enum):
    ENUM1 = 1
    ENUM2 = 2
    ENUM3 = 3
    
class Test(unittest.TestCase):

    def setUp(self):
        pass
        
        
    def testEnum(self):
        e1 = TestEnum.ENUM1
        e2 = TestEnum.ENUM2
        print("e1 = " + str(e1))
        print(str(e1.name))
        print(str(e1.value))
        print(TestEnum.ENUM1)
        print(TestEnum["ENUM1"])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test']
    unittest.main()
    