from threading import Thread
import Queue
import time


def thread_it(f, *args, **kwargs):
    t = Thread(target=f, args=args, kwargs=kwargs)
    t.setDaemon(True)
    t.start()
    return t

TO_RETURN = -1 

class Message(object):
    def __init__(self, content):
        self.content = content
    def get_message(self):
        return self.content

class ChannelManager(object):
    def __init__(self, channel_count):
        self.channels = list()
        for no in xrange(channel_count):
            self.channels.append(Channel(no, self));
    
    def get_channel(self,no):
        return self.channels[no]

    def get_channel_count(self):
        return len(self.channels)

class Channel(object):
    def __init__(self, no, channel_mgr):
        self.__queue = Queue.Queue()
        self.no = no
        self.channel_mgr = channel_mgr

    def get_channel_no(self):
        return self.no

    def send_message(self, message):
        self.__queue.put(message);

    def get_next_queue(self):
        next_no = (self.no + 1) % self.channel_mgr.get_channel_count()
        return self.channel_mgr.get_channel(next_no) 

    def task_loop(self):
        #print "entry of channel", self.no
        while True:
            r = self.__queue.get()
            msg = r.get_message()
            print "channel ", self.no , " receive ", msg,

            if msg == TO_RETURN or msg == 100:
                self.get_next_queue().send_message(Message(TO_RETURN))
                print "channel done: no=", self.no
                break
            m = Message(msg+1)
            next_chan = self.get_next_queue().get_channel_no()
            #print "send ", m.get_message() , id(m), " to channel", next_chan
            self.get_next_queue().send_message(m)
            #time.sleep(1)
            

c_mgr = ChannelManager(5)
threads = []
for i in range(c_mgr.get_channel_count()):
    threads.append(thread_it(c_mgr.get_channel(i).task_loop ))

c_mgr.get_channel(0).send_message(Message(0))

for t in threads:
    t.join()
