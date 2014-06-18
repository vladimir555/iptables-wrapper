'''
Created on 01 июня 2014 г.

@author: volodja
'''


from utility.shell      import executeShellCommand
from network.interface  import Interface
from enum               import Enum, unique


@unique
class Direction(Enum):
#     BOTH    = 0
    INPUT   = 1
    OUTPUT  = 2
   

@unique
class Protocol(Enum):
    UDP     = "udp"
    TCP     = "tcp"
    ICMP    = "icmp"
    
    def getIPTablesParam(self):
        return "-p " + self.value + " -m " + self.value

    def getIPTablesParamNotSyn(self):
        if self.value == "tcp":
            return " ! --syn"
        else:
            return ""
    

class IPTables():
    def __init__(self):
        self.__unprivileged_ports   = "1024:65535"
    
    def configureModrobe(self):
        executeShellCommand("/sbin/modprobe ip_conntrack_ftp")
        executeShellCommand("/sbin/modprobe ip_tables")
        executeShellCommand("/sbin/modprobe ip_conntrack")
        executeShellCommand("/sbin/modprobe iptable_filter")
        executeShellCommand("/sbin/modprobe iptable_mangle")
        executeShellCommand("/sbin/modprobe iptable_nat")
        executeShellCommand("/sbin/modprobe ipt_LOG")
        executeShellCommand("/sbin/modprobe ipt_limit")
        executeShellCommand("/sbin/modprobe ipt_state")
        executeShellCommand("sysctl -w net.ipv4.tcp_syncookies=1")

    def disableIPv6(self):
        executeShellCommand("echo 1 > /proc/sys/net/ipv6/conf/all/disable_ipv6")
        executeShellCommand("echo 1 > /proc/sys/net/ipv6/conf/default/disable_ipv6")

    def disableForward(self):
        executeShellCommand("echo 0 > /proc/sys/net/ipv4/ip_forward")
        executeShellCommand("echo 0 > /proc/sys/net/ipv4/ip_dynaddr")

    def enableForward(self):
        executeShellCommand("echo 1 > /proc/sys/net/ipv4/ip_forward")
        executeShellCommand("echo 1 > /proc/sys/net/ipv4/ip_dynaddr")

    def resetRules(self):
        executeShellCommand("iptables -t mangle  -X")
        executeShellCommand("iptables -t nat     -X")
        executeShellCommand("iptables -t filter  -X")
        executeShellCommand("iptables -t raw     -X")
        executeShellCommand("iptables -t mangle  -F")
        executeShellCommand("iptables -t nat     -F")
        executeShellCommand("iptables -t filter  -F")
        executeShellCommand("iptables -t raw     -F")

    def dropAllDefault(self):
        executeShellCommand("iptables -P INPUT     DROP")
        executeShellCommand("iptables -P OUTPUT    DROP")
        executeShellCommand("iptables -P FORWARD   DROP")

        
    def acceptPort(self, interface, direction, protocol_list, port_list):
        i = interface.getName()
        u = self.__unprivileged_ports

        for protocol in protocol_list:
            p = protocol.getIPTablesParam()

            for port in port_list:
                port = str(port)

                if direction is Direction.OUTPUT:
                    si = protocol.getIPTablesParamNotSyn()
                    so = ""
                    pi = " --dport " + u + " --sport " + port 
                    po = " --sport " + u + " --dport " + port
                     
                if direction is Direction.INPUT:
                    so = protocol.getIPTablesParamNotSyn()
                    si = ""
                    pi = " --sport " + u + " --dport " + port 
                    po = " --dport " + u + " --sport " + port 

                executeShellCommand("iptables -A  INPUT -i " + i + " " + p + pi + " -j ACCEPT " + si)
                executeShellCommand("iptables -A OUTPUT -o " + i + " " + p + po + " -j ACCEPT " + so)

    def acceptPortToPort(self, interface, direction, protocol_list, source_port, dest_port):
        i           = interface.getName()
        source_port = str(source_port)
        dest_port   = str(dest_port)

        for protocol in protocol_list:
            if direction is Direction.OUTPUT:
                si = protocol.getIPTablesParamNotSyn()
                so = ""
                pi = " --dport " + dest_port + " --sport " + source_port 
                po = " --sport " + dest_port + " --dport " + source_port
            
            if direction is Direction.INPUT:
                so = protocol.getIPTablesParamNotSyn()
                si = ""
                pi = " --sport " + source_port + " --dport " + dest_port 
                po = " --dport " + source_port + " --sport " + dest_port

            p           = protocol.getIPTablesParam()
            source_port = str(source_port) 
            dest_port   = str(dest_port)
                
            executeShellCommand("iptables -A  INPUT -i " + i + " " + p + pi + " -j ACCEPT" + si)
            executeShellCommand("iptables -A OUTPUT -o " + i + " " + p + po + " -j ACCEPT" + so)

    def forward(self, interface_out, interface_in, protocol_list, port_list):
        i = interface_in.getName()
        o = interface_out.getName()
        u = self.__unprivileged_ports
        for protocol in protocol_list:
            p = protocol.getIPTablesParam() 

            for port in port_list:
                port    = str(port)
                executeShellCommand("iptables -A FORWARD -i " + i + " -o " + o + " " + p + " --sport " + u    + " --dport " + port + " -j ACCEPT")
                executeShellCommand("iptables -A FORWARD -o " + i + " -i " + o + " " + p + " --sport " + port + " --dport " + u    + " -j ACCEPT" + protocol.getIPTablesParamNotSyn())

    def forwardICMP(self, interface_out, interface_in):
        i = interface_in.getName()
        o = interface_out.getName()
        executeShellCommand("iptables -A FORWARD -i " + i + " -o " + o + " -p icmp -m icmp --icmp-type any -j ACCEPT")
        executeShellCommand("iptables -A FORWARD -o " + i + " -i " + o + " -p icmp -m icmp --icmp-type any -j ACCEPT")

    def rerouteHTTPToTransparentProxy(self, interface_in, proxy_port):
        i = interface_in.getName()
        d = interface_in.getIPv4()
        dd= "192.168.1.0"
        executeShellCommand("iptables -t nat -A PREROUTING ! -d " + d + "/24 -i " + i + " -p tcp -m multiport --dports 80 -j DNAT --to-destination " + d + ":3128")
        
    def acceptMasquerading(self, interface_out):
        i = interface_out.getName()
        executeShellCommand("iptables -t nat -A POSTROUTING -o " + i + " -j MASQUERADE")
        
    def acceptICMP(self, interface):
        i = interface.getName()
        executeShellCommand("iptables -A  INPUT -i " + i + " -p icmp -m icmp --icmp-type any -j ACCEPT")
        executeShellCommand("iptables -A OUTPUT -o " + i + " -p icmp -m icmp --icmp-type any -j ACCEPT")

    def enableForwardMTUProcessing(self, interface_in, interface_out):
        i = interface_in.getName()
        o = interface_out.getName()
        executeShellCommand("iptables -I FORWARD -i " + i + " -o " + o + " -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu")
        executeShellCommand("iptables -I FORWARD -o " + i + " -i " + o + " -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu")

    def enableSequrityXServer(self):
        executeShellCommand("iptables -A  INPUT -p tcp -m tcp --dport 6000:6063 -j DROP --syn")

    def enableSequrityLoInterface(self):
        executeShellCommand("iptables -A  INPUT ! -i lo -m state --state NEW -j DROP")

    def acceptLoInterface(self):
        executeShellCommand("iptables -A  INPUT -i lo -j ACCEPT")
        executeShellCommand("iptables -A OUTPUT -o lo -j ACCEPT")

    def enableSequrityLoAddress(self):
        executeShellCommand("iptables -A  INPUT -s 127.0.0.1/8 ! -i lo -j DROP")

    def enableSequritySpoofing(self):
        executeShellCommand("iptables -A  INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -m state --state NEW -j REJECT --reject-with tcp-reset")
        
    def enableSequrityUnknownStatusPackets(self):
        executeShellCommand("iptables -A  INPUT  -m state --state INVALID -j DROP")
        executeShellCommand("iptables -A FORWARD -m state --state INVALID -j DROP")

    def enableSequritySynFlood(self):
        executeShellCommand("iptables -A  INPUT -p tcp -m tcp -m state --state NEW -j DROP ! --syn")
        executeShellCommand("iptables -A OUTPUT -p tcp -m tcp -m state --state NEW -j DROP ! --syn")

    def acceptEstabilishedPackets(self):
        executeShellCommand("iptables -A  INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")

    def enableSequrityUDPFlood(self):
        executeShellCommand("iptables -A  INPUT -p udp -m udp -s 0/0 --destination-port 138 -j DROP")
        executeShellCommand("iptables -A  INPUT -p udp -m udp -s 0/0 --destination-port 113 -j DROP")
        executeShellCommand("iptables -A  INPUT -p udp -m udp -s 0/0 --source-port 67 --destination-port 68 -j ACCEPT")
        executeShellCommand("iptables -A  INPUT -p udp -m udp -j RETURN")
        executeShellCommand("iptables -A OUTPUT -p udp -m udp -s 0/0 -j ACCEPT")

    def enableSequrityICMPRerouting(self):
        executeShellCommand("iptables -A  INPUT -p icmp --fragment -j DROP")
        executeShellCommand("iptables -A OUTPUT -p icmp --fragment -j DROP")
        
    def enableSequritySystemPorts(self):
        executeShellCommand("iptables -A  INPUT ! -i lo -p tcp -m tcp -m multiport --dports 630,640,783,3310,10000 -j DROP")
        executeShellCommand("iptables -A  INPUT ! -i lo -p udp -m udp -m multiport --dports 630,640,783,3310,10000 -j DROP")

    def enableSequrityCommon(self):
        self.enableSequrityXServer()
        self.enableSequrityLoAddress()
        #self.enableSequrityLoInterface()
        self.enableSequritySpoofing()
        self.enableSequrityUnknownStatusPackets()
        self.enableSequritySynFlood()
        #self.enableSequrityUDPFlood()
        self.enableSequrityICMPRerouting()
        self.enableSequritySystemPorts()

    def save(self, file_name):
        executeShellCommand("iptables-save > '" + file_name + "'")

