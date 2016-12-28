from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        if subprocess.call(['lighttpd', '-f', '/usr/local/etc/lighttpd.conf']):
            retVal = False
        return(retVal)

    def stop(self):
        retVal = True
        f = open('/var/run/lighttpd.pid', 'r')
        pid = f.read()[:-1]
        f.close()
        if subprocess.call(['kill', '-INT', '%s']):
            retVal = False
        return(retVal)

    def restart(self):
        retVal = True
        self.stop()
        self.start()
        return(retVal)

    def stat(self):
        retVal = True
        return(retVal)

