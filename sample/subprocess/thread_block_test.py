# -*- coding: utf-8 -*-
import multiprocessing
import threading
import time
import os
import signal

MAX_PROCESS = 2
MAX_THREAD = 5

def thread_test():
    thread_list = []
    for i in range(5):
        thread_name = i
        t = threading.Thread( name=thread_name, target=thread_entry, args=(i,) )
        thread_list.append(t)

    for t in thread_list:
        print "starting thread:" ,t.name
        t.start()

    for t in thread_list:
        t.join()
    

def thread_entry(thread_arg):
    while True:
        print "thread {No} running".format(No=thread_arg)
        time.sleep(1)

thread_test()
    
