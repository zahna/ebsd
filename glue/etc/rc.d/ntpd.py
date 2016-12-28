from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        f = open('/etc/ntp.conf', 'w')
        f.write('\nrestrict default nomodify notrap noquery\nrestrict 127.0.0.1\npidfile   /var/run/ntpd.pid\ndriftfile   /var/db/ntp.drift\ntos   minsane 2\n')
        for server in self.config.getVar('sys.ntpd.servers'):
            f.write('server %s\n' % (server))
        f.close()
        if not subprocess.call(['ntpd', '-c', '/etc/ntp.conf', '-p', '/var/run/ntpd.pid', '-f', '/var/db/ntpd.drift', '-x', '-g']):
            retVal = False
        return(retVal)

    def stop(self):
        pass

    def restart(self):
        pass

    def stat(self):
        pass

