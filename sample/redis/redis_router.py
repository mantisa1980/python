'''

Basic Design Thoughts
There is a controller which controls the redis map that is active
RedisPool keeps established redis clients . different maps share same redis with same host:port pair



Configs

RoutingConfig (only one document)
{
    group_id: "v1",
    redis_hosts:["redis001:6379", "redis002:6379", "redis003:6379"],
    start_ts: 1600000000,
},

if no routing config: use default (all static configs in RedisClientPool)
else: use routing config , even if start_is is too old. 

class RedisClientPool
build shared redis client , so when cluster config switches, no new connection is required. 

class RedisGroupRouter

class PipelinedRedisRouter: use a RedisGroupRouter to get corresponding redis instance

'''
import time

class MyRedis():
    pass

# this object does not know group
class RedisPool(object):
    def __init__(self):
        self.redis_nodes = {
            "redis001:6379":MyRedis(),
            "redis002:6379":MyRedis(),
        }

    def add_node(self, name, ip, port):
        pass

def RedisRouter(object):
    def __init__(self, config_reader, redis_pool):
        self.config_reader = config_reader
        self.redis_pool = redis_pool
        self.current_group = None
        self.pending_group = None
        self.update()

    def update(self):
        config = self.config_reader.get_config()
        self.sync_redis_group(config)

    def sync_redis_pool(self, config):
        now_ts = time.time()
        if config['start_ts'] > time.time(): # future group exists
            if self.pending_group != config['group_id']:
                print("pending group found!")
                self.pending_group = config['group_id']
            else: # already found pending group
                pass
        else:
            if self.current_group != self.pending_group:
                self.current_group = self.pending_group
                self.pending_group = None
                print("removing pending group")

    def get_nodes(self, key):
        if self.pending_group != None:
            # must check timestamp to use correct group. 
            pass
        else:
            pass
        pass

class RedisRouterConfigReader(object):
    def __init__(self, db):
        self.col_routing_config = db['RoutingConfig']

    def get_config(self):
        r = self.col_routing_config.find_one({})
        if r is None:
            return {
                "group_id": "default",
                "start_ts": 1200000000,
                "redis_hosts":["redis001:6379", "redis002:6379", "redis003:6379"],
            }
        else:
            return {
                "group_id": "v2",
                "start_ts": 1600000000,
                "redis_hosts":["redis001:6379", "redis002:6379", "redis003:6379", "redis004:6379"],
                }

        