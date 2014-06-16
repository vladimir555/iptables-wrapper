'''
Created on 31 мая 2014 г.

@author: volodja
'''


import os


def executeShellCommand(command_line):
    command_line     = command_line.replace("$", "\\$")
    print("exec: " + command_line)
    result_pipe = os.popen(command_line)
    result_     = result_pipe.readlines()
    result      = []
    for line in result_:
        result.append(line.replace('\n', ''))
    return result
