# -*- coding: utf-8 -*-
import multiprocessing
import time
 
def process_entry(arg):
    time.sleep(10)
    #counter = 0
    #while True:
    #    counter+=1
    #    if (counter % 10000) == 0:
    #        time.sleep(0.1)


if __name__ == "__main__":

    for i in range(10):
        p = multiprocessing.Process(target=process_entry, args=(i, ))
        p.daemon = True
        p.start()

    #p1.join()
    #p2.join()
    #p3.join()
    #p4.join()

    print "Sub-process done."

