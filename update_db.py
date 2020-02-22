# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:13:20 2020

@author: sqr_p
"""

import pymongo
from MaterialPlanning import MaterialPlanning
from bson.decimal128 import Decimal128
import time
from dateutil import parser
from utils import required_dct, owned_dct

print('正在更新数据库...')
dbclient = pymongo.MongoClient('SERVER')
db = dbclient['Arknights_OneGraph']

db_Material, db_Event= db['Material'], db['Material_Event']
Event_Stages = []
update_time = parser.parse(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))

def update_collection(collection):
    print('正在更新数据库' + str(collection.name))
    for item in collection.find():
        if 'credit_store_value' in item:
            if item['name'] in mp.best_stage:
                collection.update_one({'_id': item['_id']},
                    {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                              'Notes': mp.Notes[item['name']],
                              'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                              'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                              'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                              'last_updated': update_time}
                    })
            else:
                collection.update_one({'_id': item['_id']},
                    {'$set': {'credit_store_value': Decimal128('%.3f'%(100*mp.creditEffect[item['name']])),
                              'Notes': mp.Notes[item['name']],
                              'lowest_ap_stages': [{}],
                              'balanced_stages': [{}],
                              'drop_rate_first_stages': [{}],
                              'last_updated': update_time}
                    })
        if 'green_ticket_value' in item:
            if item['name'] in mp.best_stage:
                collection.update_one({'_id': item['_id']},
                    {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                              'Notes': mp.Notes[item['name']],
                              'lowest_ap_stages': mp.best_stage[item['name']]['lowest_ap_stages'],
                              'balanced_stages': mp.best_stage[item['name']]['balanced_stages'],
                              'drop_rate_first_stages': mp.best_stage[item['name']]['drop_rate_first_stages'],
                              'last_updated': update_time}})
            else:
                collection.update_one({'_id': item['_id']},
                    {'$set': {'green_ticket_value': Decimal128('%.3f'%(mp.greenTickets[item['name']])),
                              'Notes': mp.Notes[item['name']],
                              'lowest_ap_stages': [{}],
                              'balanced_stages': [{}],
                              'drop_rate_first_stages': [{}],
                              'last_updated': update_time}})
        if 'golden_ticket_value' in item:
            collection.update_one({'_id': item['_id']},
                    {'$set': {'golden_ticket_value': Decimal128('%.3f'%(mp.yellowTickets[item['name']])),
                              'Notes': mp.Notes[item['name']],
                              'last_updated': update_time}})

    print(str(collection.name)+'更新完成.')

mp = MaterialPlanning(filter_stages=['S4-4', 'S6-4'],
                      filter_freq=100,
                      update=True,
                      printSetting='0000110010'
                      )
mp.get_plan(required_dct, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
[mp.output_best_stage(x) for x in '123']
if Event_Stages:
    # 如果活动开放, 就先更新带活动关卡的, 再更新正常关卡
    # 如果活动不开放, 上面算的就是正常关卡
    update_collection(db_Event)
    mp = MaterialPlanning(filter_stages=['S4-4', 'S6-4'] + Event_Stages,
                      filter_freq=100,
                      update=False,
                      printSetting='0000110010',
                      )
    mp.get_plan(required_dct, owned_dct, print_output=False, outcome=True,
                                  gold_demand=True, exp_demand=True)
update_collection(db_Material)
