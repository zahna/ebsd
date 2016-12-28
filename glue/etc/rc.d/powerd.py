from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        if not subprocess.call(['powerd', '-i', '99', '-r', '50', '-a', 'adaptive', '-n', 'adaptive']):
            retVal = False
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

