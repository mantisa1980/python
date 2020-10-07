import time
import datetime
from datetime import timedelta
import traceback
import pymongo
import sys

'''
# when calculating results, players are blocked from playing to avoid ranking race condition and ambiguity

#### score mongodb schema

# always only one document
RankCampaign
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

#TODO: drop CampaignScore and recreate index once calculate finish.
#TODO: after adding score , if no group, dispatch one
RankScore:
{
    campaign_id
    ark_id
    last_update_ts
    score
    level
    group
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
RankInfo
{
    ark_id
    level
    group
}
index: ark_id

'''


class RankCampaign(object):
    STATE_READY = 0
    STATE_BEGIN = 1
    STATE_CLOSING = 2 # player cannot join ; wait remaining players to finish
    #STATE_RESULT = 3 # wait calculate result
    STATE_END = 3
    WAIT_DRAINING_MINUTES = 30

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
            return RankCampaign.STATE_READY
        elif dt < self.closing_datetime:
            return RankCampaign.STATE_BEGIN
        elif dt < self.end_datetime:
            return RankCampaign.STATE_CLOSING
        else:
            return RankCampaign.STATE_END

    def get_campaign_id(self):
        return self.campaign_id

    def is_active(self, dt=None):
        return self.get_state(dt) == RankCampaign.STATE_BEGIN

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

# campaign state: 
class RankCampaignScheduler(object):
    EVENT_CREATE_CAMPAIGN = 0
    EVENT_RESOLVE_CAMPAIGN = 1

    def __init__(self, logger, db):
        self.logger = logger
        self.col_campaign = db['RankCampaign']
        #!!TODO: config reload
        self.cfg = {
            'active_interval':86400 - 3600,
            'closing_interval':1800, # disable join game, wait remaing players to finish
        }
        self.col_campaign.create_index([('campaign_id', pymongo.DESCENDING)], unique=True)
        self.col_campaign.create_index([('resolved', pymongo.DESCENDING), ('end_datetime', pymongo.DESCENDING)])
        self.campaign_event_listeners = list()
    
    def register_campaign_event(self, handler):
        self.campaign_event_listeners.append(handler)

    def _create_campaign(self):
        # get last end campaign's data
        cursor = self.col_campaign.find({'resolved':1}).limit(1)
        temp_data = [i for i in cursor]
        if len(temp_data) > 0:
            b_dt = self.get_datetime_ceiling(temp_data[0]['end_datetime'], 'day')
            now_day = self.get_datetime_ceiling(datetime.datetime.now(), 'day')
            # protection: in case now time much greater than last end_datetime, new campaign opens and closed immediately 
            # (when you does not launch scheduler for a long time ...)
            if now_day > b_dt:
                b_dt = now_day
        else:
            b_dt = self.get_datetime_floor(datetime.datetime.now(), 'day')

        c_dt = b_dt + timedelta(seconds=self.cfg['active_interval'])
        e_dt = c_dt + timedelta(seconds=self.cfg['closing_interval'])
        cid = self.get_datetime_representation(b_dt)
        campaign_data = {
            'campaign_id':cid,
            'begin_datetime':b_dt,
            'closing_datetime':c_dt,
            'end_datetime':e_dt,
            'resolved':0,
        }
        self.col_campaign.insert(campaign_data)
        campaign_object = RankCampaign(cid, b_dt, c_dt, e_dt)
        self.notify_event(RankCampaignScheduler.EVENT_CREATE_CAMPAIGN, campaign_object)
        self.logger.info('[RankCampaignScheduler] create new campaign:{}'.format(campaign_data))
        return True

    def notify_event(self, event_type, data):
        for handler in self.campaign_event_listeners:
            handler(event_type, data)

    def update(self):
        self._process_campaigns()

    def get_datetime_representation(self, dt):
        r = '%04d%02d%02d%02d%02d%02d' %(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return r
    
    def get_datetime_ceiling(self, base_t, mask):
        if mask == 'day':
            new_dt = base_t + timedelta(days=1)
        elif mask == 'hour':
            new_dt = base_t + timedelta(hours=1)
        elif mask == 'minute':
            new_dt = base_t + timedelta(minutes=1)
        else:
            raise Exception('[RankCampaignScheduler] unsupported mask!{}'.format(mask))
        
        return self.get_datetime_floor(new_dt, mask)

    def get_datetime_floor(self, base_t, mask):
        if mask == 'day':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=0,minute=0,second=0)
        elif mask == 'hour':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=base_t.hour,minute=0,second=0)
        elif mask == 'minute':
            new_dt = datetime.datetime(year=base_t.year,month=base_t.month,day=base_t.day,hour=base_t.hour,minute=base_t.minute,second=0)
        else:
            raise Exception('[RankCampaignScheduler] unsupported mask!{}'.format(mask))
        
        return new_dt

    def _resolve_campaign(self, campaign_id):
        query = {'campaign_id': campaign_id, 'resolved':0 }
        op = {'$set':{'resolved':1}}
        r = self.col_campaign.find_and_modify(query, op, upsert=False, new=True)
        if r != None:
            self.logger.info('[RankCampaignScheduler] campaign resolved:id={}'.format(campaign_id))
            campaign_object = RankCampaign(r['campaign_id'], r['begin_datetime'], r['closing_datetime'], r['end_datetime'])
            self.notify_event(RankCampaignScheduler.EVENT_RESOLVE_CAMPAIGN, campaign_object)
        else:
            self.logger.error('[RankCampaignScheduler] resolve failed!{}'.format(campaign_id))

    def _process_campaigns(self):
        try:
            temp_data = [i for i in self.col_campaign.find({'resolved':0})]
            current_campaigns = sorted(temp_data, key=lambda doc:doc['begin_datetime'], reverse=False)

            if len(current_campaigns) == 0:
                self._create_campaign()
                return

            for doc in current_campaigns:
                rc = RankCampaign(doc['campaign_id'], doc['begin_datetime'], doc['closing_datetime'], doc['end_datetime'])
                state = rc.get_state()
                campaign_id = rc.get_campaign_id()
                if state == RankCampaign.STATE_END:
                    self.logger.info('[RankCampaignScheduler] campaign ends: resolving document:{}'.format(campaign_id))
                    self._resolve_campaign(campaign_id)
        except:
            self.logger.error('[RankCampaignScheduler] update error!{}'.format(traceback.format_exc()))

    def test_resolve_all_campaign(self):
        cursor = self.col_campaign.find({'resolved':0})
        docs = [i for i in cursor]
        for i in docs:
            self._resolve_campaign(i['campaign_id'])

# create in cron server
class RankCampaignReader(object):
    def __init__(self, logger, db):
        self.logger = logger
        #self.col = db['RankCampaign']
        self.active_campaign = None
        self.reload()

    def get_active_campaign(self):
        return self.active_campaign

    def reload(self):
        #!!TODO load from mongodb
        pass

##!!TODO legacy collection cleaner
class RankScoreBank(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db

    def init_campaign_index(self, campaign_id):
        col = self.__get_score_col(campaign_id)
        col.create_index([('ark_id', pymongo.DESCENDING)])
        col.create_index([('score', pymongo.DESCENDING), ('last_update_time', pymongo.DESCENDING), ('ark_id', pymongo.DESCENDING)])
    
    def get_score(self, campaign_id, ark_id):
        col = self.__get_score_col(campaign_id)
        try:
            r = col.find_one({'ark_id':ark_id }, read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED)
            return r
        except:
            self.logger.error('[{}]err!campaign={},ark_id={},cs={}'.format(
                self.__class__.__name__, campaign_id, ark_id, traceback.format_exc()))
            return None

    def get_campaign_score(self, campaign_id, direction, limit=None):
        col = self.__get_score_col(campaign_id)
        total_count = col.count()
        upgrade_set = set()
        downgrade_set = set()
        lst = list()

        if direction == 'top':
            sorting = pymongo.DESCENDING
        elif direction == 'buttom':
            sorting = pymongo.AESCENDING

        batch_size = 5000
        current_count = 0

        if limit == None:
            while True:
                iteration_counter = 0
                cursor = col.find({'score':{'$gte:0'}}, {'_id':False}).sort([('score', sorting)]).skip(current_count).limit(batch_size)
                for i in cursor:
                    lst.append(i)
                    iteration_counter +=1
                if iteration_counter == 0:
                    break
                else:
                    current_count += batch_size
        else:
            while current_counter < limit:
                remain = limit - current_counter
                if remain < batch_size:
                    batch_size = remain

                cursor = col.find({'score':{'$gte':0}}, {'_id':False}).sort([('score', sorting)]).skip(current_count).limit(batch_size)
                for i in cursor:
                    lst.append(i)
                current_count += batch_size

    def __get_score_col(self, campaign_id):
        return self.db['RankScore_{}'.format(campaign_id)]

    #def add_score(self, campaign_id, ark_id, level, group, score):
    def add_score(self, campaign_id, ark_id, score):
        col = self.__get_score_col(campaign_id)
        query = {'ark_id':ark_id }
        op = {'$inc':{'score': score}}
        r = col.find_and_modify(query, op, upsert=True, new=True)
        return r

class RankAssigner(object):
    def __init__(self, logger, db, namespace):
        self.logger = logger
        self.namespace = namespace
        rank_col_name = '{}Rank'.format(namespace)
        group_col_name = '{}Group'.format(namespace)

        self.col_rank = db[rank_col_name]
        self.col_group = db[group_col_name]
        self.col_rank.create_index([('ark_id', pymongo.DESCENDING)], unique=True)

    def get_rank_data(self, ark_id):
        try:
            doc = self.col_rank.find_one({'ark_id':ark_id}, {'_id':False })
            if doc != None:
                return doc
            return None
        except:
            self.logger.error('[RankAssigner({})] err! ark_id={},cs={}'.format(self.namespace, ark_id, traceback.format_exc()))
            return None
        
    def init_rank_data(self, ark_id):
        try:
            doc = {'group':1, 'level':1, 'ark_id': str(ark_id) }
            self.col_rank.insert(doc, manipulate=False)
        except:
            self.logger.error('[RankAssigner({})] err! ark_id={},cs={}'.format(self.namespace, ark_id, traceback.format_exc()))
    
    def dispatch_newbie_group(self):
        pass

    def rank(self, level, sorted_score_list):
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

class RankReArranger(object):
    @staticmethod
    def resolve_ranking(level, group, data_list):
        # select top N / Buttom N percent

        return {
            'upgrade':[]
            'downgrade':[]
        }

class RankManager(object):
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db
        self.assigner = RankAssigner(self.logger, self.db, 'WinRank')
        self.score_bank = RankScoreBank(self.logger, self.db)
        self.campaign_finder = RankCampaignReader(self.logger, self.db)
        self.scheduler = RankCampaignScheduler(self.logger, self.db)
        self.init_campaign_event_handlers()
    
    def init_campaign_event_handlers(self):
        self.scheduler.register_campaign_event(self.on_campaign_event)

    def on_campaign_event(self, event_type, data):
        if event_type == RankCampaignScheduler.EVENT_CREATE_CAMPAIGN:
            campaign_id = data.get_campaign_id()
            self.score_bank.init_campaign_index(campaign_id)
    
    def add_score(self, ark_id, score):
        rank_info = self.rank_assigner.get_rank(ark_id)
        if rank_info == None:
            rank_info = self.rank_assigner.init_rank(ark_id)
            if rank_info == None:
                self.logger.error('[RankService] fail to add score!ark_id:{},score:{}'.format(ark_id, score))    
        #campaign_id = self.

        level = rank_info['level']
        group = rank_info['group']
        campaign = self.campaign_finder.get_active_campaign()
        if campaign is None:
            print "Campaign is None, cannot play"
            return

        campaign_id = campaign.get_campaign_id()
        self.score_accumolator.add_score(campaign_id, ark_id, level, group, score)
    