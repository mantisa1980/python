import os
import time
import gevent
import concurrent
from google.cloud import pubsub_v1
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    MessageMetadata,
    TopicPath,
)

# Resolve the publish future in a separate thread.
def callback(future: pubsub_v1.publisher.futures.Future) -> None:
    message_id = future.result()
    print("Successfully published:", message_id)

batch_settings = pubsub_v1.types.BatchSettings(
                max_bytes=1024*1024*1024,
                max_latency=5,
                max_messages=1024, 
            )

# TODO(developer):
project_number = 'rd7-data-test-big-query'
cloud_region = "asia-southeast1"
zone_id = "c"
topic_id = "BackendLog"

location = CloudZone(CloudRegion(cloud_region), zone_id)
t = time.time()
topic_path = TopicPath(project_number, location, topic_id)
print(time.time()-t)
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/duyhsieh/gcp/keys/bigquery-key-test.json'

with PublisherClient().from_service_account_file('/Users/duyhsieh/gcp/keys/bigquery-key-test.json', per_partition_batching_settings=batch_settings)  as publisher_client:
    while True:
        publish_futures = []
        for i in range(3):
            data = "Hello world {}!{}".format(i, int(time.time()))
            print("sending ", data)
            future = publisher_client.publish(topic_path, data.encode("utf-8"))
            future.add_done_callback(callback)
            publish_futures.append(future)

        # skip waiting, let batch trigger its condition and send it out
        #message_id = future.result()
        #message_metadata = MessageMetadata.decode(message_id)
        #print(f"Published a message to partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}.")
        concurrent.futures.wait(publish_futures, return_when=concurrent.futures.ALL_COMPLETED)
        #time.sleep(1)
