# Ohmcoin Simple Web Server

import cherrypy
import json
import os

# Public web directory
PUB_DIR = "C:\\DEV\\sites\\ohm\\Ohmiesite\\public\\";

# Main ohm web object
class OhmRoot(object):
    
    #@cherrypy.expose
    #def index(self):
    #    message = { "response" : True, "status" : True, "message" : "not a web server." }
    #    return json.dumps(message)

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
        
        # TODO: process input!!!
        
        # send response
        message = { "response" : True, "status" : True, "message" : "message sent!" }
        return json.dumps(message)

    @cherrypy.expose
    def shutdown(self):  
        cherrypy.engine.exit()


##############################################
# Serve all files in public directory
conf = { '/':
    {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': PUB_DIR,
        'tools.staticdir.index': 'index.html',
    },
}

# listen on alt port
cherrypy.server.socket_port = 8771
# listen on all interfaces
cherrypy.server.socket_host = '0.0.0.0'

# start the webserver!
cherrypy.quickstart( OhmRoot(), config = conf )

