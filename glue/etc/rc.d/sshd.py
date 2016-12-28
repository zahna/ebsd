from BaseService import BaseService
import subprocess

class Service(BaseService):
    def start(self):
        retVal = True
        if not os.path.exists('/etc/ssh'):
           os.mkdir('/etc/ssh')

        # Write the basic ssh config files
        f = open('/etc/ssh/ssh_config', 'w')
        f.write('# Host *\n')
        f.close()
        f = open('/etc/ssh/sshd_config', 'w')
        f.write('PermitRootLogin yes\n')
        f.close()

        # Generate rsa1 keys, if needed
        privkey = self.config.getVar('svc.sshd.rsa1.privkey')
        if privkey == '':
            syslog.syslog(syslog.LOG_NOTICE, 'svcStart(): %s: Generating RSA1 keys' % (service))
            subprocess.call(['ssh-keygen', '-t', 'rsa1', '-f', '/tmp/temp_rsa1_key', '-N', ''])

            f = open('/tmp/temp_rsa1_key', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.rsa1.privkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_rsa1_key')

            f = open('/tmp/temp_rsa1_key.pub', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.rsa1.pubkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_rsa1_key.pub')

            # Set that we need to commit to CF
            needcommit = True

        # Write out the rsa1 keys
        privkey = self.config.getVar('svc.sshd.rsa1.privkey')
        f = open('/etc/ssh/ssh_host_key', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

        pubkey = self.config.getVar('svc.sshd.rsa1.pubkey')
        f = open('/etc/ssh/ssh_host_key.pub', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

# Generate rsa2 keys, if needed
        privkey = self.config.getVar('svc.sshd.rsa2.privkey')
        if privkey == '':
            syslog.syslog(syslog.LOG_NOTICE, 'svcStart(): %s: Generating RSA2 keys' % (service))
            subprocess.call(['ssh-keygen', '-t', 'rsa', '-f', '/tmp/temp_rsa2_key', '-N', ''])

            f = open('/tmp/temp_rsa2_key', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.rsa2.privkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_rsa2_key')

            f = open('/tmp/temp_rsa2_key.pub', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.rsa2.pubkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_rsa2_key.pub')

            # Set that we need to commit to CF
            needcommit = True

        # Write out the rsa2 keys
        privkey = self.config.getVar('svc.sshd.rsa2.privkey')
        f = open('/etc/ssh/ssh_host_rsa_key', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

        pubkey = self.config.getVar('svc.sshd.rsa2.pubkey')
        f = open('/etc/ssh/ssh_host_rsa_key.pub', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

        # Generate dsa keys, if needed
        privkey = self.config.getVar('svc.sshd.dsa.privkey')
        if privkey == '':
            syslog.syslog(syslog.LOG_NOTICE, 'svcStart(): %s: Generating DSA keys' % (service))
            subprocess.call(['ssh-keygen', '-t', 'dsa', '-f', '/tmp/temp_dsa_key', '-N', ''])

            f = open('/tmp/temp_dsa_key', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.dsa.privkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_dsa_key')

            f = open('/tmp/temp_dsa_key.pub', 'r')
            contents = f.read()
            f.close()
            self.config.setVar('svc.sshd.dsa.pubkey', base64.b64encode(contents)) 
            os.unlink('/tmp/temp_dsa_key.pub')

            # Set that we need to commit to CF
            needcommit = True

        # Write out the dsa keys
        privkey = self.config.getVar('svc.sshd.dsa.privkey')
        f = open('/etc/ssh/ssh_host_dsa_key', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

        pubkey = self.config.getVar('svc.sshd.dsa.pubkey')
        f = open('/etc/ssh/ssh_host_dsa_key.pub', 'w')
        f.write(base64.b64decode(privkey))
        f.close()

        # Ensure strict permissions on ssh files
        subprocess.call(['chmod 600 /etc/ssh/*'], shell=True)

        # Start SSHd
        subprocess.call(['/usr/sbin/sshd'])
        return(retVal)

    def stop(self):
        pass

    def restart(self):
        pass

    def stat(self):
        pass

