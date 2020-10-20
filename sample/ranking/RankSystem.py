#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import datetime
from datetime import timedelta
import traceback
import pymongo
import sys
import gevent
import math
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
    group: # created when adding score; updated when resolved.
}

Score
{
    campaign_id
    level:0,
    group: 0,
    player_data:{
        '$uid':{
            'score':0,
            'last_update_timestamp':
        }
    }
}

# only for level 1 new users
GroupDispatchInfo {
    level:
    counter:
}

RankResultLog
{
    CampaignID
    UserID
    FromRankGroup
    ToRankGroup
    FromRankLevel
    ToRankLevel 
}

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
    STATE_END = 3

    def __init__(self, campaign_id, begin_datetime, closing_datetime, end_datetime, upgrade_ratio, downgrade_ratio, group_max):
        self.campaign_id = campaign_id
        self.begin_datetime = begin_datetime
        self.closing_datetime = closing_datetime
        self.end_datetime = end_datetime
        self.upgrade_ratio = upgrade_ratio
        self.downgrade_ratio = downgrade_ratio
        self.group_max = group_max
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

    def get_group_max(self):
        return self.group_max

    def get_campaign_id(self):
        return self.campaign_id
    
    def __get_abs_diff_time(self, dt1, dt2):
        if dt1 >= dt2:
            return (dt1 - dt2).seconds
        else:
            return (dt2 - dt1).seconds

    def get_time_to_begin(self):
        return self.__get_abs_diff_time(self.begin_datetime, datetime.datetime.now())

    def get_time_to_closing(self):
        return self.__get_abs_diff_time(self.closing_datetime, datetime.datetime.now())

    def get_time_to_end(self):
        return self.__get_abs_diff_time(self.end_datetime, datetime.datetime.now())

    def is_active(self, dt=None):
        return self.get_state(dt) == Campaign.STATE_BEGIN

    def is_closing(self, dt=None):
        return self.get_state(dt) == Campaign.STATE_CLOSING

    def is_ended(self, dt=None):
        return self.get_state(dt) == Campaign.STATE_END

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
    INTERVAL_UNIT = 'day'

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
            'upgrade_ratio':0.3,
            'downgrade_ratio':0.1,
            'group_max':100,
        }
        self.col_campaign.create_index([('campaign_id', pymongo.DESCENDING)], unique=True)
        self.col_campaign.create_index([('resolved', pymongo.DESCENDING), ('end_datetime', pymongo.DESCENDING)])
        self.campaign_event_listeners = list()
        self.__reload_config()
    
    def register_campaign_event(self, handler):
        self.campaign_event_listeners.append(handler)

    def _update(self):
        self.__reload_config()
        self.__process_campaigns()

    def __create_campaign(self):
        # get last ended campaign's data
        cursor = self.col_campaign.find({'resolved':1}).limit(1)
        t = [i for i in cursor]
        if len(t) > 0:
            self.logger.info('[CampaignScheduler]create campaign based on last campaign:id={},endtime={}'.format(
                t[0]['campaign_id'], t[0]['end_datetime']))
            b_dt = self.__get_datetime_ceiling(t[0]['end_datetime'], CampaignScheduler.INTERVAL_UNIT)
            now_day = self.__get_datetime_ceiling(datetime.datetime.now(), CampaignScheduler.INTERVAL_UNIT)
            # protection: in case now time much greater than last end_datetime, new campaign opens and closed immediately 
            # (when you does not launch scheduler for a long time ...)
            if now_day > b_dt:
                b_dt = now_day
        else:
            b_dt = self.__get_datetime_floor(datetime.datetime.now(), CampaignScheduler.INTERVAL_UNIT) # open right now

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
            'upgrade_ratio':self.cfg['upgrade_ratio'],
            'downgrade_ratio':self.cfg['downgrade_ratio'],
            'group_max':self.cfg['group_max'],
            'resolved':0,
        }
        self.col_campaign.insert(campaign_data)
        self.__notify_event(CampaignScheduler.EVENT_CREATE_CAMPAIGN, cid)
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
            self.__notify_event(CampaignScheduler.EVENT_RESOLVE_CAMPAIGN, r['campaign_id'])
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
                campaign = Campaign(i['campaign_id'], 
                                    i['begin_datetime'],
                                    i['closing_datetime'],
                                    i['end_datetime'],
                                    i['upgrade_ratio'],
                                    i['downgrade_ratio'],
                                    i['group_max'] )

                state = campaign.get_state()
                campaign_id = campaign.get_campaign_id()
                if state == Campaign.STATE_END:
                    self.logger.info('[CampaignScheduler] campaign ends: resolving document:{}'.format(campaign_id))
                    self.__resolve_campaign(campaign_id)
        except:
            self.logger.error('[CampaignScheduler] update error!{}'.format(traceback.format_exc()))

    def test_resolve_all_campaign(self):
        print "--------test resolve all campaign--------"
        cursor = self.col_campaign.find({'resolved':0})
        docs = [i for i in cursor]
        for i in docs:
            self.__resolve_campaign(i['campaign_id'])

# create in cron server
class CampaignReader(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.col_campaign = db['Campaign']
        self.current_campaign = None
        self.reload()

    def get_current_campaign(self):
        if self.current_campaign != None:
            return self.current_campaign
        return None
    
    def __get_non_ending_campaign(self): # for readers
        if self.current_campaign == None:
            return None

        if self.current_campaign.is_ended():
            return None
        return self.current_campaign

    def get_active_campaign(self): # for general users
        if self.current_campaign != None and self.current_campaign.is_active():
            return self.current_campaign
        return None

    def reload(self):
        if self.__get_non_ending_campaign() != None:
            return

        try:
            now = datetime.datetime.now()
            cursor = self.col_campaign.find({'resolved':0}, {'_id':False}) # new campaign only appears when previous campaign is resolved
            for i in cursor:
                #if now >= i['begin_datetime'] and now < i['end_datetime']:
                self.current_campaign = Campaign(i['campaign_id'], 
                                                 i['begin_datetime'],
                                                 i['closing_datetime'],
                                                 i['end_datetime'],
                                                 i['upgrade_ratio'],
                                                 i['downgrade_ratio'],
                                                 i['group_max'] )
                self.logger.debug('[CampaignReader] New campaign loaded:ID:{},begin:{}, closing:{},ending:{}'.format(
                    self.current_campaign.get_campaign_id(),
                    self.current_campaign.get_time_to_begin(),
                    self.current_campaign.get_time_to_closing(),
                    self.current_campaign.get_time_to_end()))
                break
        except:
            self.logger.error('[CampaignReader] reload err!{}'.format(traceback.format_exc()))
            pass

class Score(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db
        self.col_score = db['Score']
        self.col_score.create_index([('campaign_id', pymongo.DESCENDING), ('level', pymongo.DESCENDING), ('group', pymongo.DESCENDING)], unique=True)
    
    def clear_score(self, campaign_id):
        try:
            r = self.col_score.remove({'campaign_id':campaign_id})
            return r
        except:
            self.logger.error('[{}]err!campaign_id={},cs={}'.format(
                self.__class__.__name__, campaign_id, traceback.format_exc()))
            return None

    def get_all_scores(self, campaign_id, rd_pfr=pymongo.ReadPreference.PRIMARY):
        try:
            cursor = self.col_score.find({'campaign_id':campaign_id}, {'_id':False}, read_preference=rd_pfr)
            group_info = [doc for doc in cursor]
            rtn = {}
            for doc in group_info:
                level = doc['level']
                group = doc['group']
                if level not in rtn:
                    rtn[level] = dict()
                if group not in rtn[level]:
                    rtn[level][group] = {}
                
                rtn[level][group] = doc['player_data']
            return rtn
        except:
             self.logger.error('[{}]err!campaign_id={},cs={}'.format(
                self.__class__.__name__, campaign_id, traceback.format_exc()))
             return None

    def get_group_score(self, campaign_id, level, group, rd_pfr=pymongo.ReadPreference.SECONDARY_PREFERRED):
        try:
            r = self.col_score.find_one({'campaign_id':campaign_id, 'level':level, 'group':group},
                                        {'_id':False},
                                        read_preference=rd_pfr)
            if r != None:
                return r['player_data']
        except:
            self.logger.error('[{}]err!campaign_id={},level={},group={},cs={}'.format(
                self.__class__.__name__, campaign_id, level, group, traceback.format_exc()))
            return None

    #def add_score(self, campaign_id, ark_id, level, group, score):
    def add_player_score(self, campaign_id, ark_id, level, group, score):
        # =0 is allowed (lose)
        if score < 0 or not isinstance(score, int):
            self.logger.error('[{}]err!ark_id={},level={},group={},score={}'.format(
                self.__class__.__name__, ark_id, level, group, score))
            return False
        
        try:
            query = {'campaign_id':campaign_id, 'level':level, 'group':group}
            key1 = 'player_data.{}.score'.format(ark_id)
            key2 = 'player_data.{}.last_update_timestamp'.format(ark_id)
            ts = int(time.time())
            op = {'$inc':{key1: score }, '$set':{key2:ts}}
            r = self.col_score.find_and_modify(query, op, upsert=True, new=True)
            return True
        except:
            self.logger.error('[{}]err!campaign_id={},ark_id={},level={},group={},score={},cs={}'.format(
                self.__class__.__name__, campaign_id, ark_id, level, group, score,traceback.format_exc()))
            return False

## Also Group lookup table for users
class Level(object):
    BEGINNER = 1
    ROOKIE1 = 2
    ROOKIE2 = 3
    ROOKIE3 = 4
    PROFESSIONAL1 = 5
    PROFESSIONAL2 = 6
    PROFESSIONAL3 = 7
    EXPERT1 = 8
    EXPERT2 = 9
    EXPERT3 = 10
    MASTER1 = 11
    MASTER2 = 12
    MASTER3 = 13
    MIN = 1
    MAX = 13

    def __init__(self, logger, db):
        self.logger = logger
        self.col_level = db['Level']
        self.col_level.create_index([('ark_id', pymongo.DESCENDING)], unique=True)

    def set_multi_level(self, ark_id_list, level):
        if level > Level.MAX:
            return

        try:
            query = {'ark_id': {'$in': ark_id_list}}
            op = {'$set':{'level': level}}
            r = self.col_level.update(query, op, multi=True)
            return r
        except:
            self.logger.error('[Level] err!{}'.format(traceback.format_exc()))
            return None

    def get_level(self, ark_id, rd_pfr=pymongo.ReadPreference.SECONDARY_PREFERRED):
        try:
            doc = self.col_level.find_one({'ark_id':ark_id}, {'_id':False},read_preference=rd_pfr)
            if doc != None:
                return True, doc
            return True, None
        except:
            self.logger.error('[Level] get level err! ark_id={},cs={}'.format(ark_id, traceback.format_exc()))
            return False, None

    def reassign_group(self, campaign_id, ark_id, group):
        try:
            query = {'ark_id': ark_id }
            op = {'$set':{ 'last_campaign_id':campaign_id, 'group': group}}
            r = self.col_level.find_and_modify(query, op, new=False, upsert=False)
            if r == None:
                self.logger.error('[Level] reassign_group fail! no initial data!campaign_id={},ark_id={},group={}'.format(
                    campaign_id, ark_id, group))
            return r
        except:
            self.logger.error('[Level] err!campaign_id={},ark_id={},level={},group={},cs={}'.format(
                campaign_id, ark_id, level, group, traceback.format_exc()))
            return None
        pass

    def init_level(self, campaign_id, ark_id, group):
        try:
            doc = {'last_campaign_id':campaign_id, 'level':Level.BEGINNER, 'ark_id': ark_id, 'group': group}
            self.col_level.insert(doc, manipulate=False)
            return doc
        except:
            self.logger.error('[Level] err! ark_id={},cs={}'.format(ark_id, traceback.format_exc()))
            return None

#!! TODO : rule for master degree
class GroupDispatcher(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.col_grp_dispatch = db['GroupDispatch']
        self.col_grp_dispatch.create_index([('campaign_id', pymongo.DESCENDING), ('level', pymongo.DESCENDING)], unique=True)

    def dispatch_group(self, campaign_id, level, group_max):
        query = {'campaign_id':campaign_id, 'level':level}
        op = {'$inc':{'counter':1}}
        try:
            r = self.col_grp_dispatch.find_and_modify(query, op, new=False, upsert=True)
            if r == None: # first time
                group = 0
            else:
                group = int(r['counter']/group_max)
            return group
        except:
            self.logger.error('[GroupDispatcher] err! level={},cs={}'.format(level, traceback.format_exc()))
        return None

    def clear(self, campaign_id):
        query = {'campaign_id':campaign_id}
        try:
            self.col_grp_dispatch.remove(query, multi=True)
        except:
            self.logger.error('[GroupDispatcher] err! campaign_id={},cs={}'.format(campaign_id, traceback.format_exc()))

# this runs in scheduler server
class RankCron(object):
    def __init__(self, logger , db):
        self.UPDATE_TIME = 5
        self.logger = logger
        self.db = db
        self.level = Level(logger, db)
        self.score = Score(logger, db)
        self.dispatcher = GroupDispatcher(logger, db) # only for clear old data
        self.scheduler = CampaignScheduler(logger, db)
        self.scheduler.register_campaign_event(self.on_campaign_event)
        self.ap_scheduler = GeventScheduler()
        self.init_modules()

    def update(self):
        self.scheduler._update()

    def init_modules(self):
        self.ap_scheduler.add_job(self.update, trigger='interval', seconds=self.UPDATE_TIME)
        self.ap_scheduler.start()

    def on_campaign_event(self, event_type, campaign_id):
        if event_type == CampaignScheduler.EVENT_CREATE_CAMPAIGN:
            pass
        elif event_type == CampaignScheduler.EVENT_RESOLVE_CAMPAIGN:
            self.resolve_campaign(campaign_id)

    def resolve_campaign(self, campaign_id):
        '''
        all_data format :
        data: {
            '$level': {
                $group: {
                    $ark_id:{last_update_timestamp:1234567899, score': 100}
                }
            }
        }
        # sample:
        1:{
            0:{
                u'10000002':{u'last_update_timestamp':1602756612, u'score':100 },
                u'10000001':{u'last_update_timestamp':1602756612, u'score':100 }
            },
            1:{
                u'10000003':{u'last_update_timestamp':1602756612, u'score':100 }
            }
        },
        2:{
            0:{
                u'10000004':{u'last_update_timestamp':1602756612, u'score':100 }
            }
        }
        '''

        all_data = self.score.get_all_scores(campaign_id)
        if all_data is None:
            self.logger.error('[RankCron] get all data error! please handle this manually!(resolve award):campaign_id={}'.format(campaign_id))
            return

        for level, group_data in all_data.items():
            for group_id, player_data in group_data.items():
                top_down_users = self.pick_level_change_players(level, player_data)
                self.logger.info('[RankCron]level change list:Campaign={},level={},group={},data={}'.format(
                    campaign_id, level, group_id, top_down_users))
                
                if level < Level.MAX:
                    if len(top_down_users['upgrade']) > 0:
                        user_lst = []
                        for p in top_down_users['upgrade']:
                            user_lst.append(p[0])
                        self.level.set_multi_level(user_lst, level+1)
                
                if level > Level.BEGINNER:
                    if len(top_down_users['downgrade']) > 0:
                        user_lst = []
                        for p in top_down_users['downgrade']:
                            user_lst.append(p[0])
                        self.level.set_multi_level(user_lst, level-1)

                
        ##!!TODO award for upgraders
        print "TODO ------------- Giving campaign resolve awards"
        self.score.clear_score(campaign_id)
        self.dispatcher.clear(campaign_id)

    # player_data format: 
    # {'10000002': {'last_update_timestamp': 1602826256, 'score': 100}, '10000001': {'last_update_timestamp': 1602826256, 'score': 100}}
    def pick_level_change_players(self, level, player_data):
        #!!TODO: level MAX checking flow

        player_count = len(player_data)
        if player_count == 0:
            return {
                'upgrade':[],
                'downgrade':[],
            }

        iter_data = player_data.items()
        # sort by score, last_update_timestamp,ark_id descending
        iter_data.sort(key=lambda elm: (elm[1]['score'], elm[1]['last_update_timestamp'], elm[0]), reverse=True)

        upgrade_ratio = 0.3
        downgrade_ratio = 0.1
        upgrade_max = int(math.ceil(player_count * upgrade_ratio))
        downgrade_max = int(math.floor(player_count * downgrade_ratio))
        middle_max = player_count - upgrade_max - downgrade_max

        up_count = 0
        middle_count = 0
        down_count = 0

        if player_count <= upgrade_max:
            up_count = player_count
        else:
            up_count = upgrade_max
            player_count-=up_count

            if player_count <= middle_max:
                middle_count = player_count
                down_count = 0
            else:
                middle_count = middle_max
                player_count -= middle_max
                down_count = player_count

        return {
            'upgrade':iter_data[:up_count],
            'downgrade':iter_data[up_count+middle_count:],
        }

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
        self.ap_scheduler.add_job(self.update, trigger='interval', seconds=self.UPDATE_TIME)
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
        campaign_object = self.campaign_reader.get_active_campaign()
        if campaign_object is None:
            self.logger.debug('[RankGame] no campaign! skip adding score:id={},score={}'.format(ark_id, score)) #also avoids altering group info when resolving
            return

        campaign_id = campaign_object.get_campaign_id()
        ok, rank_info = self.level.get_level(ark_id, rd_pfr=pymongo.ReadPreference.PRIMARY)
        if not ok:
            self.logger.error('[RankGame] fail to add score!ark_id:{},score:{}'.format(ark_id, score))
            return
        
        if rank_info == None:
            group = self.dispatcher.dispatch_group(campaign_id, Level.BEGINNER, campaign_object.get_group_max()) # create group info in BEGINNER
            if group == None:
                self.logger.error('[RankGame] fail to dispatch new group!ark_id:{},score:{}'.format(ark_id, score))
                return

            rank_info = self.level.init_level(campaign_id, ark_id, group)
            if rank_info == None:
                self.logger.error('[RankGame] fail to init level!ark_id:{},group:{},score:{}'.format(ark_id, group, score))
                return

        level = rank_info['level']
        group = rank_info['group']
        if rank_info['last_campaign_id'] != campaign_id:
            group = self.dispatcher.dispatch_group(campaign_id, level, campaign_object.get_group_max())
            self.level.reassign_group(campaign_id, ark_id, group)
        
        self.score.add_player_score(campaign_id, ark_id, level, group, score)

    def update(self):
        self.campaign_reader.reload()
        pass
