#!/usr/bin/env python
# encoding: utf-8
# This is an appliance config DB management program

import os
import sys
sys.path.append('./glue/usr/local/lib/python2.5/site-packages')
import config

# Get an argument to an alternate db file
if (len(sys.argv) > 1):
    confFile = sys.argv[1]
else:
    confFile = 'cfg/config.db'
    print 'No config database specified'

print 'Using file %s' % confFile
print 'Enter "help" or "?" for help.'
print 'Enter "quit" or "exit" to exit.'

myConfig = config.Config(confFile)

while True:
    cmd = raw_input('\n> ')
    if cmd == 'quit' or cmd == 'exit':
        break
    if cmd == 'help' or cmd == '':
        print 'Commands: set get del delete commit exit quit help'
    else:
        cmd = cmd.strip().split()
        # TODO: complete commands to closest match or display help
        if cmd[0] == 'get':
            if '*' in cmd[1] or '%' in cmd[1]:
                results = myConfig.getVars(cmd[1])
                for key, value in results.iteritems():
                    print('%s%s' % (key.ljust(45, ' '), str(value)))
            else:
                results = myConfig.getVar(cmd[1])
                print(results)
        elif cmd[0] == 'set':
            if cmd[2] == 'True' or cmd[2] == 'False': 
                myConfig.setVar(cmd[1], cmd[2] == 'True')
            elif ',' in cmd[2]:
                myConfig.setVar(cmd[1], cmd[2].split(','))
            else:
                myConfig.setVar(cmd[1], cmd[2])
        elif cmd[0] == 'del' or cmd[0] == 'delete':
            if '*' in cmd[1] or '%' in cmd[1]:
                myConfig.delVars(cmd[1])
            else:
                myConfig.delVar(cmd[1])
        elif cmd[0] == 'commit':
            myConfig.commit()
        else:
            print 'Commands: set get del delete commit exit quit help'
    cmd = ''
myConfig.close()
