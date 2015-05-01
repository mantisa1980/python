# -*- coding: utf-8 -*-
import multiprocessing
import time
import os
import signal



def signal_handler_sub(signum, stack):
    print "Sub Process receive signal:signal=%s proccess info %s, getpid()=%s, getppid=%s, pgid=%s" % (signum,multiprocessing.current_process(), os.getpid(),os.getppid(),os.getpgrp() )
    #print 'Receive stack:%s, fcode=%s' %(stack, stack.f_code )

def signal_handler_main(signum, stack):
    print "Main process receive signal:signal=%s proccess info %s, getpid()=%s, getppid=%s, pgid=%s" % (signum,multiprocessing.current_process(), os.getpid(),os.getppid(),os.getpgrp() )
    #print 'Receive stack:%s, fcode=%s' %(stack, stack.f_code )

def process_entry(arg):
    #signal.signal(signal.SIGTERM, signal_handler_sub) # set signal handler
    print "entering process_entry: args=%s,current proccess info %s, getpid()=%s, getppid=%s, pgid=%s" % (arg,multiprocessing.current_process(), os.getpid(),os.getppid(),os.getpgrp() )
    signal.signal(signal.SIGTERM, signal_handler_sub) # set signal handler
    while True:
        pass

if __name__ == "__main__":
    plist=[]

    print "main process info:%s, pid=%s, ppid=%s, pgid=%s" %(multiprocessing.current_process(), os.getpid(), os.getppid(),os.getpgrp() ) # 這的ppid其實就是bash的process id

    for i in range(2):
        p = multiprocessing.Process(target=process_entry, args=(i, ) )
        p.daemon = True # parent process exit時會嘗試關閉child processes. 若沒設該flag, 會發現程式結束後還有很多python process在跑. 但設deamon也可能很多sub process還沒起來, parent process一離開就直接結束了.
        plist.append(p)


    for i in plist:
        i.start()
        print i.pid
    #    i.join()


    time.sleep(3) # wait some time , let child process spawned.
    signal.signal(signal.SIGTERM, signal_handler_main) # set signal handler

    '''
    for i in plist:
        print "child process %s alive before terminate:%s" %( i, i.is_alive())
        i.terminate()
        print "child process %s alive after terminate:%s" %( i, i.is_alive() )
        i.join()
        print "child process %s alive after join:%s, exitcode=%s" %( i, i.is_alive(), i.exitcode )
    '''
    
    # try killing all child processes
    print "killing sub processes"
    for i in plist:
        os.kill(i.pid, signal.SIGTERM)
        #i.join() # 不加這行會發現sub process依舊還在, 但ps aux查看 , 會標一個defunct tag

    os.kill(os.getpid(), signal.SIGTERM) # signal main process itself, but it is caught and nothing happen
    #os.killpg(os.getpgrp(), signal.SIGTERM)
    raw_input() # check if all child process alives



    print "Sub-process done."

