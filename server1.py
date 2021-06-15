import socket
import sys
import re
from signal import signal, SIGINT

# Create a Socket ( connect two computers)
def create_socket(h,p):
    try:
        global host
        global port
        global s
        host=h
        port=p
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    except socket.error as err_msg:
        print('Socket Creation Failed : \n'+ str(err_msg))

# Binding the socket with port and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))

        # After successful binding start listening for connections
        s.listen(5)

    except socket.error as err_msg:
        print("Socket Binding Error : \n" + str(err_msg) + "\n" + "Retrying...")
        bind_socket()   # To retry binding the socket in case of failure


def socket_accept(h,p):
    while True:
        try:
            create_socket(h,p)
            bind_socket()
            conn, address = s.accept()
            s.close()

            print("Connection has been established |" + " IP " + address[0] + " | Port " + str(address[1]))
            send_ack(conn)
            process_commands(conn)
            if conn is not None:
                conn.close()
        except:
            print('Error in accepting connection \n'+ str(socket.error))

    server.close()

def send_ack(conn):
    print('Sending ACK')
    conn.send(str.encode('ack'))


def process_commands(conn):
    while True:
        try:
            expr=str(conn.recv(4096),"utf-8")
            expr=expr.lower()
            if len(expr)==0:
                continue

            elif expr=='exit' or expr=='quit' :
                conn.send(str.encode('closed'))
                while True:
                    try:
                        conn.close()
                        break
                    except:
                        print('Error closing connection! Retrying...')
                        continue

                conn=None
                break

            else:
                if re.match(r'^[0-9+\-*/()]*$', expr):
                    result=str(eval(expr))
                    print('Result on server: '+ result + '\n')
                    conn.send(str.encode(result))
                else:
                    print("Error in expression")

        except KeyboardInterrupt:
                    print("Exit using Ctrl-C\n")
                    exit()

def main():
    h=socket.gethostname()
    p=9999
    keys = ["--host=","--port=","-h=","-p="]
    for i in range(1,len(sys.argv)):
        for key in keys:
            if sys.argv[i].find(key) == 0:
                # print(f"The Given value is: {sys.argv[i][len(key):]}")
                if key=='--host=' or key=='-h=':
                    h=sys.argv[i][len(key):]
                elif key=='--port=' or key=='-p=':
                    p=int(sys.argv[i][len(key):])

    socket_accept(h,p)

main()
