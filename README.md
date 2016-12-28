This is my personal, embedded BSD system; based on FreeBSD.

I will add to this README as I port over the docs from the wiki which used to house them.

Third party software is software that isn't found in the FreeBSD ports system. It has to be compiled from source tarballs and manually managed.
This is what is used in ebsd:
  * clog
    * needs the clog enabled syslogd
    * compilation of the custom syslogd requres ttymsg.c and .h from wall(1), found in /usr/src/usr.bin/wall
  * Python
    * netifaces - http://pypi.python.org/pypi/netifaces/0.3
    * py-smbpasswd - http://barryp.org/software/py-smbpasswd/
    * pyparsing - http://pyparsing.wikispaces.com/
    * pysnmp - http://pysnmp.sourceforge.net/
      * ASN.1 library for python - http://sourceforge.net/projects/pyasn1/


