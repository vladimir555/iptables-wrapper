'''
Created on 14 июня 2014 г.

@author: volodja
'''


from network.iptables import Protocol, Direction
from enum import Enum, unique


@unique
class Profile(Enum):
    Quake3          = {Protocol: [Protocol.UDP], "dst_port": [27960]}
    Authorization   = {Protocol: [Protocol.UDP], "dst_port": [113]}
    DNS             = {Protocol: [Protocol.UDP], "dst_port": [53]}
    DHCP            = {Protocol: [Protocol.UDP], "dst_port": 68,        "src_port": 67}
    NTP             = {Protocol: [Protocol.UDP], "dst_port": 123,       "src_port": 123}
    NFS             = {Protocol: [Protocol.TCP], "dst_port": 2049,      "src_port": "512:1024"}
    Samba           = {Protocol: [Protocol.TCP], "dst_port": 445,       "src_port": "137:139"}
    SSH             = {Protocol: [Protocol.TCP], "dst_port": [22]}
    HTTP            = {Protocol: [Protocol.TCP], "dst_port": [80]}
    HTTPS           = {Protocol: [Protocol.TCP], "dst_port": [443]}
    Transmission    = {Protocol: [Protocol.TCP], "dst_port": ["65500:65535"]}
    TransmissionGUI = {Protocol: [Protocol.TCP], "dst_port": [9091]}
    Proxy           = {Protocol: [Protocol.TCP], "dst_port": [3128]}
    Linphone        = {Protocol: [Protocol.TCP], "dst_port": [5060]}
    

class Firewall():
    
    def __init__(self, iptables):
        self.iptables   = iptables

        ##### initialize
        self.iptables.configureModrobe()
        self.iptables.disableIPv6()
        self.iptables.resetRules()
        self.iptables.disableForward()
        self.iptables.dropAllDefault()
        self.iptables.enableSequrityCommon()
        self.iptables.acceptLoInterface()
        self.iptables.acceptEstabilishedPackets()
        
    def allowClient(self, interface_list, profile_list):
        for i in interface_list:
            for profile in profile_list:
                profile = profile.value
                if "src_port" in profile:
                    self.iptables.acceptPortToPort  (i, Direction.OUTPUT, profile[Protocol], profile["dst_port"], profile["src_port"])
                else:
                    self.iptables.acceptPort        (i, Direction.OUTPUT, profile[Protocol], profile["dst_port"])

    def allowServer(self, interface_list, profile_list):
        for i in interface_list:
            for profile in profile_list:
                profile = profile.value
                if "src_port" in profile:
                    self.iptables.acceptPortToPort  (i, Direction.INPUT,  profile[Protocol], profile["src_port"], profile["dst_port"])
                else:
                    self.iptables.acceptPort        (i, Direction.INPUT,  profile[Protocol], profile["dst_port"])

    def forward(self, interface_out, interface_in_list, profile_list):
        for i in interface_in_list:
            for profile in profile_list:
                profile = profile.value
                self.iptables.forward(interface_out, i, profile[Protocol], profile["dst_port"])

    def allowICMP(self, interface_list):
        for i in interface_list:
            self.iptables.acceptICMP(i)

    def forwardICMP(self, interface_out, interface_in_list):
        for i in interface_in_list:
            self.iptables.forwardICMP(interface_out, i)

    def rerouteHTTPToTransparentProxy(self, interface_list):
        for i in interface_list:
            self.iptables.rerouteHTTPToTransparentProxy(i, 3128)
            