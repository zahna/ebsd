from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        if self.config.getVar('net.lan.proto') == 'dhcp':
            syslog.syslog(syslog.LOG_ERR, 'svcStart(): Can not start %s when lan interface is configured via DHCP' % (service))
        else:
            lanIf = self.config.getVar('net.lan.device')
            lanIfInfo = self.getifinfo(lanIf)
            f = open('/usr/local/etc/dhcpd.conf', 'w')
            # Write the base part of the config file
            f.write('authoritative;\nddns-update-style none;\nlog-facility local7;')
            # Write the customized part
            f.write('\nsubnet %s netmask %s {\n\trange %s %s;\n\toption domain-name "%s";' % (lanIfInfo['network'], lanIfInfo['netmask'], self.config.getVar('svc.dhcpd.start'), self.config.getVar('svc.dhcpd.end'), self.config.getVar('net.domain')))
            f.write('\toption domain-name-servers %s;' % (' '.join(self.config.getVar('net.nameserver4'))))
            f.write('\toption routers %s;\n\toption broadcast-address %s;\n\tdefault-lease-time %s;\n\tmax-lease-time %s;\n}' % (self.config.getVar('net.gateway4'), lanIfInfo['broadcast'], self.config.getVar('svc.dhcpd.lease.default'), self.config.getVar('svc.dhcpd.lease.max')))
            f.close()
            # Create the dhcpd.leases file
            open('/var/db/dhcpd.leases','w').close()
            # Start dhcpd
            subprocess.call(['dhcpd', lanIf])
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

