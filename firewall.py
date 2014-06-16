'''
Created on 01 июня 2014 г.

@author: volodja
'''


from network.interface  import Interface
from network.iptables   import IPTables, Protocol, Direction


def configureFirewallDesktop():
    iptables    = IPTables()
    internet    = Interface("eth1")
    udp         = Protocol.UDP
    tcp         = Protocol.TCP
    output      = Direction.OUTPUT
    
    ##### initialize
    iptables.configureModrobe()
    iptables.disableIPv6()
    iptables.resetRules()
    iptables.disableForward()
    iptables.dropAllDefault()
    iptables.enableSequrityCommon()
    iptables.acceptLoInterface()
    iptables.acceptEstabilishedPackets()

    ##### internet
    i = internet 
    # ICMP
    iptables.acceptICMP(i)
    # SSH client
    iptables.acceptPort             (i, output, [tcp]       , [22])
    # transmission remote gui client
    iptables.acceptPort             (i, output, [tcp]       , [9091])
    # NFS client
    iptables.acceptPortToPort       (i, output, [tcp]       , 2049              , "512:1024")
    # NTP client
    iptables.acceptPortToPort       (i, output, [udp]       , 123               , 123)
    # proxy client
    iptables.acceptPort             (i, output, [tcp]       , [3128])
    # quake 3 client
    iptables.acceptPort             (i, output, [udp]       , [27960])
    
    ##### save config
    iptables.save("/etc/iptables.config")


def configureFirewallServer():
    iptables    = IPTables()
    internet    = Interface("ppp0")
    local       = Interface("eth1")
    wifi        = Interface("wlan0")
    udp         = Protocol.UDP
    tcp         = Protocol.TCP
    input       = Direction.INPUT
    output      = Direction.OUTPUT

    
    ##### initialize
    iptables.configureModrobe()
    iptables.disableIPv6()
    iptables.resetRules()
    iptables.disableForward()
    iptables.dropAllDefault()
    iptables.enableSequrityCommon()
    iptables.acceptLoInterface()
    iptables.acceptEstabilishedPackets()

    
    ##### internet
    i = internet 
    # icmp
    iptables.acceptICMP(i)

    ### client
    # authorization
    iptables.acceptPort             (i, output, [udp]       , [113])
    # NTP client
    iptables.acceptPortToPort       (i, output, [udp]       , 123               , 123)
    # DHCP client
    iptables.acceptPortToPort       (i, output, [udp]       , 68                , 67)
    # browser, http, https
    iptables.acceptPort             (i, output, [tcp]       , [80, 443])
    # DNS
    iptables.acceptPort             (i, output, [udp]       , [53])
    # transmission client
    iptables.acceptPort             (i, output, [tcp]       , ["65500:65535"])
    #  
    ## server
    # quake 3 server
    iptables.acceptPort             (i, input,  [udp]       , [27960])
    # nginx http server
    iptables.acceptPort             (i, input,  [tcp]       , [80])
    # transmission incoming ports
    iptables.acceptPort             (i, input,  [tcp, udp]  , [51413])
    
    
    ##### local
    i = local
    
    ### server
    # DHCP server
    iptables.acceptPortToPort       (i, input,  [udp]       , 68                , 67)
    # DNS server
    iptables.acceptPort             (i, input,  [udp]       , [53])
    # SSH server
    iptables.acceptPort             (i, input,  [tcp]       , [22])
    # NFS server
    iptables.acceptPortToPort       (i, input,  [tcp]       , "512:1024"        , 2049)
    # transmission remote gui server
    iptables.acceptPort             (i, input,  [tcp]       , [9091])
    # samba server
    iptables.acceptPort             (i, input,  [tcp]       , ["137:139"        , 445])
    # squid proxy server
    iptables.acceptPort             (i, input,  [tcp]       , [3128])
    
    
    ##### wifi
    i = wifi
    
    ### server
    # DNS server
    iptables.acceptPort             (i, input,  [udp]       , [53])
    # DHCP server
    iptables.acceptPortToPort       (i, input,  [udp]       , 68                , 67)
    # squid proxy server
    iptables.acceptPort             (i, input,  [tcp]       , [3128])

    
    ##### forward
    
    ### internet - local
    # quake 3 from desktop to server
    iptables.forward                (internet               , local             , [udp]     , [27960])
    
    ### internet - wifi
    # icmp
    iptables.forwardICMP            (internet               , wifi)
    # https
    iptables.forward                (internet               , wifi              , [tcp]     , [443])
    # http to transparent proxy
    iptables.rerouteHTTPToTransparentProxy(wifi, 3128)
    # PPPOE MTU processing
    iptables.enableForwardMTUProcessing(wifi, internet)
    
    
    ##### finalize
    iptables.acceptMasquerading(internet)
    iptables.enableForward()

    iptables.save("/etc/iptables.config")


# configureFirewallServer()
# configureFirewallDesktop()
