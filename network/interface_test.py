'''
Created on 31 мая 2014 г.

@author: volodja
'''
import unittest
import network.interface

class InterfaceTest(unittest.TestCase):

    def setUp(self):
        self.__i = network.interface.Interface("eth1")
        unittest.TestCase.setUp(self)
        
    def testGetInfo(self):
        info = self.__i.getInfo()
        print("network interface info:")
        for line in info: 
            print("    " + str(line))
        self.assertGreater(len(info), 5)
    
    def testGetIPv4(self):
        ip = self.__i.getIPv4()
        print("ip    = '" + ip + "'")
        self.assertEqual(3, ip.count('.'))

    def testGetMac(self):
        mac = self.__i.getMac()
        print("mac   = '" + mac + "'")
        self.assertEqual(5, mac.count(':'))

    def testGetMask(self):
        mask = self.__i.getIPv4Mask()
        print("mask  = '" + mask + "'")
        self.assertEqual(3, mask.count('.'))

if __name__ == "__main__":
    unittest.main()
