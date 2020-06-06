# Ohmcoin Simple Web Server

import cherrypy
import json
import os
import time
import smtplib
import hashlib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from pathlib import Path


# Main ohm web object
class OhmRoot(object):

    COOLDOWN_TIME_IP = 3  # time in seconds between mail attempts per ip..
    COOLDOWN_TIME = 120  # time in seconds between mail attempts per session..
    hostsAgents = {}  # map of host sessions and last mail times.
    hosts = {}  # map of host sessions and last mail times.

    localDir = str(Path(os.path.dirname(os.path.realpath(__file__))).resolve().parent)
    pubDir = localDir + "/public"
    print( "Root Directory: " + localDir )
    _cp_config = {'error_page.404': os.path.join(pubDir, "error/404.html")}

    ###########################################################################
    def __init__(self):
        version = "0.1"
        conf = self.loadConf()
        COOLDOWN_TIME_IP = conf['cooldownhost']
        COOLDOWN_TIME = conf['cooldownagent']

    @cherrypy.expose
    def index(self):
        message = { "response" : True, "status" : True, "message" : "Not a web server. This method is restricted." }
        return json.dumps(message)

    @cherrypy.expose
    def contact_submit(self):
        if (cherrypy.request.method == "GET") :
            message = { "response" : True, "status" : False, "message" : "post required.." }
            return json.dumps(message)
        # setup default vars
        body = json.loads("{}")
        remoteHost = "127.0.0.1"
        userAgent = "1"
        agentHash = "0"
        hostHash = "0"
        # load form data
        try:
            cl = cherrypy.request.headers['Content-Length']
            rawbody = cherrypy.request.body.read(int(cl))
            body = json.loads(rawbody)
            remoteHost = cherrypy.request.headers['X-FORWARDED-FOR']
            userAgent = cherrypy.request.headers['USER-AGENT']
            # get agent hashes..
            agentHash = self.getHostHash(remoteHost, userAgent)
            hostHash = self.getHostHash(remoteHost, 0)
        except Exception as ex:
            print("ERROR: " + ex)
            message = { "response" : False, "status" : False, "message" : "input error.." }
            return json.dumps(message)
        # Check if spam..
        if self.allowHost(hostHash) == False:
            message = { "response" : False, "status" : True, "message" : "you are doing this too often!!" }
            return json.dumps(message)
        elif remoteHost == "127.0.0.1":
            message = { "response" : False, "status" : False, "message" : "host invalid.." }
            return json.dumps(message)
        else:
            self.addHost(hostHash)
        # clean up old agent trackings..
        self.cleanHostAgents()
        # process form data..
        try:
            if 'g-recaptcha-response' in body:
                captcha = body['g-recaptcha-response']
            else:
                captcha = "NA"
            name = body['Name']
            email = body['Email']
            message = body['Message']
        except Exception as ex:
            print("ERROR: " + ex)
            message = { "response" : False, "status" : False, "message" : "input error.." }
            return json.dumps(message)
        # log to console..
        print ( "RECEIVED CONTACT FROM: " + email + "  MESSAGE: " + message )
        # Check if can send..
        if self.allowAgent(agentHash):
            dateTimeObj = datetime.now()  # current time
            # build email body..
            msg = "\nUSER HOST: " + hostHash + "\nUSER AGENT: " + agentHash + "\nSERVER TIME: " + str(dateTimeObj) + "\n\nFROM NAME: " + name + "\nFROM EMAIL: " + email + "\n\nMESSAGE:\n" + message + "";
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
        xfrom = self.conf["systemfrom"]
        xfromName = self.conf["sysnamefrom"]
        xto = self.conf["fowardto"]
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

    # Host Agent cleaner
    def cleanHostAgents(self):
        hosts = []
        agents = []
        # Clean Hosts
        for key in self.hosts:
            if self.getHostTime(key) <= -30:
                hosts.append(key)
        for key in hosts:
            self.hosts.pop(key)
            print( "> Removed Expired Host " + key )
        # Clean Agents
        for key in self.hostsAgents:
            if self.getAgentTime(key) <= -30:
                agents.append(key)
        for key in agents:
            self.hostsAgents.pop(key)
            print( "> Removed Expired Agent " + key )

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

    # Loads the config from file into dict
    def loadConf(self):
        try:
            data = json.loads("{}")
            with open(self.localDir + '/.env/conf.json') as f:
                data = json.load(f)
            self.version = data['CONFIG'][0]['Version']
            username = data['CONFIG'][1]['RPC'][0]['Username']
            password = data['CONFIG'][1]['RPC'][0]['Password']
            port = data['CONFIG'][1]['RPC'][0]['Port']
            sysfrm = data['CONFIG'][2]['EMAIL'][0]['SystemFrom']
            sysnmefrm = data['CONFIG'][2]['EMAIL'][0]['SystemFromName']
            fwdto = data['CONFIG'][2]['EMAIL'][0]['FowardTo']
            chost = data['CONFIG'][3]['XDOS'][0]['CooldownTimeHost']
            cagnt = data['CONFIG'][3]['XDOS'][0]['CooldownTimeAgent']
            item = { "username" : username, "password" : password, "port" : port, "fowardto" : fwdto, "systemfrom" : sysfrm, "sysnamefrom" : sysnmefrm, "cooldownhost" : chost, "cooldownagent" : cagnt}
            print("Config Loaded! Version " + self.version)
            return item
        except Exception as ex:
            print("Config Loading Error!  " + ex)
            return {}

    # Do RPC request
    def doRpcRequest(self, port, user, pazz, method, params):
        url = 'http://127.0.0.1:' + port
        payload = json.dumps({" jsonrpc": "2.0", "id": "pycurl", "method": method, "params": params })
        headers = { 'content-type': 'application/json' }
        r = requests.post(url, data=payload, headers=headers, auth=(user, pazz))
        respj = r.json()
        return respj

    ###########################################################################
    # API Functions..
    @cherrypy.expose
    def getblockheight(self):
        try:
            method = "getblockcount"
            params = []
            hh = self.doRpcRequest(self.conf['port'], self.conf['username'], self.conf['password'], method, params)
            height = hh['result']
        except Exception as ex:
            print("Failed to fetch Height!")
            print(ex)
            return "error"
        return json.dumps({"height": height })

    @cherrypy.expose
    def getconnectioncount(self):
        try:
            method = "getconnectioncount"
            params = []
            cc = self.doRpcRequest(self.conf['port'], self.conf['username'], self.conf['password'], method, params)
            conns = cc['result']
        except Exception as ex:
            print("Failed to fetch Connection count!")
            print(ex)
            return "error"
        return json.dumps({"connections": conns })

    @cherrypy.expose
    def getbestblock(self):
        try:
            method = "getblockcount"
            params = []
            hh = self.doRpcRequest(self.conf['port'], self.conf['username'], self.conf['password'], method, params)
            height = hh['result']
            method = "getblockhash"
            params = [ height ]
            bb = self.doRpcRequest(self.conf['port'], self.conf['username'], self.conf['password'], method, params)
            blockh = bb['result']
        except Exception as ex:
            print("Failed to fetch Block!")
            print(ex)
            return "error"
        return json.dumps({ "blockhash": blockh, "height": height })

# listen on alt port
cherrypy.server.socket_port = 8771
# listen on all interfaces
cherrypy.server.socket_host = '127.0.0.1'

# start the webserver!
cherrypy.quickstart( OhmRoot() )
