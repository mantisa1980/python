# -*- coding: utf-8 -*-
import multiprocessing
import time
 
def process_entry(arg):
    f = open("./log.txt", 'a')

    for i in range(100000):
        f.write("process %s write %s\n"  %(arg,i) )

    print "process %s ends" %(arg) 
    #counter = 0
    #while True:
    #    counter+=1
    #    if (counter % 10000) == 0:
    #        time.sleep(0.1)


if __name__ == "__main__":
    # clear file
    f = open("./log.txt", 'w')
    f.close()
    plist=[]

    for i in range(10):

        p = multiprocessing.Process(target=process_entry, args=(i, ))
        plist.append(p)
        #p.daemon = True # parent process exit時會嘗試關閉child processes. 若沒設該flag, 會發現程式結束後還有很多python process在跑

    for i in plist:
        print "starting pid", i.pid
        i.start()
        print i.pid
    #    i.join()

    print "Sub-process done."

