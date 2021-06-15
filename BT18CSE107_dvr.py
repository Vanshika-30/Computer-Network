# Name: Vanshika Jain
# Roll No.: BT18CSE107

import time
import threading
import sys
from queue import Queue
import copy

# Function to update queue of each router after 2s
def update_queue(router,shared,node_name):
    for n in router['neighbours']:
        # acquiring queue lock so that 2 threads don't overwrite the data
        lck=shared[n][1]
        temp={}
        lck.acquire()

# Putting the dvr table in the neighbours og this thread
        for key, value in router['dvr'].items():
            temp[key] = value
        shared[n][0].put((node_name,copy.deepcopy(temp)))
        lck.release()

    queue = shared[node_name][0]
# Looping untill all the neighbouring routers have sent the updated table
    while queue.qsize()!=len(router['neighbours']):
        continue

# Function to update the table using Bellman Ford equation
def bellman_ford(router,shared,node_name):
    queue = shared[node_name][0]

    newTable = copy.deepcopy(router['dvr'])
# iterating over all the items of the queue
    while not queue.empty():
        nn,tables = queue.get()

        src = node_name
        for dest,value in newTable.items():
            cost1 = value[0]
            cost2 = tables[dest][0]

            if cost2 != float('inf') and cost2 + newTable[nn][0] < cost1:
                newCost, newHop = cost2 + router['dvr'][nn][0], router['dvr'][nn][1]
                newTable[dest] = (newCost, newHop)

    changed = {}
# updating the value and keeping track of all the links where a change occured
    for dest,value in newTable.items():
        if router['dvr'][dest][0]!=value[0] or router['dvr'][dest][1]!=value[1]:
            changed[dest]=value
        router['dvr'][dest] = value
    return changed

def task(router,shared,id,node):
    # share table with neighbours
    # update table (neighbours.length > queue..size)
    # print new table
    i = 0;
    while i<4:
        i+=1
        update_queue(router,shared,node)
        changed = bellman_ford(router,shared,node)

# Creating a common list of strings for printing
        totalNodes = 0
        s=''
        s += "\tROUTER: {rname}\n".format(rname=node)
        s += "Destination\tCost\tNext Hop\n"

        for dest,value in router['dvr'].items():
            if dest in changed.keys():
                s = s + ' *  '+ dest + '\t\t' + str(value[0]) + '  \t   ' + value[1] + '\n'
            else:
                s = s + '    '+ dest + '\t\t' + str(value[0]) + '  \t   ' + value[1] + '\n'
            totalNodes += 1

        s += '\n'

# checking if all threads have appended the new table and printing
        shared['printLock'].acquire()
        shared['finalString'][id] = s
        shared['counter'].append(id)

        if(len(shared['counter']) == totalNodes):
            print('----------------------------------ITERATION {iter}----------------------------------\n'.format(iter=i))
            for s in shared['finalString']:
                print(s)
            shared['finalString'] = [0]*totalNodes
            shared['counter']=[]
        shared['printLock'].release()
        time.sleep(2)

# looping the threads untill all have complete the current iteration
        while True:
            shared['printLock'].acquire()
            if id not in shared['counter']:
                 shared['printLock'].release()
                 break
            shared['printLock'].release()

        while id in shared['counter']:
            continue

# Function to print initial condition
def print_init(router,nlist):
    s='----------------------------------INITIAL----------------------------------\n'
    for node in nlist:
        s += "\tROUTER: {rname}\n".format(rname=node)
        s += "Destination\tCost\tNext Hop\n"

        for dest,value in router[node]['dvr'].items():
            s = s + '    '+ dest + '\t\t' + str(value[0]) + '  \t   ' + value[1] + '\n'

        s += '\n'

    print(s)


def main(shared):
    # reading the file
    fname=sys.argv[1]
    f = open(fname,'r')
    Lines = f.readlines()

    cnt=0
    node_count=0
    nlist=''

# Router is a dictionary with keys as node names. This is used to store router information
# For each node name there is a subsequent dictionary with keys: neighbours and dvr
    router = {}

    for line in Lines:
        s=line.strip()
        if s=='EOF':
            break
        if cnt==0:
            node_count=int(s)
            cnt=1
        elif cnt==1:
            nlist=s.split(' ')
            for node in nlist:
                shared[node]=[Queue(maxsize=node_count),threading.Lock()]

                router[node]={}
                router[node]['neighbours'] = []
                router[node]['dvr'] = {}
                for n in nlist:
                    router[node]['dvr'][n]=(float('inf'),'NA')

                router[node]['dvr'][node]=(0,node)

            cnt=2
        else:
            src,dest,cost=s.split()
            cost = float(cost)

            router[src]['dvr'][dest] = (cost,dest)
            router[dest]['dvr'][src] = (cost,src)

            router[src]['neighbours'].append(dest)
            router[dest]['neighbours'].append(src)

    threads = []
    shared['counter']= []
    shared['printLock'] = threading.Lock()
    shared['finalString'] = [0]*node_count

    print_init(router,nlist)

    for id,node in enumerate(nlist):
        th = threading.Thread(target=task, args=(router[node],shared,id,node))
        threads.append(th)
        th.start()

    for t in threads:
        t.join()

# For storing shared information, shared dictionary is used. It has keys: {node-names, counter, printLock,finalString}
# Key nodename conatins the queue for each node where the updated tables are sent after each iteration. It also has a key lock
shared={}

main(shared)
