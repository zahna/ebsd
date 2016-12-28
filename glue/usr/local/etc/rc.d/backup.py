from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        f = open('/dev/null', 'w')
        f.write('')
        f.close()
        rc = subprocess.call(['false'])
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

