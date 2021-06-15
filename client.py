import socket
import os
import subprocess

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
# host = '192.168.1.77'
host= socket.gethostname()
port = 9999

try:
    s.connect((host, port))

    data = s.recv(4096)
    data=data[:].decode("utf-8")
    if data=='ack':
        # cmd = subprocess.Popen(data,shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Connection established with server !\n')
        while True:
            expr=input('Enter expression to evaluate : ')
            expr = expr.lower()
            if len(expr)==0:
                continue

            elif expr=='quit' or expr=='exit':
                s.send(str.encode(expr))
                data = s.recv(4096)
                data=data[:].decode("utf-8")
                if data=='closed':
                    print('Connetion closed with server !')
                else :
                    print('Forcefully closed connection with server !')
                s.close()
                break

            else :
                s.send(str.encode(expr))
                data = s.recv(4096)
                data=data[:].decode("utf-8")
                print('Result on client : ' + data)

except socket.timeout:
    print('Server is busy with another client. Please try again later !\n')

except socket.error as err_msg:
    print('Socket Creation Failed : \n'+ str(err_msg))
    print('Quitting!')

except KeyboardInterrupt:
    print("Exit using Ctrl-C")
    s.close()
except :
    print('Error has occured! Quitting!')
