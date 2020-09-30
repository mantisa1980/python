import unittest
import pymongo
import logging
import time
#import redis
import traceback
import datetime
from datetime import datetime, timedelta
from RankSystem import *

class RankTestCase(unittest.TestCase):
    def setUp(self):
        #conn = pymongo.MongoClient(host='mongo')
        #conn.drop_database('_UnitTest_ML')
        #self.db = conn['_UnitTest_ML']
        self.db = None
        self._init_logger()

    def tearDown(self):
        pass

    def _init_logger(self):
        logging.basicConfig()
        self.logger = logging.getLogger('')
        self.logger.setLevel(logging.DEBUG)

    def test_rank(self):
        acc = RankAccumulator(self.logger, self.db)
        rank = Rank(self.logger, self.db)
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)

