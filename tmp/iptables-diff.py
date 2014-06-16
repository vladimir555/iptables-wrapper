# -*- coding: utf-8 -*-
'''
Created on 05 июня 2014 г.

@author: volodja
'''

#iptables_config = open('iptables.rules.1').readlines()
#iptables_rules  = open('iptables.config.1').readlines()

iptables_config = open('1').readlines()
iptables_rules  = open('2').readlines()

for rules_line in iptables_rules:
    rules = rules_line.strip()
    is_found = False
    for config_line in iptables_config:
        config = config_line.strip()
#         print("compare '" + rules + "' and '" + config + "'")
        if rules_line == config_line:
            is_found = True
            break
    if not is_found:
        print(rules)
        