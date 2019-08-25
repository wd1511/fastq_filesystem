import multiprocessing
import time
def func(msg):
    f = open("2.fq")
    t = f.read()
    print (msg)
if __name__ == "__main__":
    pool = multiprocessing.Pool(processes = 4)
    for i in range(10):
        msg = "hello %d :" %(i)
        pool.apply_async(func,(msg, ))
    pool.close()
    pool.join()
