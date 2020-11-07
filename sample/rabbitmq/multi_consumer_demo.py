import gevent
from gevent import monkey; monkey.patch_all()
import pika
import sys

def callback1(ch, method, properties, body):
    #print("Consumer 1: channel {},method:{}, properties:{},body:{}".format(ch, method, properties, body))
    print("Consumer 1: msg:{}".format(body))

def callback2(ch, method, properties, body):
    #print("Consumer 2: channel {},method:{}, properties:{},body:{}".format(ch, method, properties, body))
    print("Consumer 2: msg:{}".format(body))

handlers = {
    1:callback1,
    2:callback2,
}

def init():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    connection.close()

def producer_loop():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    counter = 1
    while True:
        for i in range(0, 5):
            body = "Hello {}".format(counter)
            counter+=1
            channel.basic_publish(exchange='',
                                  routing_key='hello',
                                  body=body)
        #print(" [x] Sent 'Hello World!'")
        gevent.sleep(1)

def consumer_loop(no, auto_ack=False):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #channel.basic_consume(queue='hello', auto_ack=True, on_message_callback=handlers[no])
    channel.basic_consume(queue='hello', auto_ack=auto_ack, on_message_callback=handlers[no])
    channel.start_consuming()
    while True:
        gevent.sleep(1)

def produce_sample():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    counter = 1
    for i in range(0, 50):
        body = "Hello {}".format(counter)
        counter+=1
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body=body)

def consume_sample(auto_ack=False):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_consume(queue='hello', auto_ack=auto_ack, on_message_callback=callback1)
    channel.start_consuming()
    while True:
        gevent.sleep(1)

def persist_demo():
    auto_ack = True # queue message flooding test
    init()
    produce_sample()
    consume_sample(auto_ack=auto_ack)
    while True:
        gevent.sleep(1)

def main():
    auto_ack = True
    init()
    gevent.spawn(producer_loop)
    gevent.spawn(consumer_loop, no=1, auto_ack=auto_ack)
    gevent.spawn(consumer_loop, no=2, auto_ack=auto_ack)
    while True:
        gevent.sleep(1)

if __name__ == "__main__":
    main()
    #persist_demo()
