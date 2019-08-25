import threading
import time

def readfq(file_name,count):
    f = open("2.fq")
    t = f.read()
    print (count)
    f.close()

try:
    t1 = threading.Thread(target = readfq,args = ("2.fq", 1, ))
    t2 = threading.Thread(target = readfq,args = ("2.fq", 2, ))
    #t3 = threading.Thread(target = readfq,args = ("2.fq", 3, ))
    t1.start()
    t2.start()
    #t3.start()
    t1.join()
    t2.join()
    #t3.join()
except:
    print ("error")


