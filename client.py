# Python TCP Client A
import socket
import sys
import rsa
from time import sleep

if(len(sys.argv)>1):
    host=sys.argv[1]
    if(len(sys.argv)>2):
        port=int(sys.argv[2])
    else:
        port=8080
else:
    host = socket.gethostname()
    port = 8080

gotKey=False
gotName=False
MESSAGE='_I_NEED_THE_KEY_'
MESSAGE=MESSAGE.encode()
publicKey=''

exit=False

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClientA.connect((host, int(port)))

while not exit:
    tcpClientA.send(MESSAGE)
    if not gotKey:
        data = tcpClientA.recv(1024).decode()
        if data.startswith('_PUBKEY_'):
            pk=data[8:]
            beGone=pk[10:]
            n=beGone.split(',')[0]
            n=int(n)
            we=beGone.split(',')[1][1:]
            e=we[:len(we)-1]
            e=int(e)
            publicKey=rsa.PublicKey(n,e)
            gotKey=True
    elif not gotName:
        MESSAGE = input("Enter username: ")
        MESSAGE='_SETNAME_'+MESSAGE
        MESSAGE=rsa.encrypt(MESSAGE.encode(),publicKey)
        MESSAGE=str(MESSAGE).encode()
        gotName=True
    else:
        MESSAGE = input("Enter message: ")
        if(MESSAGE=='exit'):
            exit=True
            break
        MESSAGE=rsa.encrypt(MESSAGE.encode(),publicKey)
        MESSAGE=str(MESSAGE).encode()

MESSAGE='_OFFLINE_'
MESSAGE=rsa.encrypt(MESSAGE.encode(),publicKey)
MESSAGE=str(MESSAGE).encode()
tcpClientA.send(MESSAGE)
sleep(1)
tcpClientA.close()
