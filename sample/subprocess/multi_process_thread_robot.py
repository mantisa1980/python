# -*- coding: utf-8 -*-
import multiprocessing
import threading
import time
import os
import signal

'''
launch MAX_PROCESS process, each process launching MAX_THREAD threads; Each thread running execution of one robot
note: keyboard interrupt is sent to all sub process

'''

class Robot():
    def __init__(self,name):
        self.name = name
        pass
    def run(self):
        self.perform_one_action()

    def perform_one_action(self):
        #print "Robot {name} doing task:".format(name=self.name)
        counter = 0
        for i in range(0,1000000):
            counter +=1

class RobotManager():
    def __init__(self):
        self.active_flag = True
        self.name = None
        self.robots={}

    def create_robot(self,name):
        r = Robot(name)
        self.robots[name] = r
        return r

    def is_enable(self):
        return self.active_flag

    def disable(self):
        self.active_flag = False

    def set_name(self,name):
        self.name = name

    def get_robot(self, name):
        return self.robots[name]

MAX_PROCESS = 2
MAX_THREAD = 4
#SIGINT_FLAG = False  # note : fork時subprocess會一起被複製 (但因為copy-on-write特性, 你有改道他才複製另一份給child process)
robot_manager = RobotManager()

def signal_handler(signum, stack):
    global robot_manager
    print "receive signal:signal=%s pid=%s" % (signum,os.getpid())
    robot_manager.disable()

def subprocess_entry(process_arg):
    signal.signal(signal.SIGINT, signal_handler)
    #print "subprocess_entry:process_arg=%s,current proccess info %s, getpid()=%s, getppid=%s, pgid=%s" % (process_arg,multiprocessing.current_process(), os.getpid(),os.getppid(),os.getpgrp())
    global robot_manager # cloned in subprocess
    robot_manager.set_name(process_arg)

    thread_list = []
    for i in range(MAX_THREAD):
        robot_name = "".join([process_arg, "t", str(i) ] )
        robot_manager.create_robot(robot_name)
        thread = threading.Thread( target=thread_entry, args=(robot_manager, robot_name) )
        thread_list.append(thread)
        thread.start()

    try:
        while robot_manager.is_enable():
            time.sleep(1)
    except KeyboardInterrupt: # actually a sigint signal transformed by python intepreter
        print "subprocess %s catch KeyboardInterrupt" % os.getpid()
    except Exception as e:
        print "subprocess %s catch exception:%s" % os.getpid(), str(e)        
    finally:
        robot_manager.disable()

    for thread in thread_list:
        thread.join() # 這會讓subprocess block, 無法處理signal handler.
    print "sub process {PID} done".format(PID=os.getpid())

def thread_entry(robot_mgr, robot_name):
    while robot_mgr.is_enable():
        robot_mgr.get_robot(robot_name).perform_one_action()
        time.sleep(0.001)

def main():
    global robot_manager
    process_list=[]

    for i in range(MAX_PROCESS):
        p = multiprocessing.Process(target=subprocess_entry, args=("".join(["p",str(i)]) ,) )
        p.daemon = True # parent process exit時會嘗試關閉child processes. 若沒設該flag, 會發現程式結束後還有很多python process在跑. 但設deamon也可能很多sub process還沒起來, parent process一離開就直接結束了.
        process_list.append(p)

    print "main process id:%s" % os.getpid()
    for i in process_list:
        i.start()
        print "subprocess launched,pid=",i.pid

    signal.signal(signal.SIGTERM, signal_handler)
    #signal.signal(signal.SIGINT, sigint_handler) #若用sigint接住, 就不會觸發到 try/except的 KeyboardInterrupt

    kill_flag = True
    try:
         while robot_manager.is_enable():
             time.sleep(0.1)
    except KeyboardInterrupt:
        kill_flag = False
        print "main process catch keyboard exception" # subprocess也會收到KeyboardInterrupt,所以自己會停
        #time.sleep(1) # wait for subprocess to finish, so main process does not need issue os.kill to them
        pass
    except Exception as e:
        print "main process catch exception:%s" % str(e)
        pass
    finally:
        robot_manager.disable()
        pass

    for i in process_list:
        if kill_flag:
            if i.is_alive(): # 只有 parent process收到kill signal的case; 若是KeyboardInterrupt大家會一起
                print "subprocess still alive: killing pid", i.pid
                os.kill(i.pid, signal.SIGINT)
        i.join()

    print "main process done. exit program"

if __name__ == "__main__":
    main()
    
