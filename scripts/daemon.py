# Ohmcoin Simple Web Server

import cherrypy
import json
import os
import time
import smtplib
import hashlib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


# Main ohm web object
class OhmRoot(object):

    MAIL_RECEIVER = "squid@sqdmc.net"
    COOLDOWN_TIME = 120  # time in seconds between mail attempts..
    COOLDOWN_TIME_IP = 3  # time in seconds between mail attempts..
    hostsAgents = {}  # map of host sessions and last mail times.
    hosts = {}  # map of host sessions and last mail times.

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
        remoteHost = cherrypy.request.headers['X-FORWARDED-FOR']
        userAgent = cherrypy.request.headers['USER-AGENT']
        agentHash = self.getHostHash(remoteHost, userAgent)
        hostHash = self.getHostHash(remoteHost, 0)
        # Check if spam..
        if !self.allowHost(hostHash):
            message = { "response" : False, "status" : True, "message" : "you are doing this too often!!" }
            return json.dumps(message)
        else:
            self.addHost(hostHash)
        # process form data..
        captcha = body['g-recaptcha-response']
        name = body['Name']
        email = body['Email']
        message = body['Message']
        # log to console..
        print ( "RECEIVED FROM: " + email + "  MESSAGE: " + message )
        dateTimeObj = datetime.now() # current time
        # build email body..
        msg = "\nUSER HOST: " + hostHash +
            "\nUSER AGENT: " + agentHash +
            "\nSERVER TIME: " + str(dateTimeObj) +
            "\n\nFROM NAME: " + name +
            "\nFROM EMAIL: " + email +
            "\n\nMESSAGE:\n" + message + "";
        # Check if can send..
        if self.allowAgent(agentHash):
            # send mail
            self.sendMail(name, email, msg)
            # track host..
            self.addAgent(agentHash)
            # log to file..
            file1 = open("contact.log", "a")  # append mode
            file1.write(str(dateTimeObj) + " > " + "NAME: " + name + ", EMAIL: " + email + ", MESSAGE: " + message + "\n")
            file1.close()
            # send response
            message = { "response" : True, "status" : True, "message" : "message sent!", "retry" : 0 , "id" : agentHash }
            return json.dumps(message)
        else:
            # send response
            message = { "response" : False, "status" : True, "message" : "you are doing this too often!", "retry" : self.getAgentTime(agentHash), "id" : agentHash }
            return json.dumps(message)

    ###########################################################################
    # Send Email message
    def sendMail(self, name, email, message):
        xfrom = "system@ohmc.tips"
        xfromName = "ohmc.tips SYSTEM"
        xto = self.MAIL_RECEIVER
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

    # Hosts
    def addHost(self, host):
        ts = time.time()
        self.hosts[host] = ts

    def getHost(self, host):
        if host in self.hosts:
            return self.hosts[host];
        return 0

    def allowHost(self, host):
        ts = time.time()
        th = self.getHost(host)
        if (th <= 0) :
            return True
        return ts - th > self.COOLDOWN_TIME_IP

    def getHostTime(self, host):
        ts = time.time()
        th = self.getHost(host)
        if (th <= 0) :
            return 0
        return self.COOLDOWN_TIME_IP - (ts - th)

    # User Agents
    def addAgent(self, host):
        ts = time.time()
        self.hostsAgents[host] = ts

    def getAgent(self, host):
        if host in self.hostsAgents:
            return self.hostsAgents[host];
        return 0

    def allowAgent(self, host):
        ts = time.time()
        th = self.getAgent(host)
        if (th <= 0) :
            return True
        return ts - th > self.COOLDOWN_TIME

    def getAgentTime(self, host):
        ts = time.time()
        th = self.getAgent(host)
        if (th <= 0) :
            return 0
        return self.COOLDOWN_TIME - (ts - th)

    # Gets hash of host or agent
    def getHostHash(self, host, client):
        h = str(host);
        c = str(client);
        return hashlib.sha256(str(h + "::" + c).encode('utf-8')).hexdigest()

# listen on alt port
cherrypy.server.socket_port = 8771
# listen on all interfaces
cherrypy.server.socket_host = '127.0.0.1'

# start the webserver!
cherrypy.quickstart( OhmRoot() )
