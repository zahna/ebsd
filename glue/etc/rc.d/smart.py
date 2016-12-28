from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        rc = subprocess.call(['/usr/local/sbin/smartd'])
        return(retVal)

    def stop(self):
        pass

    def restart(self):
        pass

    def stat(self):
        pass

