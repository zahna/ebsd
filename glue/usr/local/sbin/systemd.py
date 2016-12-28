#!/usr/bin/env python

import MCP
import config
import os
import sys
import socket # for a few socket variables
import select
import signal
import syslog
import threading
from time import sleep

# Handle caught signals
def handleSignal(sigNum, frame):
    if sigNum == 2:
        syslog.syslog(syslog.LOG_NOTICE, 'Caught signal %s.  Closing up shop...' % sigNum)
        # TODO: shutdown all running threads here
        for sock in myMcpServer.listeners:
            myMcpServer.close(sock)
        if os.path.exists(unixSock):
            os.unlink(unixSock)
        exit(0)

signal.signal(signal.SIGINT, handleSignal)

syslog.syslog(syslog.LOG_NOTICE, 'starting systemd')

# Instantiate the MCP Agent
myMcpServer = MCP.MCPAgent()
# Set a few variables of the agent
myMcpServer.recvTimeo = 600
myMcpServer.recvBuf = 16 
myMcpServer.acceptTimeo = -1

unixSock = '/var/run/systemd.sock'
inetSock = ('', 1025)

pidFile = '/var/run/systemd.pid'

# We can't listen on a pre-existing socket.
# Make sure we aren't going to run a duplicate copy.
if os.path.exists(unixSock):
    if os.path.exists(pidFile):
        try:
            f = open(pidFile)
            os.kill(int(f.read()), 0)
            f.close()
        except:
            os.unlink(unixSock)
        else:
            print 'Systemd already running. Exiting.'
            exit(-1)
    else:
        os.unlink(unixSock)

f = open(pidFile, 'w')
f.write(str(os.getpid()))
f.close()


# Add sockets to listen on
try:
    myMcpServer.listen(socket.AF_UNIX, socket.SOCK_STREAM, unixSock) 
    myMcpServer.listen(socket.AF_INET, socket.SOCK_STREAM, inetSock) 
except socket.error, (strerror):
    print strerror
    exit(-1)

syslog.syslog(syslog.LOG_NOTICE, 'ready to accept connections')

# This is the connection handling callback function.  It handles connections
# from MCP Agents acting as clients.
def handleConn(sock, addr=None):
    # Instantiate the appliance config
    configdb = config.Config()

    # Instantiate our MCP messages for each direction
    recvMsg = MCP.MCPMessage()
    sendMsg = MCP.MCPMessage()

    sessUser = ''
    sessHash = ''

    while True:
        # Set whether we need to send after processing a recv().
        needSend = True
        sendMsg['type'] = 'ACK'

        # Receive data
        try:
            recvMsg = myMcpServer.recv(sock)
            syslog.syslog(syslog.LOG_NOTICE, 'received "%s"' % recvMsg.asString())
        except:
            syslog.syslog(syslog.LOG_NOTICE, 'receive error: %s' % sys.exc_info()[1])
            break

        # Figure out if we're authenticated or if we can be.  It's kind of necessary. :)
        if recvMsg['userpass'] != sessHash:
            userPasses = configdb.getVars('user.*.md5userpass')
            for key, val in userPasses.iteritems():
                if recvMsg['userpass'] == val:
                    sessUser = key.split('.')[1]
                    sessHash = val
                    syslog.syslog(syslog.LOG_NOTICE, 'user %s logged in' % sessUser)
                    break

        # If the user is authenticated, communicate!
        if recvMsg['userpass'] == sessHash:
            # OK. We have some data. Decide what to do based on message type.
            if recvMsg['type'] == 'SYN':
                syslog.syslog(syslog.LOG_NOTICE, 'received SYN')
                syslog.syslog(syslog.LOG_NOTICE, 'sending ACK')
            elif recvMsg['type'] == 'ENQ':
                payload = recvMsg['payload'].split(' ')
                if payload[0] == 'DATE':
                    fh = os.popen('date')
                    sendMsg['payload'] = fh.read()[:-1]
                elif payload[0] == 'EXEC':
                    fh = os.popen(payload[1])
                    sendMsg['payload'] = fh.read()
                elif payload[0] == 'GET':
                    if payload[1] == 'VAR':
                        sendMsg['payload'] = configdb.getVar(payload[2])
                    else:
                        sendMsg['type'] = 'NAK'
                        sendMsg['payload'] = 'Undefined command: %s' % (payload[1])
                elif payload[0] == 'HALT':
                    sendMsg['payload'] = '%s not implemented in systemd yet' % payload[0]
                elif payload[0] == 'REBOOT':
                    sendMsg['payload'] = '%s not implemented in systemd yet' % payload[0]
                elif payload[0] == 'SET':
                    if payload[1] == 'VAR':
                        sendMsg['payload'] = configdb.setVar(payload[2])
                elif payload[0] == 'STAT':
                    sendMsg['payload'] = ''
                    for i in ['uptime', 'swapinfo', 'vmstat']:
                        cmdFH= os.popen(i)
                        sendMsg['payload'] += '%s' % (cmdFH.read(), '\n')
                        cmdFH.close()
                else:
                    sendMsg['type'] = 'NAK'
                    sendMsg['payload'] = 'Undefined command: %s' % (payload[0])
            elif recvMsg['type'] == 'EM':
                syslog.syslog(syslog.LOG_NOTICE, 'received EM')
                break
            else:
                syslog.syslog(syslog.LOG_NOTICE, 'received invalid message type %s' % (recvMsg.type))
                sendMsg['type'] = 'NAK'
                sendMsg['payload'] = 'Invalid message type: %s' % (recvMsg.type)
        else:
            sendMsg['type'] = 'NAK'
            sendMsg['payload'] = 'Not authenticated.'

        # Do sending here, if necessary.
        if needSend:
            try:
                syslog.syslog(syslog.LOG_NOTICE, 'sending "%s"' % sendMsg.asString())
                myMcpServer.send(sendMsg, sock)
            except socket.error, (strerror):
                syslog.syslog(syslog.LOG_NOTICE, 'send failure: %s' % (strerror))
                break 

        # Reset the send message for re-use 
        sendMsg.reset()

    # If we got here, we're ready to close the connection
    myMcpServer.close(sock)
    return True

def watchdog(programs=(), delay=5.0):
    '''The watchdog function ensures other programs are always running.
    '''
    while True:
        for program in programs:
            pass
            #syslog.syslog(syslog.LOG_NOTICE, 'ensuring that %s is still running' % (program))
        sleep(delay)

# Start initial threads
thread = threading.Thread(target=watchdog, args=(('ntpd',),))
thread.start()

# The main loop
while True:
    #syslog.syslog(syslog.LOG_NOTICE, 'waiting for connections')
    conns = myMcpServer.accept()
    for conn in conns:
        thread = threading.Thread(target=handleConn, args=(conn[0],))
        thread.start()

