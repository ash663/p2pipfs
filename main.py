import sys
import dns.resolver
import threading
import hashlib
import time
import threadedserver
from cmd import Cmd
import _thread
from queue import Queue
from pathlib import Path
import os
import socket
import csv
import re
import _pickle as cPickle
from ast import literal_eval as make_tuple

HOST_PORT = 50007

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def not_int(object):  # Helper function to verify integer value
    try:
        int(object)
        return False
    except ValueError:
        return True

def peering(self, in_q, out_q):
    peer_instance = threadedserver.ThreadedServer('', HOST_PORT, in_q, out_q)
    peer_instance.start()

def network_queue(self, queue):
    try:
        while True:
            while queue.empty():
                pass
            while not queue.empty():
                response = queue.get().decode("utf-8")
                if re.search('peer', response) or re.search('PEER', response):
                    #Create object - hostname, PORT
                    #peerObject = p2pwebprompt()
                    #peeringResult = peerObject.do_PEER(response)
                    prompt.onecmd(response)
                    '''parameters = response.split(' ')  # generate object array with empty space delimiter, ' '
                    if len(parameters) != 3: #includes the term 'peer'
                        print('Incorrect number of parameters, please use PEER <peer-hostname> <peer-port> structure: ')
                    peeringResult = peerHelper(parameters)
                    if peeringResult:
                        print("Peered Succesfully")
                    else:
                        print("Peering failed")'''
                elif re.search('publish', response) or re.search('PUBLISH', response):
                    #do publish
                    prompt.onecmd(response)
                elif re.search('unpublish', response) or re.search('UNPUBLISH', response):
                    #do unpublish
                    prompt.onecmd(response)
                elif re.search('remotepub', response) or re.search('REMOTEPUB', response):
                    prompt.onecmd(response)
                elif re.search('remoteunpub', response) or re.search('REMOTEUNPUB', response):
                    prompt.onecmd(response)

    except BaseException as e:
        print(str(e))
#TODO: Write seperate actual peering logic as a function.

def peerHelper(object):
    '''parameters = object.split(' ')  # generate object array with empty space delimiter, ' '

    if len(parameters) != 3: #includes the term 'peer'
        print('Incorrect number of parameters, please use PEER <peer-hostname> <peer-port> structure: ')
        return False
    else:
        #if not_int(parameters[2]):
        #    print('<peer-port> is not integer value: ')
        #else:'''
    print('Executing peering...')
    hostname = object[1]
    PORT = int(object[2])

    myResolver = dns.resolver.Resolver()  # create DNS resolver object
    myAnswers = myResolver.query(hostname, 'A') # DNS query using <peer-hostname> value for 'A' Record
    print('Found the following IP address for hostname [' + hostname + ']:')
    for dnsResults in myAnswers:
        print(dnsResults)  # display IPs mapped to hostname
        HOST_IP = str(dnsResults)
    #ping = os.system("ping -c 1 " + HOST_IP)  #Assume peers don't go down (Mentioned in discussion).
    #Send PEER request only if not in files. TODO: Reverse above line and below few
    #if ping==0:
    with open('peers.csv', 'r') as csvfile:
        peers = [tuple(line) for line in csv.reader(csvfile)]
        csvfile.close()
    with open('peers.csv', 'w') as peersFile:
        peerTuple = (hostname, HOST_IP, str(PORT))
        if peerTuple in peers:
            #duplicate
            csvwriter = csv.writer(peersFile)
            for peerTuple in peers:
                csvwriter.writerow(peerTuple)
            peersFile.close()
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((HOST_IP, int(PORT)),)
            peerRequest = ('PEER '+str(get_ip_address())+' '+str(PORT)).encode()
            sock.send(peerRequest)
            sock.close()
            csvwriter = csv.writer(peersFile)
            peers.append(peerTuple)
            for peerTuple in peers:
                csvwriter.writerow(peerTuple)
            peersFile.close()
    return True
    #return False

def publishHelper(object):
    filename = object[0]

    #opened_file = open('C:\CNXTHDASUP.log', 'rb')  # open file in 'read binary' mode
    if os.path.exists(filename):
        print('File found!')
        print('Publishing object with filename "' + filename + '"')
        with open(filename, 'rb') as file:
            read_data = file.read()
            hash = hashlib.sha1()
            hash.update(read_data)
            #print(hash)
            #
            fileHash = hash.hexdigest()
            fileType = 'text/html'
            metadata = (fileHash,filename,fileType)
            ipAddress = get_ip_address()
            endPoint = str(ipAddress)+':'+str(HOST_PORT)
            tempTupleList=[]
            #sequenceNumber = 0
            with open('published.csv', 'r') as csvfile:
                publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
                csvfile.close()
            for i in publishedFiles:
                if i:
                    tempTuple = make_tuple(i[0])
                    tempTupleList.append((tempTuple, i[1]),)
            with open('published.csv', 'w') as publishedCSV:
                publishTuple = (metadata,endPoint)
                #print(publishTuple)
                #print(publishedFiles)
                if publishTuple in tempTupleList:
                    #duplicate
                    csvwriter = csv.writer(publishedCSV)
                    for files in tempTupleList:
                        csvwriter.writerow(files)
                    publishedCSV.close()
                else:
                    csvwriter = csv.writer(publishedCSV)
                    tempTupleList.append(publishTuple)
                    for files in tempTupleList:
                        csvwriter.writerow(files)
                    publishedCSV.close()
                    #Check PEERS, and publish metadata to all peers
                    with open('peers.csv', 'r') as csvfile:
                        peers = [tuple(line) for line in csv.reader(csvfile)]
                        csvfile.close()
                    #print(peers)
                    for peerTuple in peers:
                        #print(peerTuple)
                        if peerTuple:
                            peerIP = peerTuple[1]
                            peerPort = peerTuple[2]
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            #try:
                            sock.connect((peerIP, int(peerPort)),)
                            #sendToPeer = cPickle.dumps(publishTuple)
                            sendToPeer = ('REMOTEPUB '+str(publishTuple)).encode()
                            sock.send(sendToPeer)
                            sock.close()
                        #except:
                        #    print('Peer unavailable')
                        #    return False
        return True
    else:
        print('File not found!')
        return False

def unpublishHelper(fl, object):
    if fl:
        fileHash = object
    else:
        fileHash = object[0]
    #print(object)
    flag=0
    with open('published.csv', 'r') as csvfile:
        publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
        csvfile.close()
    for publishTuple in publishedFiles:
        if publishTuple:
            tempTuple = make_tuple(publishTuple[0])

        if tempTuple[0] == fileHash:
            publishedFiles.remove(publishTuple)
            flag=1
    with open('published.csv', 'w') as publishedCSV:
        csvwriter = csv.writer(publishedCSV)
        for files in publishedFiles:
            csvwriter.writerow(files)
        publishedCSV.close()
    with open('peers.csv', 'r') as csvfile:
        peers = [tuple(line) for line in csv.reader(csvfile)]
        csvfile.close()
    if flag:
        for peerTuple in peers:
            #print(peerTuple)
            if peerTuple:
                peerIP = peerTuple[1]
                peerPort = peerTuple[2]
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #try:
                sock.connect((peerIP, int(peerPort)),)
                #sendToPeer = cPickle.dumps(publishTuple)
                sendToPeer = ('REMOTEUNPUB '+str(fileHash)).encode()
                sock.send(sendToPeer)
                sock.close()
    if flag == 1:
        return True
    else:
        return False

class p2pwebprompt(Cmd):
    def do_quit(self, args):
        # Quits Program
        print('Exiting program.')
        raise SystemExit

    def do_peer(self, object):
        self.do_PEER(object)  # supports case-insensitive option
    def do_PEER(self, object):
        parameters = object.split(' ')
        if len(parameters) != 2: #includes the term 'peer'
            print('Incorrect number of parameters, please use PEER <peer-hostname> <peer-port> structure: ')
        temp = parameters[0]
        parameters[0] = 'PEER'
        parameters.append(parameters[1])
        parameters[1] = temp
        peeringResult = peerHelper(parameters)
        if peeringResult:
            print("Peered Succesfully")
        else:
            print("Peering failed")

    def do_publish(self, object):
        self.do_PUBLISH(object)  # supports case-insensitive option
    def do_PUBLISH(self, object):
        parameters = object.split(' ')  # generate object array with empty space delimiter, ' '
        if len(parameters) != 1:
            print('Incorrect number of parameters, please use PUBLISH <filename> structure: ')
            for x in parameters :
                print(x)
        else:
            if publishHelper(parameters):
                print('Published succesfully')
            else:
                print('Failed to publish')
            ######################################
            # Execute logic for 'PUBLISH'        #
            ######################################
    def do_REMOTEUNPUB(self, object):
        parameters = object
        if unpublishHelper(1, parameters):
            print('Unpublished succesfully')
        else:
            print('Failed to unpublish, or file doesn\'t exist')

    def do_REMOTEPUB(self, object):
        parameters = object
        tempTupleList=[]
        #parameters = object.split(' ')
        with open('published.csv', 'r') as csvfile:
            publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
            csvfile.close()
        for i in publishedFiles:
            if i:
                tempTuple = make_tuple(i[0])
                tempTupleList.append((tempTuple, i[1]),)
        with open('published.csv', 'w') as publishedCSV:
            #parameters = parameters.decode()
            publishTuple = make_tuple(parameters)
            #print(publishTuple)
            if publishTuple in tempTupleList:
                #duplicate
                csvwriter = csv.writer(publishedCSV)
                for files in tempTupleList:
                    csvwriter.writerow(files)
                publishedCSV.close()
            else:
                csvwriter = csv.writer(publishedCSV)
                tempTupleList.append(publishTuple)
                for files in tempTupleList:
                    csvwriter.writerow(files)
                publishedCSV.close()
                #Check PEERS, and publish metadata to all peers
                with open('peers.csv', 'r') as csvfile:
                    peers = [tuple(line) for line in csv.reader(csvfile)]
                    csvfile.close()
                for peerTuple in peers:
                    peerIP = peerTuple[1]
                    peerPort = peerTuple[2]
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    #try:
                    sock.connect((peerIP, int(peerPort)),)
                    #sendToPeer = cPickle.dumps(publishTuple)
                    sendToPeer = ('REMOTEPUB '+str(publishTuple)).encode()
                    sock.send(sendToPeer)
                    sock.close()

    def do_unpublish(self, object):
        self.do_UNPUBLISH(object)  # supports case-insensitive option
    def do_UNPUBLISH(self, object):
        parameters = object.split(' ')  # generate object array with empty space delimiter, ' '
        if len(parameters) != 1:
            print('Incorrect number of parameters, please use PUBLISH <filename> structure: ')
        else:
            hash = parameters[0]
            print('Un-publishing object with hash "' + hash + '"')
            ######################################
            # Execute logic for 'UNPUBLISH'      #
            ######################################
            if unpublishHelper(0, parameters):
                print('Unpublished succesfully')
            else:
                print('Failed to unpublish, or file doesn\'t exist')

    def do_show_peer(self, object):
        self.do_SHOW_PEER(object)  # supports case-insensitive option
    def do_SHOW_PEER(self, object):
        print('Showing peered hosts table: ')
        ######################################
        # Execute logic for 'SHOW_PEERS'     #
        ######################################
        with open('peers.csv', 'r') as csvfile:
            peers = [tuple(line) for line in csv.reader(csvfile)]
            csvfile.close()
        for i in peers:
            print(i)

    def do_show_metadata(self, object):
        self.do_SHOW_METADATA(object)  # supports case-insensitive option
    def do_SHOW_METADATA(self, object):
        print('Showing metadata table: ')
        tempTupleList=[]
        ######################################
        # Execute logic for 'SHOW_METADATA'  #
        ######################################
        with open('published.csv', 'r') as csvfile:
            publishedFiles = [tuple(line) for line in csv.reader(csvfile)]
            csvfile.close()
        for i in publishedFiles:
            if i:
                tempTuple = make_tuple(i[0])
                tempTupleList.append((tempTuple, i[1]),)
        for i in tempTupleList:
            print(i)


if __name__ == '__main__':
    #_thread.start_new_thread(print_time, ("Thread-1", 2,))  # Replace 'print_time' with peering loop
    in_q = Queue()
    out_q = Queue()
    _thread.start_new_thread(peering, ("Peering: ", in_q, out_q,))
    _thread.start_new_thread(network_queue, ("Network1: ", in_q,))
    #_thread.start_new_thread(network_queue, ("Network2: ", out_q,))

    prompt = p2pwebprompt()
    prompt.cmdloop('Initializing CLI for P2P Web...  \nWritten by Tim Gowan & Ashish Patil')
