# -*- coding: utf-8 -*-
#!/usr/bin/env python
import time
from time import sleep
import json
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['192.168.132.200:19092'], 
                         key_serializer=lambda x: str(x),
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                         acks=0
                         )
ts = int(time.time())
for e in range(3):
    data = {'ts':ts,  'number' : e}
    r = producer.send('numtest', value=data, key=ts)
    print('sent', data, r)

producer.flush(timeout=10)
