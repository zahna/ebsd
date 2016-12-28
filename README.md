This is my personal, embedded BSD system; based on FreeBSD.

I will add to this README as I port over the docs from the wiki which used to house them.

API's

Class Config('<path_to_config>')

* getVar(string) - Get a config value held by a config key. Returns a string if successful. Returns an empty string if the config key doesn't exist.
* getVars(wildcard) - Get multiple config values by supplying a string that matches the beginning of a group of config keys or is a string with either regular or SQL wildcards (* or %). Returns a dictionary. Example: foo = config.getVars('fung.moo*')
* setVar(string, string) - Set the value of a config key. Returns True if successful, False if not.
* setVars(dict) - Set the values of multiple config keys contained in dictionary. Returns True if successful, False if not.
* delVar(string) - Delete the config key and value where key matches string. Returns True if successful, False if there are no key matches.
* delVars(list) - Delete a list of config keys. Returns True if successful, False if there are no key matches.
* commit() - Saves the configuration database back to disk. Returns True or False.


MCP - This module contains objects and information for communicating via MCP.

MCPMessage() - This object represents messages sent and received between MCPAgent()'s.
Member Variables:
* type - type of message
* payload - message payload
* length - length of message
* version - version of MCP used in the packet
Methods:
* parse(string) - Take a string and parse it and assign the MCPMessage instance's member variables. Useful for recv()'ing.
* asString() - Returns the MCPMessage instance as a string. Useful for send()'ing.
* reset() - Reset the values in the packet back to intial defaults.


MCPAgent() - This object is used for transmitting and receiving MCPMessage()'s.
Member Variables:
* listeners - List of listening sockets.
* msgEom - End of message character. ←- this is probably going away with the use of length to calculate end of message.
* recvBuf - size of recv'ing buffer
* recvTimeo - recv() timeout value
* sendTimeo - send() timeout value
* acceptTimeo - accept() timeout value
Methods:
* listen(family, type, addr) - Create and listen on a socket. Added to listeners member variable.
* connect(family, type, addr) - Create a socket and connect to a remote address.
* accept() - Accept a connection from a remote address(es). Returns a tuple of sockets.
* recv(sock) - Receive from a socket.
* send(sock) - Send out on a socket.
* close(sock) - Shutdown and close a socket.
* run(handler, extras) - Runs one iteration of listening for and handling connections, then handling extra functions. Extras should be passed in as a tuple.


System() - This is an object that supplies member functions to control the system operation, such as starting/stopping services, adding users and groups, etc
* svcStart(service_name)
* svcStop(service_name)
* svcStat(service_name)
* inetAtoi(addr) - Convert an IP address to a long int
* inetItoa(num) - Convert a long int into an IP address
* netmask(num) - Make a netmask of num bits
* invertNetmask(addr) - Invert the bits of a netmask into a Cisco like hostmask
* getIfInfo(net_device) - Get a dictionary containing the keys of: address, netmask, broadcast, network.
* createUser(username,gecos,password,samba_acct_flags,shell) - Create a user.
* genPasswdFiles()
* genGroupFiles()
* genSambaFiles()
* createUser() - Creates a user, then regenerates the account files.
* randStr() - Generate a string of random characters (samba compliant)
* getBootList() - Generate a list of services in the order in which they need to boot.


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


