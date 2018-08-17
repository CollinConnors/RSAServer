import socket
import os
import threading
from threading import *
import _thread
import rsa
from codecs import encode

clients = set()
clients_lock = threading.Lock()

(pubKey, privKey)= rsa.newkeys(512)

num=0

class SuperClient:
    def __init__(self, client, numms):
        global num
        self.client=client
        self.type='NONE'
        self.pubKey=''
        self.numms=numms
        num+=1

    def setKey(self,n,e):
        self.pubKey=rsa.PublicKey(n,e)

    def setType(self,type):
        self.type=type

    def isDisplay(self):
        return(self.type=='Display')

def listener(SuperClient, address):
    print ("Accepted connection from: ", address)
    Name=str(address)
    gotKey=False
    with clients_lock:
        clients.add(SuperClient)
    try:
        while True:
            data = SuperClient.client.recv(1024)
            if not data:
                break
            elif(data.decode().startswith('_I_NEED_THE_KEY_')):
                message='_PUBKEY_'+str(pubKey)
                gotKey=True
                with clients_lock:
                    for c in clients:
                        c.client.sendall(message.encode())
            elif(data.decode().startswith('_KEY_')):
                data=data.decode()
                pk=data[5:]
                beGone=pk[10:]
                n=beGone.split(',')[0]
                n=int(n)
                we=beGone.split(',')[1][1:]
                e=we[:len(we)-1]
                e=int(e)
                SuperClient.setKey(n,e)
                SuperClient.setType('Display')
            else:
                krypto=data.decode()
                crypto=encode(krypto.encode().decode('unicode_escape'),"raw_unicode_escape")
                crypto=crypto[2:len(crypto)-1]
                mess=str(rsa.decrypt(crypto, privKey))
                mess=mess[2:len(mess)-1]
                if(mess.startswith('_SETNAME_')):
                    Name=mess[9:]
                    with clients_lock:
                        for c in clients:
                            message='SYSTEM: '+Name+str(address)+' is now online'
                            if(c.isDisplay()):
                                print(c.numms)
                                print(message)
                                message=rsa.encrypt(message.encode(),c.pubKey)
                                c.client.sendall(str(message).encode())
                elif(mess).startswith('_OFFLINE_'):
                    Name=mess[9:]
                    with clients_lock:
                        for c in clients:
                            message='SYSTEM: '+str(address)+' offline'
                            if(c.isDisplay()):
                                print(c.numms)
                                print(message)
                                message=rsa.encrypt(message.encode(),c.pubKey)
                                c.client.sendall(str(message).encode())
                else:
                    #print (repr(data))
                    with clients_lock:
                        for c in clients:
                            message=str(Name)+': '+mess
                            if(c.isDisplay()):
                                print(c.numms)
                                print(message)
                                message=rsa.encrypt(message.encode(),c.pubKey)
                                c.client.sendall(str(message).encode())
    finally:
        with clients_lock:
            clients.remove(SuperClient)
            SuperClient.client.close()

host = ''
port = 8080

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host,port))
s.listen(1)
th = []

while True:
    print ("I'm Waiting")
    client, address = s.accept()
    betterClient=SuperClient(client, num)
    th.append(Thread(target=listener, args = (betterClient,address)).start())

s.close()
