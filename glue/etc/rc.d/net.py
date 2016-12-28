from BaseService import BaseService
import subprocess
import netifaces

class Service(BaseService):
    def start(self):
        retVal = True
        # Write out resolv.conf
        f = open('/etc/resolv.conf', 'w')
        f.write('search %s\n' % self.config.getVar('net.domain'))
        for nameserver in self.config.getVar('net.nameserver4'):
            f.write('nameserver %s\n' % (nameserver))
        f.close()

        # Start loopback interface. It's always there.
        subprocess.call(['/sbin/ifconfig', 'lo0', '127.0.0.1', 'netmask', '255.0.0.0'])

        physIfaces = netifaces.interfaces()
        # Removing lo0 because we consider it hardwired up.
        physIfaces.remove('lo0')

        for physIface in physIfaces:
            if not self.appliance.netIfUp(physIface):
                retVal = False
        return(retVal)

    def stop(self):
        retVal = True
        # Shutdown lan interface
        physIfaces = netifaces.interfaces()
        # Removing lo0 because we consider it hardwired up.
        physIfaces.remove('lo0')

        for physIface in physIfaces:
            if not self.appliance.netIfDown(physIface):
                retVal = False
        return(retVal)


    def restart(self):
        retVal = True
        return(retVal)

    def stat(self):
        retVal = True
        return(retVal)

