#!/usr/bin/env python
# This file is meant to be read in by console.py, compiled, and exec'ed

import os
import re
#import pyparsing
import MCP
import config
import socket
import md5
from time import sleep

class CLICommand(object):
    '''Split up a command into its parts: verb, adjective, and nouns
    ''' 
    def __init__(self):
        self.verb = ''
        self.adj = ''
        self.nouns = {}

    def getVerb(self):
        return self.verb

    def getAdj(self):
        return self.adj

    def getNouns(self):
        return self.nouns

    def setVerb(self, string):
        self.verb = string 
        return True

    def setAdj(self, string):
        self.adj = string 
        return True

    def setNoun(self, string1, string2=None):
        self.nouns[string1] = string2
        return True

    def parse(self, input=''):
        '''Parse a command from a string.  The grammar of a command is as follows:
           verb adjective noun property noun property ...
        '''
        # TODO: use pyparsing here.  regexes are sucking...
        singles = ('help', '?')

        line = re.split('\s+', input)
        lineLength = len(line)
        if lineLength > 0:
            self.setVerb(line[0])
        if lineLength > 1:
            self.setAdj(line[1])
        # if there are nouns, enter them in the noun dict
        if lineLength > 2:
            i = 2
            while i <= lineLength:
                if line[i] in singles:
                    self.setnoun(line[i])
                else:
                    self.setnoun(line[i], line[i+1])
                i += 2

        return True


myMcpClient = MCP.MCPAgent()

# Set up the connection to the system daemon
# Connect to server
try:
    conn = myMcpClient.connect(socket.AF_UNIX, socket.SOCK_STREAM, '/var/run/systemd.sock')
except socket.error, (strError):
    print 'Couldn\'t connect to host: %s' % (strError)
    exit(0)

# Create the message objects
sendMessage = MCP.MCPMessage()
recvMessage = MCP.MCPMessage()

# Set the userpass md5 hash before we continue
# TODO: If we get this far, presumably we've already authenticated via the
# unix mechanism, so get the md5userpass directly from the config db and use
# it.  The webgui will *NOT* do this...
md5userpass = md5.md5('roota').hexdigest()

# Spawn a keepalive thread
def keepalive(conn, seconds=30):
    while True:
        try:
            print 'sending keepalive'
            myMcpClient.send(MCP.MCPMessage(MCP.SYN), conn)
        except socket.error, (strError):
            print 'keepalive failed: %s' % (strError)
        sleep(seconds)
#thread = threading.Thread(target=keepalive, args=(conn, 60))
#thread.start()

print 'getting hostname...'
# Get the machine's hostname
sendMessage['userpass'] = md5userpass
sendMessage['payload'] = 'GET VAR sys.hostname'
try:
    print sendMessage.asString()
    myMcpClient.send(sendMessage, conn)
    recvMessage = myMcpClient.recv(conn)
    hostname = recvMessage['payload']
except socket.error, (strError):
    print 'failed to retrieve hostname: %s' % (strError)
    hostname = ''

# The main loop
while True:
    # Initialize the MCP messages with each iteration
    sendMessage.reset()
    recvMessage.reset()

    sendMessage['userpass'] = md5userpass

    # Reset the send and receive variables. Default is True.
    needRecv = True
    needSend = True

    #command = CLICommand()

    # Get cli command and turn it into an MCP message(s)
    #command.parse(raw_input('%s> ' % hostname))
    line = re.split('\s+', raw_input('%s> ' % hostname))
    lineLength = len(line)
    input = ''
    if lineLength > 0:
        # handle commands
        if line[0] == 'help' or line[0] == '?':
            print 'this will show help'
            needSend = False
        elif line[0] == 'exit' or line[0] == 'quit':
            sendMessage['type'] = 'EM'
            needRecv = False
        elif line[0] == 'reboot':
            input = 'REBOOT'
        elif line[0] == 'halt':
            input = 'HALT'
        elif line[0] == 'commit':
            input = 'COMMIT'
        elif line[0] == 'save':
            input = 'SAVE'
        elif line[0] == 'show':
            if lineLength > 1:
                if line[1] == 'net':
                    if lineLength > 2:
                        if line[2] == 'domain':
                            input = 'GET VAR net.domain'
                elif line[1] == 'sys':
                    if lineLength > 2:
                        if line[2] == 'hostname':
                            input = 'GET VAR sys.hostname'
                    else:
                        print 'not implemented yet'
                        needSend = False
                elif line[1] == 'date':
                    input = 'DATE'
                else:
                    print 'not implemented yet'
                    needSend = False
            else:
                print 'not implemented yet'
                needSend = False
        elif line[0] == 'set':
            if lineLength > 1:
                if line[1] == 'dns':
                    if lineLength > 2:
                        if line[2] == 'domain':
                            if lineLength > 3:
                                input = 'SET VAR net.domain ' % line[3]
        else:
            print 'help ? exit quit reboot halt commit save show set'
            needSend = False
               
        if input:
            sendMessage['payload'] = input

        if needSend:
            # Sending
            try:
                myMcpClient.send(sendMessage, conn)
            except socket.error, (strError):
                print 'send failed: %s' % (strError)
                break 

            # Receiving
            if needRecv:
                try:
                    recvMessage = myMcpClient.recv(conn)
                except socket.error, (strError):
                    print 'receive failed: %s' % (strError)
                    break

                # Handle the message we receive
                if recvMessage['type'] != 'EM':
                    print recvMessage['payload']
                else:
                    break
            else:
                break

myMcpClient.close(conn)

