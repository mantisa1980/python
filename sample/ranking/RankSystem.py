#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
from datetime import timedelta
import traceback
import pymongo
import sys
import gevent
from apscheduler.schedulers.gevent import GeventScheduler
'''
# when calculating results, players are blocked from playing to avoid ranking race condition and ambiguity

#### score mongodb schema

# always only one document
Campaign
{
    'campaign_id'
    'begin_datetime'
    'closing_datetime'
    'end_datetime'
    'resolved':0
}
index:
campaign_id (unique)
is_active

Level
{
    ark_id
    level
    group:
}

Score
{
    level:0,
    group: 0,
    player_data:{
        'uid':{
            'score':0,
            'last_timestamp':
        }
    }
}

# only for level 1 new users
GroupDispatchInfo {
    level:
    counter:
}


#TODO: drop CampaignScore and recreate index once calculate finish.
#TODO: after adding score , if no group, dispatch one

Score:
{
    campaign_id
    ark_id
    last_update_ts
    score
    level (main group)
    group (sub group)
}
index: score / last_update_ts

RankResultLog
{
    CampaignID
    UserID
    FromRankGroup
    ToRankGroup
    FromRankLevel
    ToRankLevel 
}

#TODO: if add score to campaign, return data does not have rank, append rank info from Rank onto it

### Put in user info (assign award時可以一起加減level)
RankInfo
{
    ark_id
    level
    #group
}
index: ark_id

'''


class Campaign(object):
    STATE_READY = 0
    STATE_BEGIN = 1
    STATE_CLOSING = 2 # player cannot join ; wait remaining players to finish
    #STATE_RESULT = 3 # wait calculate result
    STATE_END = 3

    def __init__(self, campaign_id, begin_datetime, closing_datetime, end_datetime):
        self.campaign_id = campaign_id
        self.begin_datetime = begin_datetime
        self.closing_datetime = closing_datetime
        self.end_datetime = end_datetime
        assert(self.end_datetime > self.closing_datetime)
        assert(self.closing_datetime > self.begin_datetime)

    def get_state(self, dt=None):
        if dt == None:
            dt = datetime.datetime.now()
        
        if dt < self.begin_datetime:
            return Campaign.STATE_READY
        elif dt < self.closing_datetime:
            return Campaign.STATE_BEGIN
        elif dt < self.end_datetime:
            return Campaign.STATE_CLOSING
        else:
            return Campaign.STATE_END

    def get_campaign_id(self):
        return self.campaign_id

    def is_active(self, dt=None):
        return self.get_state(dt) == Campaign.STATE_BEGIN

    def __str__(self):
        return 'campaign_id:{},begin:{},close:{},end:{}'.format(
            self.campaign_id, self.begin_datetime, self.closing_datetime, self.end_datetime)

    def __repr__(self):
        return ''.format({
            'campaign_id':self.campaign_id,
            'begin_datetime':self.begin_datetime,
            'closing_datetime':self.closing_datetime,
            'end_datetime':self.end_datetime,
        })

# run in cron server
class CampaignScheduler(object):
    EVENT_CREATE_CAMPAIGN = 0
    EVENT_RESOLVE_CAMPAIGN = 1

    def __init__(self, logger, db):
        self.logger = logger
        self.col_campaign = db['Campaign']
        self.col_cfg = db['CampaignConfig']
        #!!TODO: config reload
        self.cfg = {
            'total_interval': 86400,
            'close_interval': 1800,  # active ~ closing
            'end_interval': 900, # end (resolve) ~ next campaign
            'auto_create': True, # auto create next campaign when current one resolved
        }
        self.col_campaign.create_index([('campaign_id', pymongo.DESCENDING)], unique=True)
        self.col_campaign.create_index([('resolved', pymongo.DESCENDING), ('end_datetime', pymongo.DESCENDING)])
        self.campaign_event_listeners = list()
    
    def register_campaign_event(self, handler):
        self.campaign_event_listeners.append(handler)

    def update(self):
        self.__reload_config()
        self.__process_campaigns()

    def test_resolve_all_campaign(self):
        print "--------Test Resolve All Campaign--------"
        cursor = self.col_campaign.find({'resolved':0})
        docs = [i for i in cursor]
        for i in docs:
            self.__resolve_campaign(i['campaign_id'])

    def __create_campaign(self):
        # get last end campaign's data
        cursor = self.col_campaign.find({'resolved':1}).limit(1)
        temp_data = [i for i in cursor]
        if len(temp_data) > 0:
            b_dt = self.__get_datetime_ceiling(temp_data[0]['end_datetime'], 'day')
            now_day = self.__get_datetime_ceiling(datetime.datetime.now(), 'day')
            # protection: in case now time much greater than last end_datetime, new campaign opens and closed immediately 
            # (when you does not launch scheduler for a long time ...)
            if now_day > b_dt:
                b_dt = now_day
        else:
            b_dt = self.__get_datetime_floor(datetime.datetime.now(), 'day')

        if self.cfg['close_interval'] < self.cfg['end_interval']:
            self.logger.error('[CampaignScheduler] error! closing time less than resolve time!{},{}'.format(
                self.cfg['close_interval'], self.cfg['end_interval']))
            return

        c_dt = b_dt + timedelta(seconds=self.cfg['total_interval']) - timedelta(seconds=self.cfg['close_interval'])
        e_dt = b_dt + timedelta(seconds=self.cfg['total_interval']) - timedelta(seconds=self.cfg['end_interval'])
        cid = self.__get_datetime_representation(b_dt)
        campaign_data = {
            'campaign_id':cid,
            'begin_datetime':b_dt,
            'closing_datetime':c_dt,
            'end_datetime':e_dt,
            'resolved':0,
        }
        self.col_campaign.insert(campaign_data)
        campaign_object = Campaign(cid, b_dt, c_dt, e_dt)
        self.__notify_event(CampaignScheduler.EVENT_CREATE_CAMPAIGN, campaign_object)
        self.logger.info('[CampaignScheduler] create new campaign:{}'.format(campaign_data))
        return True

    def __notify_event(self, event_type, data):
        for handler in self.campaign_event_listeners:
            handler(event_type, data)

    def __get_datetime_representation(self, dt):
        r = '%04d%02d%02d%02d%02d%02d' %(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return r
    
    def __get_datetime_ceiling(self, base_t, mask):
        if mask == 'day':
            new_dt = base_t + timedelta(days=1)
        elif mask == 'hour':
            new_dt = base_t + timedelta(hours=1)
        elif mask == 'minute':
            new_dt = base_t + timedelta(minutes=1)
        else:
            raise Exception('[CampaignScheduler] unsupported mask!{}'.format(mask))
        
        return self.__get_datetime_floor(new_dt, mask)

    def __get_datetime_floor(self, base_t, mask):
        if mask == 'day':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=0,minute=0,second=0)
        elif mask == 'hour':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=base_t.hour,minute=0,second=0)
        elif mask == 'minute':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=base_t.hour,minute=base_t.minute,second=0)
        else:
            raise Exception('[CampaignScheduler] unsupported mask!{}'.format(mask))        
        return new_dt

    def __reload_config(self):
        try:
            doc = self.col_cfg.find_one({}, {'_id':False})
            if doc != None:
                self.cfg = doc
        except:
            self.logger.error('[CampaignScheduler] reload_config err!{}'.format(traceback.format_exc()))

    def __resolve_campaign(self, campaign_id):
        query = {'campaign_id': campaign_id, 'resolved':0 }
        op = {'$set':{'resolved':1}}
        r = self.col_campaign.find_and_modify(query, op, upsert=False, new=True)
        if r != None:
            self.logger.info('[CampaignScheduler] campaign resolved:id={}'.format(campaign_id))
            campaign_object = Campaign(r['campaign_id'], r['begin_datetime'], r['closing_datetime'], r['end_datetime'])
            self.__notify_event(CampaignScheduler.EVENT_RESOLVE_CAMPAIGN, campaign_object)
        else:
            self.logger.error('[CampaignScheduler] resolve failed!{}'.format(campaign_id))

    def __process_campaigns(self):
        try:
            temp_data = [i for i in self.col_campaign.find({'resolved':0})]
            current_campaigns = sorted(temp_data, key=lambda doc:doc['begin_datetime'], reverse=False)

            if len(current_campaigns) == 0 and self.cfg['auto_create'] is True:
                self.__create_campaign()
                return

            for doc in current_campaigns:
                campaign = Campaign(doc['campaign_id'], doc['begin_datetime'], doc['closing_datetime'], doc['end_datetime'])
                state = campaign.get_state()
                campaign_id = campaign.get_campaign_id()
                if state == Campaign.STATE_END:
                    self.logger.info('[CampaignScheduler] campaign ends: resolving document:{}'.format(campaign_id))
                    self.__resolve_campaign(campaign_id)
        except:
            self.logger.error('[CampaignScheduler] update error!{}'.format(traceback.format_exc()))


# create in cron server
class CampaignReader(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.col_campaign = db['Campaign']
        self.current_campaign = None
        self.update()

    def get_active_campaign(self):
        if self.current_campaign != None and self.current_campaign.is_active():
            return self.current_campaign
        return None

    def update(self):
        if self.get_active_campaign() != None:
            return

        try:
            now = datetime.datetime.now()
            cursor = self.col_campaign.find({'resolved':0}, {'_id':False}) # new campaign only appears when previous campaign is resolved
            for i in cursor:
                if now >= i['begin_datetime'] and now < i['end_datetime']:
                    self.current_campaign = Campaign(i['campaign_id'], i['begin_datetime'], i['closing_datetime'], i['end_datetime'])
                    break
        except:
            self.logger.error('[CampaignReader] reload err!{}'.format(traceback.format_exc()))
            

class Score(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db
        self.col_score = db['Score']
        self.col_score.create_index([('level', pymongo.DESCENDING), ('group', pymongo.DESCENDING)], unique=True)
    
    def init_group_score(self, level, group, data):
        '''
        data: {
            '10000001':{'score':0, 'last_update_timestamp':0},
            '10000002':{'score':0, 'last_update_timestamp':0},
            '10000003':{'score':0, 'last_update_timestamp':0},
        }
        '''
        if not isinstance(data, dict):
            self.logger.error('[Score] error init_group_score format!{}'.format(type(data)))
            return
        try:
            query = {'level':level, 'group':group}
            op = {'$set':{'player_data':data } }
            self.col_score.find_and_modify(query, op, upsert=True)
        except:
            self.logger.error('[{}]err!level={},group={},data={}, cs={}'.format(
                self.__class__.__name__, level, group, data, traceback.format_exc()))
            return None
    
    def get_all_scores(self, rd_pfr=pymongo.ReadPreference.PRIMARY):
        cursor = self.col_score.find({}, {'_id':False, 'level':True, 'group':True})
        group_info = [doc for doc in cursor]
        rtn = {}
        for doc in group_info:
            level = doc['level']
            group = doc['group']
            data = self.get_group_score(level, group, rd_pfr=rd_pfr)
            if data == None:
                self.logger.error('[Score] get all scores failed! terminate here')
                return {}
            if level not in rtn:
                rtn[level] = list()
            rtn[level].append(data)
            #rtn.append(data)
        return rtn

    def get_group_score(self, level, group, rd_pfr=pymongo.ReadPreference.SECONDARY_PREFERRED):
        try:
            r = self.col_score.find_one({'level':level, 'group':group}, {'_id':False}, read_preference=rd_pfr)
            if r != None:
                return r['player_data']
        except:
            self.logger.error('[{}]err!level={},group={},cs={}'.format(
                self.__class__.__name__, level, group, traceback.format_exc()))
            return None

    #def add_score(self, campaign_id, ark_id, level, group, score):
    def add_player_score(self, ark_id, level, group, score):
        if score < 0 or not isinstance(score, int):
            self.logger.error('[{}]err!ark_id={},level={},group={},score={}'.format(
                self.__class__.__name__, ark_id, level, group, score))
            return False
        
        try:
            query = {'level':level, 'group':group}
            key1 = 'player_data.{}.score'.format(ark_id)
            key2 = 'player_data.{}.last_update_timestamp'.format(ark_id)
            ts = int(time.time())
            op = {'$inc':{key1: score }, '$set':{key2:ts}}
            r = self.col_score.find_and_modify(query, op, upsert=True, new=True)
            return True
        except:
            self.logger.error('[{}]err!ark_id={},level={},group={},score={},cs={}'.format(
                self.__class__.__name__, ark_id, level, group, score,traceback.format_exc()))
            return False

#!!TODO: put in user info
class Level(object):
    BEGINNER1 = 1
    BEGINNER2 = 2
    BEGINNER3 = 3
    ROOKIE1 = 4
    ROOKIE2 = 5
    ROOKIE3 = 6
    PROFESSIONAL1 = 7
    PROFESSIONAL2 = 8
    PROFESSIONAL3 = 9
    EXPERT1 = 10
    EXPERT2 = 11
    EXPERT3 = 12
    MASTER1 = 13
    MASTER2 = 14
    MASTER3 = 15
    MAX = 15

    def __init__(self, logger, db):
        self.logger = logger
        self.col_level = db['Level']
        self.col_level.create_index([('ark_id', pymongo.DESCENDING)], unique=True)

    def get_level(self, ark_id):
        try:
            doc = self.col_level.find_one({'ark_id':ark_id}, {'_id':False })
            if doc != None:
                return True, doc
            return True, None
        except:
            self.logger.error('[Level] get level err! ark_id={},cs={}'.format(ark_id, traceback.format_exc()))
            return False, None

    def level_up(self, ark_id):
        try:
            query = {'ark_id': ark_id, 'level':{'$lt': Level.MAX}}
            op = {'$inc':{'level':1}}
            r = self.col_level.find_and_modify(query, op, new=True, upsert=True)
            return r
        except:
            self.logger.error('[Level] err! ark_id={},cs={}'.format(ark_id, traceback.format_exc()))
            return None

    def init_level(self, ark_id, group):
        try:
            doc = {'level':Level.BEGINNER1, 'ark_id': ark_id, 'group': group}
            self.col_level.insert(doc, manipulate=False)
            return doc
        except:
            self.logger.error('[Level] err! ark_id={},cs={}'.format(ark_id, traceback.format_exc()))
            return None

#!! TODO : rule for master degree
class GroupDispatcher(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.GROUP_SIZE = 100
        self.col_dispatch = db['GroupDispatchInfo']
        self.col_dispatch.create_index([('level', pymongo.DESCENDING)], unique=True)
    
    def resize_group(self, level, size):
        query = {'level':level}
        op = {'$set':{'counter':size}}
        try:
            self.col_dispatch.find_and_modify(query, op)
        except:
            self.logger.error('[GroupDispatcher] err! level={},size={},cs={}'.format(level, size, traceback.format_exc()))

    def diff_group(self, level, counter):
        query = {'level':level}
        op = {'$inc':{'counter': counter}}
        try:
            self.col_dispatch.find_and_modify(query, op, new=False, upsert=True)
            return True
        except:
            self.logger.error('[GroupDispatcher] err! level={},cnt={},cs={}'.format(level, counter, traceback.format_exc()))
        return False

    def dispatch_group(self, level):
        query = {'level':level}
        op = {'$inc':{'counter':1}}
        try:
            r = self.col_dispatch.find_and_modify(query, op, new=False, upsert=True)
            if r == None: # first time
                group = 0
            else:
                group = int(r['counter']/self.GROUP_SIZE)
            return group
        except:
            self.logger.error('[GroupDispatcher] err! level={},cs={}'.format(level, traceback.format_exc()))
        return None

class RankReArranger(object):
    @staticmethod
    def resolve_ranking(level, group, group_data_list):
        '''
        group_data_list:{
            '10000001':{'score':0, 'last_timestamp': },
            '10000002':{'score':0, 'last_timestamp': },
        }
        '''
        # select top N / Buttom N percent
        '''
        #!!TODO
        # if level == master ...
        group_max = 100
        upgrade_max = 10
        downgrde_max = 10
        middle = group_max - upgrade_max - downgrde_max

        up_count = 0
        down_count = 0
        player_count = len(sorted_score_list)
        remainings = player_count

        if player_count <= upgrade_max:
            up_count = player_count
            down_count = 0
            remainings = 0
        else:
            up_count = upgrade_max
            remainings = player_count - up_count

            if remainings <= middle:
                down_count = 0
            else:
                remainings -= middle
                down_count = remainings

        return {
            'upgrade': sorted_score_list[:up_count],
            'downgrade':sorted_score_list[:downgrade],
        }
        '''
        return {
            'upgrade':[],
            'downgrade':[],
        }


# this runs in scheduler server
class RankCron(object):
    def __init__(self, logger , db):
        self.UPDATE_TIME = 5
        self.logger = logger
        self.db = db
        self.level = Level(logger, db)
        self.score = Score(logger, db)
        self.scheduler = CampaignScheduler(logger, db)
        self.scheduler.register_campaign_event(self.on_campaign_event)
        self.ap_scheduler = GeventScheduler()

    def init_modules(self):
        self.scheduler.update() # load first config
        self.ap_scheduler.add_job(self.scheduler.update, trigger='interval', seconds=self.UPDATE_TIME)
        self.ap_scheduler.start()

    def on_campaign_event(self, event_type, campaign_object):
        if event_type == CampaignScheduler.EVENT_CREATE_CAMPAIGN:
            pass
        elif event_type == CampaignScheduler.EVENT_RESOLVE_CAMPAIGN:
            self.resolve_campaign(campaign_object.get_campaign_id())

    def resolve_campaign(self, campaign_id):
        all_scores = self.score.get_all_scores()
        print "AllScore:", all_scores

class RankGame(object):
    def __init__(self, logger, db):
        self.UPDATE_TIME = 5
        self.logger = logger
        self.db = db
        self.level = Level(logger, db)
        self.score = Score(logger, db)
        self.dispatcher = GroupDispatcher(logger, db)
        self.campaign_reader = CampaignReader(logger, db)
        self.ap_scheduler = GeventScheduler()
        self.init_modules()
        
    def init_modules(self):
        self.campaign_reader.update() # load first config
        self.ap_scheduler.add_job(self.campaign_reader.update, trigger='interval', seconds=self.UPDATE_TIME)
        self.ap_scheduler.start()
    
    def get_scheduler(self):
        return self.scheduler

    def get_campaign_reader(self):
        return self.campaign_reader

    def get_score_module(self):
        return self.score

    def get_level_module(self):
        return self.level

    def add_score(self, ark_id, score):
        campaign = self.campaign_reader.get_active_campaign()
        if campaign is None:
            self.logger.debug('[RankManager] no campaign! skip adding score:id={},score={}'.format(ark_id, score))
            return

        ok, rank_info = self.level.get_level(ark_id)
        if not ok:
            return
        
        if rank_info == None:
            group = self.dispatcher.dispatch_group(Level.BEGINNER1)
            rank_info = self.level.init_level(ark_id, group)
            if rank_info == None:
                self.dispatcher.diff_group(Level.BEGINNER1, -1) # rollback
                self.logger.error('[RankService] fail to add score!ark_id:{},score:{}'.format(ark_id, score))
                return
        
        level = rank_info['level']
        group = rank_info['group']
        self.score.add_player_score(ark_id, level, group, score)
