import socket
import os
import sys
import re
from _thread import *

# Create a Socket ( connect two computers)
def create_socket(h,p):
    global host
    global port
    global threadCount
    global serverSideSocket

    try:
        host = h
        port = p
        serverSideSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as err_msg:
        print('Socket Creation Failed : \n'+ str(err_msg))

# Binding the socket with port and listening for connections
def bind_socket():
    global host
    global port
    global threadCount
    global serverSideSocket

    try:
        print("Binding the Port: " + str(port))
        serverSideSocket.bind((host, port))

        # After successful binding start listening for connections
        serverSideSocket.listen(5)
        # s.setblocking(True)

    except socket.error as err_msg:
        print("Socket Binding Error : \n" + str(err_msg) + "\n" + "Retrying...")
        bind_socket()   # To retry binding the socket in case of failure


def socket_accept():
    global threadCount

    while True:
        try:
            conn, address = serverSideSocket.accept()
            print("Connection has been established! |" + " IP " + address[0] + " | Port " + str(address[1]))

            start_new_thread(multi_threaded_client, (conn,address, ))
            threadCount += 1
            print('Thread Number: ' + str(threadCount))

        except:
            print('Error in accepting connection \n'+ str(socket.error))


def send_ack(conn,address):
    print('Sending ACK to IP: '+address[0]+'    Port: '+ str(address[1]))
    conn.send(str.encode('ack'))


def multi_threaded_client(conn,address):
    send_ack(conn,address)
    process_commands(conn,address)
    if conn:
        conn.close()

def process_commands(conn,address):
    while True:
        expr=str(conn.recv(4096),"utf-8")
        expr=expr.lower()
        if len(expr)==0:
            continue

        elif expr=='exit' or expr=='quit':
            conn.send(str.encode('closed'))
            while True:
                try:
                    print("Closing connection with |" + " IP " + address[0] + " | Port " + str(address[1]))
                    conn.close()
                    break
                except:
                    print('Error closing connection with IP: '+address[0]+'  Port: '+ str(address[1]) +'\nRetrying...')
                    continue

            conn=None
            break

        else:
            if re.match(r'^[0-9+\-*/()]*$', expr):
                result=str(eval(expr))
                print('Processed request from IP : '+address[0]+'  Port: '+ str(address[1]))
                print('Expression : '+expr+' = '+result +'\n')
                conn.send(str.encode(result))
            else:
                print("Error in expression")

def main():
    global threadCount

    h=socket.gethostname()
    p=9999
    threadCount = 0
    keys = ["--host=","--port=","-h=","-p="]
    for i in range(1,len(sys.argv)):
        for key in keys:
            if sys.argv[i].find(key) == 0:
                if key=='--host=' or key=='-h=':
                    h=sys.argv[i][len(key):]
                elif key=='--port=' or key=='-p=':
                    p=int(sys.argv[i][len(key):])

    create_socket(h,p)
    bind_socket()
    socket_accept()
    serverSideSocket.close()
    # signal(SIGINT, handler)

main()
