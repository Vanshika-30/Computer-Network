import threading
import copy
global counter

def inc():
    global counter
    for i in range(1000000):
        threadLock.acquire()
        counter=counter+1
        threadLock.release()

def main():
    global counter
    counter=0
    t1 = threading.Thread(target=inc, args=())
    t2 = threading.Thread(target=inc, args=())
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(counter)

# threadLock=threading.Lock()
# main()

# print(min(5,float('inf')))

original = {1:['one',1], 2:['two',2]}
new = copy.deepcopy(original)

original[2][1]=5
print('new: ', new)
print('original: ', original)
