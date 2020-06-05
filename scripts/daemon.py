# Ohmcoin Simple Web Server

import cherrypy
import json
import os
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


# Main ohm web object
class OhmRoot(object):

    hosts = {}

    def addHost(self, host):
        ts = time.time()
        self.hosts[host] = ts

    def getHost(self, host):
        if host in hosts:
            return self.hosts[host];
        return 0

    def allowHost(self, host):
        ts = time.time()
        th = self.getHost(host)
        if (th <= 0) :
            return True
        return ts - th < 60

    def getHostTime(self, host):
        ts = time.time()
        th = self.getHost(host)
        if (th <= 0) :
            return 0
        return ts - th

    @cherrypy.expose
    def index(self):
        message = { "response" : True, "status" : True, "message" : "not a web server." }
        return json.dumps(message)

    @cherrypy.expose
    def contact_submit(self):
        if (cherrypy.request.method == "GET") :
            message = { "response" : True, "status" : False, "message" : "post required.." }
            return json.dumps(message)
        # load form data
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = json.loads(rawbody)
        remoteHost = cherrypy.request.headers['X_FORWARDED_FOR'];
        print( "Request from " + remoteHost )
        # process form data..
        captcha = body['g-recaptcha-response']
        name = body['Name']
        email = body['Email']
        message = body['Message']
        # log to console..
        print ( "RECEIVED FROM: " + email + "  MESSAGE: " + message )
        dateTimeObj = datetime.now() # current time
        # build email body..
        msg = "SERVER TIME: " + str(dateTimeObj) + "\n" + "NAME: " + name + "\nEMAIL: " + email + "\n\n" + message + "";
        # Check if can send..
        if self.allowHost(remoteHost):
            # send mail
            self.sendMail(name, email, msg)
            # track host..
            addHost(remoteHost)
            # log to file..
            file1 = open("contact.log", "a")  # append mode
            file1.write(str(dateTimeObj) + " > " + "NAME: " + name + ", EMAIL: " + email + ", MESSAGE: " + message + "\n")
            file1.close()
            # send response
            message = { "response" : True, "status" : True, "message" : "message sent!" }
            return json.dumps(message)
        else:
            # send response
            message = { "response" : False, "status" : True, "message" : "you are doing this too often!", "retry" : getHostTime(remoteHost) }
            return json.dumps(message)

    #@cherrypy.expose
    #def shutdown(self):
    #    cherrypy.engine.exit()

    def sendMail(self, name, email, message):
        xfrom = "system@ohmc.tips"
        xfromName = "Ohmc.tips System"
        xto = "squid@sqdmc.net"
        # build the message
        msg = MIMEText(message)
        msg['Subject'] = "[OHMC.TIPS] New Message from '" + name + "'"
        msg['From'] = formataddr((str(Header(xfromName, 'utf-8')), xfrom))
        msg['To'] = xto
        # Send mail..
        s = smtplib.SMTP('localhost')
        s.sendmail(xfrom, xto, msg.as_string())
        s.quit()
        print( "Mail Sent!" )


# listen on alt port
cherrypy.server.socket_port = 8771
# listen on all interfaces
cherrypy.server.socket_host = '127.0.0.1'

# start the webserver!
cherrypy.quickstart( OhmRoot() )
