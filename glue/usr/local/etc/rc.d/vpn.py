from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        f = open('/usr/local/etc/openvpn.conf', 'w')
        f.write('dev tun\n')
        f.write('ifconfig %s\n' % (self.config.getVar('net.vpn.ifconfig')))
        f.write('up /usr/local/etc/vpnroute.up\nsecret /usr/local/etc/openvpn.secrets\ncomp-lzo\nping 30 120')
        f.close()
        rc = subprocess.call(['openvpn', '--daemon', '--config', '/usr/local/etc/openvpn.conf', '--writepid', '/var/run/openvpn.pid'])
        return(retVal)

    def stop(self):
        retVal = True
        return(retVal)

    def restart(self):
        retVal = True
        return(retVal)

    def stat(self):
        retVal = True
        return(retVal)

