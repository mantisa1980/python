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
        self.ark_id = '10000001'
        self.ark_id2 = '10000002'
        self.ark_id3 = '10000003'
        self.ark_id4 = '10000004'
        conn = pymongo.MongoClient(host='localhost')
        conn.drop_database('unittest_sphinx')
        self.db = conn['unittest_sphinx']
        self._init_logger()

    def tearDown(self):
        pass

    def _init_logger(self):
        logging.basicConfig()
        #log = logging.getLogger('apscheduler.executors.default')
        self.logger = logging.getLogger('')
        self.logger.setLevel(logging.DEBUG)

        apscheduler_logger = logging.getLogger('apscheduler.executors.default')
        apscheduler_logger.addHandler(logging.StreamHandler())
        apscheduler_logger.setLevel(logging.ERROR)
    
    def test_rank_assigner(self):
        pass

    def test_score_bank(self):
        pass

    def _test_scheduler(self):
        rss = CampaignScheduler(self.logger, self.db)
        for i in range(5):
            rss.update()
            #rss.test_resolve_all_campaign()
            gevent.sleep(3)
    
    def _test_infinite_scheduler(self):
        rss = CampaignScheduler(self.logger, self.db)
        while True:
            rss.update()
            gevent.sleep(1)
    
    def _test_score(self):
        level = 1
        group = 0
        score = Score(self.logger, self.db)
        r = score.get_group_score(level, 0)
        assert r == None
        init_data = {
            '10000001':{'score':0, 'last_update_timestamp':0},
            '10000002':{'score':0, 'last_update_timestamp':0},
            '10000003':{'score':0, 'last_update_timestamp':0},
        }
        score.init_group_score(level, group, init_data)

        r = score.get_group_score(level, group)
        time.sleep(1) # wait secondary
        assert r == init_data, r

    def _test_level(self):
        level = Level(self.logger, self.db)
        group = 0
        r = level.init_level(self.ark_id, group)
        assert r == {'ark_id':self.ark_id, 'level':1, 'group': 0}, r

        r = level.init_level(self.ark_id, group)
        assert r == None, r

        assert level.get_level(self.ark_id) == {'ark_id':self.ark_id, 'level':1, 'group': 0}

        for i in range(Level.MAX-1):
            r = level.level_up(self.ark_id)
            assert r != None, r

        assert level.level_up(self.ark_id) == None
        assert level.get_level(self.ark_id)['level'] == Level.MAX, level.get_level(self.ark_id)

    def test_rank_game(self):
        # create rank cron to create campaign
        level = 1
        group = 0
        game = RankGame(self.logger, self.db)
        game.add_score(self.ark_id, 100) # no effect
        self.__create_rank_cron()
        self.cron.scheduler.update() # create first campaign

        game.campaign_reader.update()
        game.add_score(self.ark_id, 100)
        game.score.add_player_score(self.ark_id2, 1, 0, 100)
        game.score.add_player_score(self.ark_id3, 1, 1, 100)
        game.score.add_player_score(self.ark_id4, 2, 0, 100)

        print " ----- group Scores:", game.get_score_module().get_group_score(level, group)
        print "get_all_scores", game.get_score_module().get_all_scores()

        self.cron.scheduler.test_resolve_all_campaign()
        #gevent.sleep(15)

    def __create_rank_cron(self):
        self.cron = RankCron(self.logger, self.db)

    def _test_rank_resolver(self):
        level = 1
        group = 0
        game = RankCron(self.logger, self.db)
        game.scheduler._CampaignScheduler__create_campaign()
        

if __name__ == "__main__":
    unittest.main(verbosity=2)

