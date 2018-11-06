import socket
import threading
from threading import Thread
import main as main
import re

#class ThreadedServer(object):
class ThreadedServer(Thread):
    def __init__(self, host, port, in_queue, out_queue):
        super(ThreadedServer, self).__init__()
        self.daemon = True
        self.cancelled = False
        self.host = host
        self.port = port
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        while not self.cancelled:
            self.listen()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            #client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            #try:
            data = client.recv(size)
            #print "Waiting here prolly"
            self.in_queue.put(data) # inserts client data into externally accessible queue
                #while not self.in_queue.empty():
                    #response = self.in_queue.get() # generating echo response
                    #Check if peering request or published message.
            '''if re.search('peer', response) or re.search('PEER', response):
                        #do peer
                        #Create object - hostname, PORT
                        peerObject = main.p2pwebprompt()
                        peerObject.do_peer(response)
                        #main.do_peer(response)
                        #print "?"
                    elif re.search('publish', response):
                        #do publish
                        pass
                    else:
                        print(response)
                        client.send(response) # echoing received data'''
                #return self.in_queue
            '''except:
                print("Closing")
                client.close()
                return False'''

if __name__ == "__main__":
    while True:
        port_num = int(input("Port? "))
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('',port_num).listen()
