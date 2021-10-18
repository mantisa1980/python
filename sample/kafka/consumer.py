import gevent
from gevent import monkey, pool;monkey.patch_all()
from kafka import KafkaConsumer, TopicPartition
import json
from json import loads

'''
consumer apis
commit(offsets=None).
the committed offset should be the next message your application should consume, i.e.: last_offset + 1.
committed: (partition, metadata=False) Get the last committed offset for the given partition.
commit_async(offsets=None, callback=None)
'''

## TODO: TopicPartition offset data structure manipulation for commit / commitasync ??

def on_offset_commit(*args, **kwargs):
    print("on commit offset", args, kwargs)

def consume_it(topic,  client_id):
    consumer = KafkaConsumer(
     topic,
     bootstrap_servers=['192.168.132.200:19092'],
     #auto_offset_reset='latest',
     auto_offset_reset='earliest',
     auto_commit_interval_ms=5000,
     enable_auto_commit=True,
     #enable_auto_commit=False,
     group_id='CCC',
     client_id=client_id,
     default_offset_commit_callback=on_offset_commit,
     max_poll_records=500,
     value_deserializer=lambda x: loads(x.decode('utf-8')))

    #consumer.commit(offset=0)
    assigned_partitions = consumer.assignment()
    print("client entering loop:{}, last commit:{}".format(client_id, {str(i):consumer.committed(i) for i in assigned_partitions } ))
    for m in consumer:
        print('{} consume:topic={},partiton={},offset={},timestamp={},key={},value={}'.format(
        client_id, m.topic,m.partition,m.offset,m.timestamp,m.key,m.value))

        assigned_partitions = consumer.assignment()
        print("client entering loop:{}, last commit:{}".format(client_id, {str(i):consumer.committed(i) for i in assigned_partitions } ))

if __name__ == "__main__":
    workers = []
    for r in ['cli1', 'cli2']:
        workers.append(gevent.spawn(consume_it, 'numtest', r))

    for w in workers:
        w.join()
