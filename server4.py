import select
import socket
import sys
import queue


# Create a Socket ( connect two computers)
def create_socket(h,p):
    global host
    global port
    global server

    try:
        host = h
        port = p
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)

    except socket.error as err_msg:
        print('Socket Creation Failed : \n'+ str(err_msg))

# Binding the socket with port and listening for connections
def bind_socket():
    global host
    global port
    global server

    try:
        print("Binding the Port: " + str(port))
        server.bind((host, port))

        # After successful binding start listening for connections
        server.listen(5)
        # s.setblocking(True)

    except socket.error as err_msg:
        print("Socket Binding Error : \n" + str(err_msg) + "\n" + "Retrying...")
        bind_socket()   # To retry binding the socket in case of failure

def socket_accept():
    global server
    # Sockets from which we expect to read
    inputs = [server]

    # Sockets to which we expect to write
    outputs = []

    # Outgoing message queues (socket:Queue)
    message_queues = {}

    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        # print('waiting for the next event', file=sys.stderr)
        readable, writable, exceptional = select.select(inputs,outputs,inputs)

        # Handle inputs
        for s in readable:
            if s is server:
                # A "readable" socket is ready to accept a connection
                connection, client_address = s.accept()
                print("\nConnection has been established! |" + " IP " + client_address[0] + " | Port" + str(client_address[1]))
                # send_ack(connection,client_address)
                connection.setblocking(0)
                inputs.append(connection)
                # Give the connection a queue for data we want to send
                message_queues[connection] = queue.Queue()
                message_queues[connection].put('ack')
                if connection not in outputs:
                        outputs.append(connection)

            else:
                client_address=s.getpeername()
                data = s.recv(4096)
                if data:
                    expr=str(data,"utf-8")
                    expr=expr.lower()
                    if expr=='quit' or expr=='exit':
                        message_queues[s].put('closed')
                    else:
                        message_queues[s].put(expr)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)

                else:
                    # Interpret empty result as closed connection
                    print("\nNo Data to be sent to " + " IP " + client_address[0] + "  Port " + str(client_address[1]))
                    print('Closing Connection !! \n')
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

        # Handle outputs
        for s in writable:
            client_address=s.getpeername()
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                # No messages waiting so stop checking for writability.
                print('\nNo message to be sent to IP: '+client_address[0]+' Port : ' +str(client_address[1])+' !!'+'\n')
                outputs.remove(s)
            else:
                if next_msg=='closed':
                    print("\nClosing connection with |" + " IP " + client_address[0] + " | Port " + str(client_address[1])+'\n')
                    s.send(str.encode(next_msg))
                    outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                elif next_msg=='ack':
                    print('Sending ACK to IP: '+client_address[0]+'    Port: '+ str(client_address[1])+'\n')
                    s.send(str.encode(next_msg))
                    outputs.remove(s)
                else:
                    print('Received message from IP : '+client_address[0]+'  Port: '+ str(client_address[1]))
                    print('Message : '+next_msg+'\nEchoing message back')
                    s.send(str.encode(next_msg))
                    outputs.remove(s)

        # Handle "exceptional conditions"
        for s in exceptional:
            client_address=s.getpeername()
            print('\nException condition on IP: '+client_address[0]+' Port : ' +str(client_address[1])+' !!\n')
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            # Remove message queue
            del message_queues[s]

    server.close()

def main():
    h=socket.gethostname()
    p=9999
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


main()
