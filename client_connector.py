#!/usr/bin/python
import socket
import urllib
import re
import os
import time
import argparse             # https://docs.python.org/2/library/argparse.html
import sys
import http.server
import http
import socketserver         # https://docs.python.org/3/library/http.server.html#http.server.HTTPServer
import time
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import webbrowser, os.path


ext2conttype = {"jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "gif": "image/gif"}

pageTemplate = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>P2P Web</title>
</head>
<body>
    {html_object_string}
</body>
</html>'''

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def getFile(reqObj):
    with open('published.csv', 'r') as csvfile:
        publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
        csvfile.close()
    for publishTuple in publishedFiles:
        if publishTuple:
            tempTuple = make_tuple(publishTuple[0])

            if tempTuple[0] == reqObj:
                ipPort = publishTuple.split(':')
                if str(get_ip_address()) == ip[0]:
                    return reqObj
                else:
                    #send GET request to other peers
                    with open('peers.csv', 'r') as csvfile:
                        peers = [tuple(line) for line in csv.reader(csvfile)]
                        csvfile.close()
                    

def fetch_resource(resource):
    '''Start your webbrowser on a local file containing the text
    with given filename.'''
    filename = 'temp.html'
    output = open(filename, "w")
    output.write(resource)
    output.close()
    webbrowser.open("file:///" + os.path.abspath(filename))  # elaborated for Mac


def encapsulate_html_image(imagefile):
    #img=str('cat.jpg')
    img=str(imagefile)
    #C:\Users\timmy\Downloads
    html_object_string = ('<img src="/{img}" border="0" id="img"/>')
    html_object_string = html_object_string.format(**locals())
    print(html_object_string)
    return html_object_string

class client_connector(BaseHTTPRequestHandler):
    # GET requests

    def testResponse(url):
        #resp = requests.get('https://todolist.example.com/tasks/')
        resp = requests.get(url)
        if resp.status_code != 200:
            # This means something went wrong.
            raise RuntimeError('GET /tasks/ {}'.format(resp.status_code))
        else:
            print('ERROR: \r\n \r\n'+ resp.content)
        #for todo_item in resp.json():
           # print('{} {}'.format(todo_item['id'], todo_item['summary']))
        return resp.content

    def do_GET(self):

        #   Send response status code
        self.send_response(200)

        #   Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        #   Send message back to client
        reqObj = parse_path(self.path)
        message= "Requested resource: " + reqObj + "\r\n\r\n"

        self.wfile.write(bytes(message, 'utf8'))
        ##########################
        # Place code here to communicate to content manager/tracker subsystems
        ##########################
        reqobj=getFile(reqObj)
        #   displays fetched object
        html_object_string =  encapsulate_html_image(str(reqObj))
        contents = pageTemplate.format(**locals())  # inserts into .html file
        #print('Printing object: \r\n \r\n' + contents)
        fetch_resource(contents)    # displays generated .html file in a new tab on default browser

        return



def parse_path(path):
    l=list(path)                    #   convert path object into list to manipulate elements
    l.pop(0)                        #   pop the '/' from the front of the path to generate requested object hash
    parsed_path = ''.join(l)        #   join() the list back into a string after removing '/'
    return parsed_path              #   return string sans leading forward slash

def run():
    print ('Starting server...')

    #   Server Settings
    #   Port 80 needs Root access, using loop back address..
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, client_connector)
    print ('Running server...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
