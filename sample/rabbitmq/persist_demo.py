import gevent
from gevent import monkey; monkey.patch_all()
import pika
import sys

def callback1(ch, method, properties, body):
    #print("Consumer 1: channel {},method:{}, properties:{},body:{}".format(ch, method, properties, body))
    print("Consumer 1: msg:{}".format(body))

def init():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello2', durable=True)
    connection.close()

def produce_sample():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    counter = 1
    for i in range(0, 10):
        body = "Hello {}".format(counter)
        counter+=1
        channel.basic_publish(exchange='',
                              routing_key='hello2',
                              properties=pika.BasicProperties(delivery_mode=2),
                              body=body)

def consume_sample(auto_ack=False):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_consume(queue='hello2', auto_ack=auto_ack, on_message_callback=callback1)
    channel.start_consuming()
    while True:
        gevent.sleep(1)

def persist_demo():
    auto_ack = False # queue message flooding test
    init()
    produce_sample()
    consume_sample(auto_ack=auto_ack)
    while True:
        gevent.sleep(1)

# demo: non-acked messages are persist even after program restart
if __name__ == "__main__":
    init()
    persist_demo()
