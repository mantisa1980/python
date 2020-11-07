import gevent
from gevent import monkey; monkey.patch_all()
import pika
import sys

def callback1(ch, method, properties, body):
    print("Consumer 1: msg:{}".format(body))

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
            channel.basic_publish(exchange='', routing_key='hello', body=body)
        gevent.sleep(1)

def consumer_loop(no, auto_ack=False):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #channel.basic_consume(queue='hello', auto_ack=True, on_message_callback=handlers[no])
    channel.basic_consume(queue='hello', auto_ack=auto_ack, on_message_callback=handlers[no])
    channel.start_consuming()
    while True:
        gevent.sleep(1)

def main():
    init()
    auto_ack = True
    gevent.spawn(producer_loop)
    gevent.spawn(consumer_loop, no=1, auto_ack=auto_ack)
    while True:
        gevent.sleep(1)

if __name__ == "__main__":
    main()
