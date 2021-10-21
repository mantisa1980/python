from google.cloud.pubsublite.cloudpubsub import SubscriberClient
from google.cloud.pubsublite.types import (
    CloudRegion,
    CloudZone,
    SubscriptionPath,
    DISABLED_FLOW_CONTROL,
    FlowControlSettings,
)

settings = FlowControlSettings(messages_outstanding=1024, bytes_outstanding=1024*1024*10)

def callback(message):
    message_data = message.data.decode("utf-8")
    print(f"Received {message_data}.")
    #message.ack()

project_number = 'rd7-data-test-big-query'
cloud_region = "asia-southeast1"
zone_id = "c"
subscription_id = "BackendLogSub"

location = CloudZone(CloudRegion(cloud_region), zone_id)
subscription_path = SubscriptionPath(project_number, location, subscription_id)

with SubscriberClient().from_service_account_file('/Users/duyhsieh/gcp/keys/bigquery-key-test.json') as subscriber_client:
    streaming_pull_future = subscriber_client.subscribe(
        subscription_path,
        callback=callback,
        per_partition_flow_control_settings=settings,
    )

    streaming_pull_future.result()