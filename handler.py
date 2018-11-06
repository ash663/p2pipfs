import socketserver
#from BaseHTTPServer import BaseHTTPRequestHandler
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import socket
import csv
from ast import literal_eval as make_tuple
import requests

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def parse_path(path):
    l=list(path)                    #   convert path object into list to manipulate elements
    l.pop(0)                        #   pop the '/' from the front of the path to generate requested object hash
    parsed_path = ''.join(l)        #   join() the list back into a string after removing '/'
    return parsed_path

def getFile(reqObj, clientIP):
    with open('published.csv', 'r') as csvfile:
        publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
        csvfile.close()
    for publishTuple in publishedFiles:
        if publishTuple:
            tempTuple = make_tuple(publishTuple[0])
            if tempTuple[0] == reqObj:
                ipPort = str(publishTuple[1]).split(':')
                #print(get_ip_address())
                #print(ipPort[0])
                if str(get_ip_address()) == ipPort[0]:
                    response = 'http://'+clientIP+':8080'
                    with open(tempTuple[1], 'rb') as f: r = requests.post(response, files={tempTuple[1]: f})
                else:
                    #send GET request to other peers
                    with open('peers.csv', 'r') as csvfile:
                        peers = [tuple(line) for line in csv.reader(csvfile)]
                        csvfile.close()
                    for peerTuple in peers:
                        #print(peerTuple)
                        if peerTuple:
                            peerIP = peerTuple[1]
                            peerPort = 8080
                            request = 'http://'+peerIP+':'+str(peerPort)+'/'+reqObj
                            urllib.request.urlopen(request)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        reqObj = parse_path(self.path)

        getFile(reqObj, self.client_address[0])

        self.send_response(200)

    def do_POST(self):
        data = self.rfile.read(10024)
        print(data)

        self.send_response(200)



httpd = socketserver.TCPServer((str(get_ip_address()), 8080), handler)
httpd.serve_forever()
