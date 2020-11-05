import gevent
from gevent import monkey; monkey.patch_all()
import pika

def callback(ch, method, properties, body):
    print("channel {},method:{}, properties:{},body:{}".format(ch, method, properties, body))

def producer_loop():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    while True:
        print "Producer publish"
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body='Hello World!')
        print(" [x] Sent 'Hello World!'")
        gevent.sleep(1)

def consumer_loop():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_consume(queue='hello',
                      auto_ack=True,
                      on_message_callback=callback)

    channel.start_consuming()
    while True:
        gevent.sleep(1)

def init():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    connection.close()

def main():
    init()
    gevent.spawn(producer_loop)
    gevent.spawn(consumer_loop)
    while True:
        gevent.sleep(1)

if __name__ == "__main__":
    main()