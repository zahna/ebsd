#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import web, page
import config, appliance
import netifaces
import os
import random
import subprocess
import syslog
import time
from cgi import escape

# Output debugging to the browser 
web.webapi.internalerror = web.debugerror

# Mapping urls to classes
urls = (
        '/dumpconfig(.*)', 'DumpConfig',
        '/login(.*)', 'Login',
        '/logout(.*)', 'Logout',
        '/logs(.*)', 'Logs',
        '/network(.*)', 'Network',
        '/shutdown(.*)', 'Shutdown',
        '/status(.*)', 'Status',
        '/system(.*)', 'System',
        '(.*)', 'Index',
       )

# Client object mapping information as a Storage object from web.py
clientMap = web.Storage()

class BaseResource(object):
    '''The BaseResource class is the base for the other resources ("pages").
       It's sort of the "template" for the other pages.
    '''
    def __init__(self):
        self.config = config.Config()
        self.appliance = appliance.Appliance(self.config)
        self.sessionTimeo = 300
        
    def _top(self):
        output = u'<div id="top">'
        output += u'<a href="/">WebGui Configuration</a>'
        output += u'<div id="right-align">%s, load averages: %s</div>' % (time.strftime("%Y/%m/%d %H:%M"), appliance.sysctl('vm.loadavg')[2:-3])
        # End the menu div tag and return the output
        output += u'</div>'
        return output

    def _navMenu(self, clientId=None):
        output = u'<div id="navMenu">'
        output += u'<a id="navMenuHead" href="/">Home</a><br>'
        # Output the default menu items
        output += u'<a href="/status">Status</a><br>'
        output += u'<a href="/system">System</a><br>'
        output += u'<a href="/network">Network</a><br>'
        output += u'<a href="/logs/messages">Logs</a><br>'
        output += u'<a href="/dumpconfig">Dump Config</a><br>'
        output += u'<a id="menuHead" href="/logs/messages">Services</a><br>'

        # Include all add-on module menu entries


        # Finish with the log out option
        if clientMap.has_key(clientId):
            output += u'<p><a href="/logout">Log out</a></p>'
        else:
            output += u'<p><a href="/login">Log in</a></p>'
        output += u'<a href="/shutdown">Shutdown</a>'
        # End the menu div tag and return the output
        output += u'</div>'
        return output

    def _ensureClientId(self, cookies):
        '''This makes sure we get the clientId and compare it to the entry
        in the clientMap.  This is necessary for keeping people logged in.
        '''
        clientId = cookies.get('clientId')
        if clientMap.has_key(clientId):
            web.setcookie('clientId', clientId, self.sessionTimeo)
            clientMap[clientId]['date'] = int(time.time())
            return clientId
        return False

    def GET(self, path=None):
        'override this method'
        pass

    def POST(self, path=None):
        'override this method'
        pass


# Resource classes.  These compose the "pages" which compose the webgui.
class DumpConfig(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Make the page
        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Dump Configuration')
        myPage.setCSS(u'/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')
        myPage.setBody(u'How do you want to dump the configuration database?<br>')
        myPage.setBody(u'<form method="post">')
        myPage.setBody(u'<select name="dumpMethod">')
        myPage.setBody(u'<option value="display">Display config database in browser</option>')
        myPage.setBody(u'<option value="download">Download a dump file of config database</option>')
        myPage.setBody(u'</select>')
        myPage.setBody('<input type="submit" value="Go >">')
        myPage.setBody('</form>')
        myPage.setBody('</div>')
        web.output(myPage.output())

    def POST(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        input = web.input(_method='post')
        myPage = page.Page()
        myPage.setTitle(u'Appliance Webgui - Dump Configuration')

        if input['dumpMethod'] == 'display':
            web.header("Content-Type", myPage.getContentType())
            myPage.setCSS(u'/static/styles.css')
            myPage.setBody(self._top())
            myPage.setBody(self._navMenu(clientId))
            myPage.setBody(u'<div id="main">')
            myPage.setBody(self.config.dump().replace('\n', '<br>'))
            myPage.setBody('</div>')
        elif input['dumpMethod'] == 'download':
            myPage.setContentType('application/octet-stream')
            web.header("Content-Type", myPage.getContentType())

        web.output(myPage.output())


class Login(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        # Handle cookies
        cookies = web.cookies()
        clientId = cookies.get('clientId')

        # Make the page
        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Login')
        myPage.setCSS(u'/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(u'<div id="login">')

        if clientMap.has_key(clientId):
            myPage.setBody(u'You are already logged in with ID %s.<br>' % clientId)
            myPage.setBody(u'Do you want to <a href="/logout">log out</a>?<br>')
            myPage.setBody(u'Do you want to <a href="javascript:history.back()">go back</a>?')
        else:
            myPage.setBody(u'<form method="post">')
            myPage.setBody(u'Username: <input type="text" name="username"><br>')
            myPage.setBody(u'Password: <input type="password" name="password"><br>')
            myPage.setBody(u'<input type="submit" value="Submit">')
            myPage.setBody(u'</form>')

        myPage.setBody(u'</div>')
        web.output(myPage.output())

    def POST(self, path):
        # Handle cookies
        cookies = web.cookies()
        clientId = cookies.get('clientId')
        if not clientId:
            clientId = web.to36(random.randint(1,4294967295))
            web.setcookie('clientId', clientId, self.sessionTimeo)
        clientMap[clientId] = {}
        clientMap[clientId]['date'] = int(time.time())

        myPage = page.Page()
        myPage.setTitle(u'Appliance Webgui - Login')
        myPage.setCSS('/static/styles.css')

        myPage.setBody(self._top())
        myPage.setBody(u'<div id="login">')
        input = web.input(_method='post')
        myPage.setBody(u'Username: %s<br>' % input.username)
        myPage.setBody(u'Password: %s<br>' % input.password)
        myPage.setBody(u'<a href="/">Go to the main page</a>')

        myPage.setBody(u'</div>')

        web.output(myPage.output())


class Logout(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = cookies.get('clientId')
        if clientId:
            web.setcookie('clientId', None, -1)
            try:
                clientMap.pop('clientId')
            except KeyError:
                pass
        web.seeother('/login')

    def POST(self, path):
        pass


class Logs(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, logfile):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        allowed = ('/messages', '/access')

        myPage = page.Page()
        web.header('Content-Type', myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui')
        myPage.setCSS(u'/static/styles.css')
        if logfile in allowed:
            myPage.setBody(self._top())
            myPage.setBody(self._navMenu(clientId))
            myPage.setBody(u'<div id="main">')
            myPage.setBody(u'<div id="logtext">')
            if logfile == 'access':
                logfile = 'lighttpd.access.log'
            proc = subprocess.Popen(['cat', '/var/log/%s' % logfile], 
                                shell=False, stdin=None,
                                stdout=subprocess.PIPE, stderr=None)
            logOutput = escape(proc.communicate()[0])
            myPage.setBody(logOutput.replace('\n', '<br>'))
            myPage.setBody(u'</div>') 
            myPage.setBody(u'</div>')
            web.output(myPage.output())
        else:
            web.notfound()

    def POST(self):
        pass


class Index(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Build the page
        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Main')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')

        myPage.setBody(u'<p>variable "path" equals: %s</p>' % path)
        myPage.setBody('clientId: %s' % clientId)

        myPage.setBody(u'</div>')
        web.output(myPage.output())

    def POST(self):
        pass


class Network(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Build the page
        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Network')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')

        myPage.setBody(u'<p>This will eventually be the networking page.</p>')
        myPage.setBody('clientId: %s' % clientId)

        myPage.setBody(u'</div>')
        web.output(myPage.output())

    def POST(self, path):
        pass


class Shutdown(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Shutdown')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')

        # Build the page
        myPage.setBody(u'<form method="post">')
        myPage.setBody(u'<select name="downMethod">')
        myPage.setBody(u'<option value="reboot" selected>Reboot</option>')
        myPage.setBody(u'<option value="halt">Shutdown</option>')
        myPage.setBody(u'</select> the appliance.')
        myPage.setBody(u' <input type="submit" value="Go >">')
        myPage.setBody(u'</form>')
        myPage.setBody('clientId: %s' % clientId)
        myPage.setBody(u'</div>')
        web.output(myPage.output())

    def POST(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Collect POST data
        input = web.input(_method='post')

        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Shutdown')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')

        # Do stuff based on POST data
        if input['downMethod'] == 'reboot' or input['downMethod'] == 'halt':
            myPage.setHead(u'<meta http-equiv="refresh" content="70;url=/">')
            myPage.setBody(u'Performing action %s. Please wait.' % input['downMethod'])
            web.background(self.appliance.shutdown(input['downMethod']))
        else:
            myPage.setHead(u'<meta http-equiv="refresh" content="5;url=/">')
            myPage.setBody(u'downMethod "%s" is not valid. Redirecting to front page.' % input['downMethod'])
            syslog.syslog(syslog.LOG_ERR, 'invalid shutdown option "%s" passed to web gui' % input['downMethod'])
        myPage.setBody(u'</div>')
        web.output(myPage.output())


class Static(object):
    '''The static class is for serving static files, if we ever want to do that from
    inside webgui.py instead of through lighttpd.
    '''
    def GET(self, name):
        # Deduce the name & type of the file
        ext = name.split('.')[-1]
        contentType = {'png':'image/png',
                 'jpg':'image/jpeg',
                 'gif':'image/gif',
                 'ico':'image/gif',
                 'css':'text/css'}

        # Serve it if we got it!
        if os.path.exists("static") and name in os.listdir("static"):
            web.header(u'Content-Type', contentType[ext])
            web.output(open('static/%s' % name, 'rb').read())
        else:
            web.notfound()
        

class Status(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Build the page
        myPage = page.Page()
        web.header("Content-Type", myPage.getContentType())
        myPage.setTitle(u'Appliance Webgui - Status')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')
        myPage.setBody(u'<p>Appliance Status</p>')
        myPage.setBody(u'<p>Hostname: %s.%s</p>' % (self.config.getVar('sys.hostname'), self.config.getVar('net.domain')))
        myPage.setBody(u'<p>Time zone: %s</p>' % self.config.getVar('sys.tz'))
        myPage.setBody(u'<p>Virtual Memory: %s</p>' % escape(appliance.sysctl('vm.vmtotal')).replace('\n', '<br>'))

        myPage.setBody('clientId: %s' % clientId)
        myPage.setBody(u'</div>')
        web.output(myPage.output())

    def POST(self, path):
        pass

class System(BaseResource):
    def __init__(self):
        BaseResource.__init__(self)

    def GET(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Build the page
        myPage = page.Page()
        web.header('Content-Type', myPage.getContentType())
        myPage.setTitle('Appliance Webgui - System')
        myPage.setCSS('/static/styles.css')
        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody(u'<div id="main">')
        myPage.setBody(u'<p>System Preferences</p>')
        myPage.setBody(u'<form method="post">')
        # Passwords
        myPage.setBody(u'Passwords<br>')
        myPage.setBody(u'Reset admin password: <input type="password" name="adminPassword1"><br>')
        myPage.setBody(u'Confirm admin password: <input type="password" name="adminPassword2"><br>')
        myPage.setBody(u'Reset root password: <input type="password" name="rootPassword1"><br>')
        myPage.setBody(u'Confirm root password: <input type="password" name="rootPassword2">')
        myPage.setBody(u'<hr>')
        # Networking
        myPage.setBody(u'Networking<br>')
        myPage.setBody(u'IPv4 Gateway: <input type="text" name="net.gateway" value="%s"><br>' % self.config.getVar('net.gateway4'))
        myPage.setBody(u'IPv4 Nameserver: <input type="text" name="net.nameserver4" value="%s"><br>' % self.config.getVar('net.nameserver4'))
        for iface in netifaces.interfaces():
            myPage.setBody('%s<br>' % iface)
            addresses = netifaces.ifaddresses(iface)
            myPage.setBody('%s<br>' % addresses[netifaces.AF_LINK][0]['addr'])
            myPage.setBody('%s<br>' % addresses[netifaces.AF_INET][0]['addr'])
        myPage.setBody(u'<hr>')
        # Syslog
        myPage.setBody(u'Syslog<br>')
        if self.config.getVar('svc.log.enable'):
            myPage.setBody(u'Enabled<input type="radio" name="svc.log.enable" value="True" checked="checked">')
            myPage.setBody(u'Disabled<input type="radio" name="svc.log.enable" value="False">')
        else:
            myPage.setBody(u'Enabled<input type="radio" name="svc.log.enable" value="True">')
            myPage.setBody(u'Disabled<input type="radio" name="svc.log.enable" value="False" checked="checked">')
        myPage.setBody(u'<br>')
        myPage.setBody(u'Server (optional): <input type="text" name="sys.log.server" value="%s">' % self.config.getVar('sys.log.server'))
        myPage.setBody(u'<hr>')
        # Language
        currLang = self.config.getVar('sys.lang')
        langs = {'en_US':u'english',
                 'es_ES':u'espa\xf1ol',
                 'de_DE':u'deutsch',
                 'fr_FR':u'fran\xe7ais',
                 'jp_JP':u'japanese',
                 'zh_CN':u'chinese'}
        myPage.setBody(u'Language: <select name="sys.lang">')
        for key, val in langs.iteritems():
            if key == currLang:
                myPage.setBody(u'<option selected value="%s">%s</option>' % (key, val))
            else:
                myPage.setBody(u'<option value="%s">%s</option>' % (key, val))
        myPage.setBody('</select>')
        myPage.setBody('<br>')
        myPage.setBody('<input type="submit" value="Save Options">')
        myPage.setBody('</form>')


        myPage.setBody('clientId: %s' % clientId)
        myPage.setBody('</div>')
        web.output(myPage.output())

    def POST(self, path):
        cookies = web.cookies()
        clientId = self._ensureClientId(cookies)
        if not clientId:
            web.seeother('/login')
            return False

        # Collect POST data
        input = web.input(_method='post')

        # Do stuff based on POST data
        for key, val in input.iteritems():
            self.config.setVar(key, val)

        # Create page
        myPage = page.Page()
        myPage.setTitle('Appliance Webgui - Login')
        myPage.setCSS('/static/styles.css')

        myPage.setBody(self._top())
        myPage.setBody(self._navMenu(clientId))
        myPage.setBody('<div id="main">')
        if self.config.needCommit:
            myPage.setBody('Settings have changed.  Be sure to commit new configuration to disk.<br>')

        for key, val in input.iteritems():
            myPage.setBody('%s: %s<br>' % (key, val))
        myPage.setBody('<a href="/">Go to the main page</a>')
        myPage.setBody('</div>')

        web.output(myPage.output())



#if __name__ == '__main__':
#    app = web.application(urls, globals())
#    app.run

# for version .3, running through fcgi 
application = web.application(urls, globals()).wsgifunc()
web.runfcgi(application, addr='/tmp/webgui.sock-0')

# Still yet another way to run as fcgi
#web.wsgi.runfcgi(web.webpyfunc(urls, globals()), ('/tmp/fcgi.sock-0'))
