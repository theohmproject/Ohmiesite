# Ohmcoin Simple Web Server

import cherrypy
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Main ohm web object
class OhmRoot(object):

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
        # process form data..
        captcha = body['g-recaptcha-response']
        name = body['Name']
        email = body['Email']
        message = body['Message']
        # log to console..
        print ( "RECEIVED FROM: " + email + "  MESSAGE: " + message )
        dateTimeObj = datetime.now() # current time
        # build email body..
        msg = str(dateTimeObj) + " > " + "NAME: " + name + "  EMAIL: " + email + " <br/>\n" + message + "";
        # send mail
        self.sendMail(name, email, msg)
        # log to file..
        file1 = open("contact.log", "a")  # append mode
        file1.write(str(dateTimeObj) + " > " + "NAME: " + name + ", EMAIL: " + email + ", MESSAGE: " + message + "\n")
        file1.close()
        # send response
        message = { "response" : True, "status" : True, "message" : "message sent!" }
        return json.dumps(message)

    #@cherrypy.expose
    #def shutdown(self):
    #    cherrypy.engine.exit()

    def sendMail(self, name, email, msg):
        xfrom = "system@ohmc.tips"
        xto = "squid@sqdmc.net"
        # build the message
        msg['Subject'] = "OHM Contact from " + name
        msg['From'] = xfrom
        msg['To'] = xto
        # Send mail..
        s = smtplib.SMTP('localhost')
        s.sendmail(xfrom, xto, msg.as_string())
        s.quit()
        print( "Mail Sent!" )


# listen on alt port
cherrypy.server.socket_port = 8771
# listen on all interfaces
cherrypy.server.socket_host = '0.0.0.0'

# start the webserver!
cherrypy.quickstart( OhmRoot() )
