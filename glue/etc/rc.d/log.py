from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        # generate circular logfiles
        #subprocess.call(['/usr/local/sbin/clog -i -s 1048576 /var/log/messages'], shell=True)
        #subprocess.call(['chmod', '0640', '/var/log/messages'])

        # What do we write to the logs?
        whatToWrite = '*.notice;authpriv.none;kern.debug;lpr.info;mail.crit;news.err'

        # generate syslog.conf
        f = open('/etc/syslog.conf', 'w')
        f.write('%s /var/log/messages\n' % whatToWrite)

        server = self.config.getVar('sys.log.server')
        if server:
            f.write('%s @%s\n' % (whatToWrite, server))

        f.close()
        rc = subprocess.call(['syslogd', '-C', '-cc', '-vv', '-s'])
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

