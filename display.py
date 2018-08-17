import socket
import sys
import rsa
from codecs import encode

if(len(sys.argv)>1):
    host=sys.argv[1]
    if(len(sys.argv)>2):
        port=sys.argv[2]
    else:
        port=8080
else:
    host = socket.gethostname()
    port = 8080

(pubKey, privKey)= rsa.newkeys(512)
MESSAGE=('_KEY_'+str(pubKey))
prevdata='Display Online'
print(prevdata)

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClientA.connect((host, int(port)))

MESSAGE=MESSAGE.encode()
tcpClientA.send(MESSAGE)

while True:
    data = tcpClientA.recv(1024)
    mess=data.decode()
    if not (mess==prevdata) and not data.decode().startswith('_PUBKEY_'):
        krypto=data.decode()
        crypto=encode(krypto.encode().decode('unicode_escape'),"raw_unicode_escape")
        crypto=crypto[2:len(crypto)-1]
        mess=str(rsa.decrypt(crypto, privKey))
        mess=mess[2:len(mess)-1]
        print (mess)
    prevdata=mess

tcpClientA.close()
