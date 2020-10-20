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
import random

class RankTestCase(unittest.TestCase):
    def setUp(self):
        self.MAX = 50
        self.ark_ids = [str(i) for i in range(10000001, 10000001+self.MAX)]
        self.ark_id = '10000001'
        self.ark_id2 = '10000002'
        self.ark_id3 = '10000003'
        self.ark_id4 = '10000004'
        conn = pymongo.MongoClient(host='localhost')
        conn.drop_database('unittest_sphinx')
        self.db = conn['unittest_sphinx']
        self._init_logger()
        self.rd_pfr = pymongo.ReadPreference.PRIMARY
        self.cron = None
    
    def ark_id(self, i):
        return self.ark_ids[i]

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

    def _test_rank_game(self):
        # create rank cron to create campaign
        level = 1
        group = 0
        game = RankGame(self.logger, self.db)
        game.add_score(self.ark_id, 100) # no effect
        self.__create_cron()
        self.cron.scheduler.update() # create first campaign

        
        game.campaign_reader.update()
        campaign_id = game.campaign_reader.get_active_campaign().get_campaign_id()
        game.add_score(self.ark_id, 100)
        game.score.add_player_score(campaign_id, self.ark_id2, 1, 0, 100)
        game.score.add_player_score(campaign_id, self.ark_id3, 1, 1, 100)
        game.score.add_player_score(campaign_id, self.ark_id4, 2, 0, 100)

        print " ----- group Scores:", game.get_score_module().get_group_score(campaign_id, level, group, rd_pfr=self.rd_pfr)
        print "get_all_scores", game.get_score_module().get_all_scores(campaign_id)

        self.cron.scheduler.test_resolve_all_campaign()
        #gevent.sleep(15)

    
    def _test_rank_game_integration(self):
        self.__create_cron()
        game = RankGame(self.logger, self.db)
        #self.cron.ap_scheduler.pause()
        #game.ap_scheduler.pause()
        CampaignScheduler.INTERVAL_UNIT = 'minute'

        self.cron.scheduler.cfg = {
            'total_interval': 60,
            'close_interval': 30, 
            'end_interval': 15, # end (resolve) ~ next campaign
            'auto_create': True, # auto create next campaign when current one resolved
            'upgrade_ratio':0.3,
            'downgrade_ratio':0.1,
            'group_max':100,
        }

        while True:
            self.cron.update() # create first campaign
            game.update()
            campaign = game.campaign_reader.get_active_campaign()
            if campaign != None:
                campaign_id = game.campaign_reader.get_active_campaign().get_campaign_id()
                print "Unittest: Active campaign going on; clock:", datetime.datetime.now().replace(microsecond=0) # trim annoying microseconds 
                game.add_score(self.ark_id, 10)
                game.add_score(self.ark_id2, 10)
                game.add_score(self.ark_id3, random.randint(1,10))
                game.add_score(self.ark_id4, random.randint(1,10))
                
                #game.score.add_player_score(campaign_id, self.ark_id2, 1, 0, 10)
                #game.score.add_player_score(campaign_id, self.ark_id3, 1, 1, random.randint(1,10))
                #game.score.add_player_score(campaign_id, self.ark_id4, 2, 0, random.randint(1,10))
                #print " ----- group Scores:", game.get_score_module().get_group_score(campaign_id, level, group, rd_pfr=self.rd_pfr)
                #print "get_all_scores", game.get_score_module().get_all_scores(campaign_id)
            else:
                print "Unittest: NO active campaign; clock:", datetime.datetime.now().replace(microsecond=0)

            #self.cron.scheduler.test_resolve_all_campaign()
            gevent.sleep(1)

    def test_random_rank_game_integration(self):
        self.__create_cron()
        game = RankGame(self.logger, self.db)
        CampaignScheduler.INTERVAL_UNIT = 'minute'

        self.cron.scheduler.cfg = {
            'total_interval': 60,
            'close_interval': 30, 
            'end_interval': 15, # end (resolve) ~ next campaign
            'auto_create': True, # auto create next campaign when current one resolved
            'upgrade_ratio':0.3,
            'downgrade_ratio':0.3,
            'group_max':10,
        }

        while True:
            self.cron.update() # create first campaign
            game.update()
            campaign = game.campaign_reader.get_active_campaign()
            if campaign != None:
                campaign_id = game.campaign_reader.get_active_campaign().get_campaign_id()
                print "Unittest: Active campaign going on; clock:", datetime.datetime.now().replace(microsecond=0) # trim annoying microseconds 
                for i in xrange(100):
                    random_id = random.choice(self.ark_ids)
                    game.add_score(random_id, 10)
            else:
                print "Unittest: NO active campaign; clock:", datetime.datetime.now().replace(microsecond=0)
            gevent.sleep(1)
    
    def __create_cron(self):
        if self.cron == None:
            self.cron = RankCron(self.logger, self.db)

    def _test_rank_resolver(self):
        level = 1
        group = 0
        game = RankCron(self.logger, self.db)
        game.scheduler._CampaignScheduler__create_campaign()
        

if __name__ == "__main__":
    unittest.main(verbosity=2)

