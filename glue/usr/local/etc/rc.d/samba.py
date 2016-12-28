from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        # Create /var/log/samba
        if not os.path.exists('/var/log/samba'):
        os.mkdir('/var/log/samba')

        # Create smb.conf
        smbconf = self.config.getVars('svc.samba.smbconf')
        # Get a list of unique section names
        sectionlist = []
        for key in smbconf.keys():
            section = key.split('.')[3]
            if not section in sectionlist:
                sectionlist.append(section)

        # Write smb.conf
        f = open('/usr/local/etc/samba/smb.conf', 'w')
        for section in sectionlist:
            f.write('['+section+']\n')
            sections = self.config.getVars('svc.samba.smbconf.'+section)
            for key, val in sections.iteritems():
                f.write('%s=%s\n' % (key.split('.')[-1], val))
        f.close()
                    
        rc = subprocess.call(['smbd'])
        rc = subprocess.call(['nmbd'])
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

