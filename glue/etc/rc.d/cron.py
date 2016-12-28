from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        rc = subprocess.call(['cron', '-s'])
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

