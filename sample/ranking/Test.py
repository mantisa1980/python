import unittest
import pymongo
import logging
import time
#import redis
import traceback
import datetime
from datetime import datetime, timedelta
from RankSystem import *
import gevent

class RankTestCase(unittest.TestCase):
    def setUp(self):
        conn = pymongo.MongoClient(host='localhost')
        conn.drop_database('unittest_sphinx')
        self.db = conn['unittest_sphinx']
        self._init_logger()

    def tearDown(self):
        pass

    def _init_logger(self):
        logging.basicConfig()
        self.logger = logging.getLogger('')
        self.logger.setLevel(logging.DEBUG)

    
    def test_scheduler(self):
        rss = RankCampaignScheduler(self.logger, self.db)
        for i in range(5):
            rss.update()
            rss.test_resolve_all_campaign()
            gevent.sleep(3)

    def test_rank(self):
        #rs = RankService(self.logger, self.db)
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)

