# -*- coding: utf-8 -*-
import multiprocessing
import time
import os

def process_entry(arg):
    print "entering process_entry: args=%s,current proccess info %s, getpid()=%s, getppid=%s, pgid=%s" % (arg,multiprocessing.current_process(), os.getpid(),os.getppid(),os.getpgrp() )
    while True:
        pass


if __name__ == "__main__":
    plist=[]

    print "main process info:%s, pid=%s, ppid=%s, pgid=%s" %(multiprocessing.current_process(), os.getpid(), os.getppid(),os.getpgrp() ) # 這的ppid其實就是bash的process id

    for i in range(4):
        p = multiprocessing.Process(target=process_entry, args=(i, ) )
        p.daemon = True # parent process exit時會嘗試關閉child processes. 若沒設該flag, 會發現程式結束後還有很多python process在跑. 但設deamon也可能很多sub process還沒起來, parent process一離開就直接結束了.
        plist.append(p)


    for i in plist:
        i.start()
        print i.pid
    #    i.join()

    time.sleep(3)

    for i in plist:
        print "child process %s alive before terminate:%s" %( i, i.is_alive())
        i.terminate()
        print "child process %s alive after terminate:%s" %( i, i.is_alive() )
        i.join()
        print "child process %s alive after join:%s, exitcode=%s" %( i, i.is_alive(), i.exitcode )


    print "Sub-process done."

