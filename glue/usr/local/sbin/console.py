#!/usr/bin/env python

import subprocess
import netifaces
import networking
import config, appliance 
from menu import Menu
from menu import confirm

myConfig = config.Config()
myAppliance = appliance.Appliance(myConfig)

osName = myConfig.getVar('sys.osname')

def reboot():
    if confirm():
        myAppliance.shutdown('reboot')

def halt():
    if confirm():
        myAppliance.shutdown('halt')

def dumpConfig():
    print(myConfig.dump())
    return True

def saveConfig():
    if confirm('Save configuration database to flash memory?'):
        if not myAppliance.cfgSave():
            return False
    return True

def runShell():
    subprocess.call(['/bin/sh']) 

def changePassword(user):
    import getpass
    # TODO: should we confirm the user's password here before proceeding?
    password1 = getpass.getpass('New %s password: ' % user)
    password2 = getpass.getpass('...one more time: ')
    if password1 == password2:
        myAppliance.authSetMd5(user, password1)
        myAppliance.authGenPasswdFiles()
    else:
        print 'Passwords do not match. Cancelling.'

def pingTest():
    host = raw_input('Host to ping: ')
    subprocess.call(['/sbin/ping', '-c', '3', host])

def selectIf():
    interfaces = netifaces.interfaces()
    interfaces.remove('lo0')
    print 'Which interface?'
    print ', '.join(interfaces)
    interface = raw_input('> ')
    if interface in interfaces:
        configIf(interface) 
        return True
    else:
        print '"%s" is not a valid interface.' % interface
        return False

def configIf(interface):
    '''Configure a network interface
    '''
    if myConfig.getVar('net.%s.enable' % interface) == True:
        # Display existing config, if it exists
        print 'Interface: %s' % interface
        proto = myConfig.getVar('net.%s.proto' % interface)
        if proto == 'dhcp':
            print 'Protocol: %s' % proto
        else:
            print 'Address: %s' % myConfig.getVar('net.%s.addr4' % interface)
            print 'Netmask: %s' % myConfig.getVar('net.%s.netmask4' % interface)

    # This is up here so we can skip the rest if we disable the interface
    if not confirm('Enable interface %s' % interface):
        myConfig.setVar('net.%s.enable' % interface, False)
        print 'Interface %s disabled' % interface
        return True

    # Prompt and enter the network information
    addr4 = raw_input('Enter IPv4 address or "dhcp": ').lower()

    if addr4 != 'dhcp': 
        if not network.isAddr4(addr4):
            print 'IPv4 address is malformed. Cancelling configuration.'
            return False
        netmask4 = raw_input('Enter netmask: ')
        if not network.isAddr4(netmask4):
            print 'Netmask is malformed. Cancelling configuration.'
            return False

    # TODO: write facilities for entering IPv6 information here
    # addr6 = raw_input('Enter IPv6 address or hit Enter to cancel: ')

    # Confirm the config variables
    print 'Interface: %s' % interface
    if addr4 == 'dhcp':
        print 'Protocol: %s' % addr4
    else:
        print 'IPv4 Address: %s' % addr4
        print 'Netmask: %s' % netmask4
        #print 'IPv6 Address: %s' % addr4

    if confirm('Are these settings correct? [y/N]'):
        myConfig.setVar('net.%s.enable' % interface, True)
        if addr4 == 'dhcp':
            myConfig.setVar('net.%s.proto' % interface, addr4)
        else:
            myConfig.setVar('net.%s.proto' % interface, 'static')
            myConfig.setVar('net.%s.addr4' % interface, addr4)
            myConfig.setVar('net.%s.netmask4' % interface, netmask4)
    else:
        print 'Configuration of %s canceled.' % interface

def configGw():
    '''Configure the default gateway
    '''
    print 'Current Gateway: %s' % (myConfig.getVar('net.gateway4'))
    gateway4 = raw_input('Enter IP Address of gateway or hit Enter to cancel: ')
    if network.isAddr4(gateway4) :
        if confirm('Is "%s" correct? [y/N]' % gateway4):
            myAppliance.netSetGw(gateway4)
            return True
    else:
        print 'Invalid address specified. Cancelling.'
    return False

def configDns():
    '''Configure the DNS settings
    '''
    domain = myConfig.getVar('net.domain')
    nameserver4 = myConfig.getVar('nameserver4')
    print 'Domain:      %s' % (domain)
    print 'Nameservers: %s' % (nameserver4)
    domain = raw_input('Enter domain: ')
    nameserver4 = raw_input('Enter nameservers, seperated by spaces: ')
    nameserver4 = nameserver4.split(' ')
    if confirm('Are these settings correct?'):
        myConfig.setVar('net.domain', domain)
        myConfig.setVar('net.nameserver4', nameserver4)
        #myAppliance.netSetDns(domain, nameserver4.split(' '))
        print 'Settings will not take effect until reboot.'

# Menus section
def cmdLine():
    f = open('/usr/local/sbin/cmdline.py')
    code = f.read()
    f.close()
    exec compile(code, '/dev/null', 'exec')

def confMenu():
    items = {'1':'Network', '2':'Users'}
    actions = {'1':networkMenu, '2':usersMenu}
    menu = Menu('Configuration Menu', items, actions)
    menu.run()

def networkMenu():
    items = {'1':'Configure Network Interface', '2':'Configure gateway', '3':'Configure DNS'}
    actions = {'1':selectIf, '2':configGw, '3':configDns}
    menu = Menu('Network Menu', items, actions)
    menu.run()

def usersMenu():
    items = {'1':'Add a user', '2':'Modify a user', '3':'Delete a user', '4':'Change admin password', '5':'Change root password'}
    actions = {'1':None, '2':None, '3':None, '4':(changePassword, 'admin'), '5':(changePassword, 'root')}
    menu = Menu('Users Menu', items, actions)
    menu.run()

def utilsMenu():
    items = {'1':'ping test', '2':'spawn a shell', '3':'Dump the config database', '4':'Raw config manager', '5':'Save config database to flash memory'}
    actions = {'1':pingTest, '2':runShell, '3':dumpConfig, '4':None, '5':saveConfig}
    menu = Menu('Utilities Menu', items, actions)
    menu.run()

def main():
    if myConfig.getVar('sys.firstrun'):
        # TODO: Create a first run wizard
        pass
    else:
        # Display the main menu
        items = {'1':'Configuration Menu', '2':'Command Line', '3':'Utilities', '4':'Reboot', '5':'Shutdown'}
        actions = {'1':confMenu, '2':cmdLine, '3':utilsMenu, '4':reboot, '5':halt}
        menu = Menu('%s Main Menu' % osName, items, actions)
        menu.run()

        if myConfig.needCommit:
            if confirm('Changes on configuration were made.  Save to NVRAM?'):
                myConfig.save()

    exit(0)

main()
