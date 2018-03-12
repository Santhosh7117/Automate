import BaseHTTPServer
from threading import Thread
import urllib2
import socket
import time
from Queue import Queue
post_body = ''
class __MyHandler__(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_POST(s):
        global post_body
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        content_len = int(s.headers.getheader('content-length'))
        post_body = s.rfile.read(content_len)

class Eventsink():   
    def __init__(self,Q):
        self.__port__ = None
        self.__Q__ = Q
        self.__CONTINUE__=True
        self.__serverThread__=None
        self.__STATE__='STOPPED' 
        
    def __continue__(self):
        if self.__CONTINUE__:
            return True
        else:
            return False

    def __startListener__(self):
        global post_body
        while self.__continue__():
            self.httpd.handle_request()
            self.__Q__.put(post_body)
        self.__STATE__='STOPPED'

    def start(self,port):
        self.__port__ = int(port)
        if self.__STATE__=='STOPPED':
            server_address = ('', self.__port__)                
            server_class=BaseHTTPServer.HTTPServer
            handler_class=__MyHandler__  
            self.httpd = server_class(server_address, handler_class)
            self.eventSinkURL='http://'+socket.gethostbyname(socket.getfqdn())+':'+str(self.__port__)+'/'

            self.__serverThread__ = Thread(target=self.__startListener__)
            self.__CONTINUE__=True
            self.__serverThread__.start()
            self.__STATE__='RUNNING'
            return 'STARTED'
        else:
            return 'SERVER ALREADY RUNNING'

    def stop(self):
        if self.__STATE__=='RUNNING':
            self.__CONTINUE__=False
            site=self.getEventSinkURL()
            data=''
            headers = {
                'Content-Type': 'text/html;charset=utf-8',
                'Content-Length': len(data),
            }
            req = urllib2.Request(site, data, headers)
            req.get_method = lambda: 'POST'
            urllib2.urlopen(req)
            #self.updateOutput('Server Stopped!')
            self.__STATE__='STOPPED'
            return 'STOPPED'
        else:
            return 'SERVER NOT RUNNING'

    def getEventSinkURL(self):
        return self.eventSinkURL

    def test(self, data='TEST MESSAGE'):
        data='%s' %(data)
        if self.__STATE__=='RUNNING':
            site=self.getEventSinkURL()
            headers = {
                'Content-Type': 'text/html;charset=utf-8',
                'Content-Length': len(data),
            }
            req = urllib2.Request(site, data, headers)
            req.get_method = lambda: 'POST'
            urllib2.urlopen(req)
            return 'TEST SUCCESSFULL'
        else:
            return 'SERVER NOT RUNNING'
        
    
    def restart(self,port=None):
        if port:
            self.__port__ = port
        try:
            self.stop()
            self.start(self.__port__)
            return 'RESTARTED'
        except:
            return 'FAILED'    

if __name__ == "__main__":
    Q = Queue()
    ec = Eventsink(Q)
















        
