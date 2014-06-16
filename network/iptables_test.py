'''
Created on 13 июня 2014 г.

@author: volodja
'''


import unittest
from network.iptables import Protocol


class Test(unittest.TestCase):


    def testProtocol(self):
        udp = Protocol.UDP
        tcp = Protocol.TCP

        self.assertEqual(tcp.getIPTablesParamNotSyn(), " ! --syn")
        self.assertEqual(udp.getIPTablesParamNotSyn(), "")
        
        self.assertEqual(udp.getIPTablesParam(), "-p udp -m udp")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testProtocol']
    unittest.main()
