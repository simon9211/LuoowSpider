# -*- coding:utf-8 -*-
import re
import threading
import random
from time import sleep

from urllib.request import urlopen

import pymongo
import ssl

# import db
from spiders import db
from spiders import lib

ssl._create_default_https_context = ssl._create_unverified_context

# client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
# 数据库

# database = client.luoow
# vol表,没有自动创建
# vol_db = database.vols
# tag_db = database.tags
# col_db = db.col


# dblist = client.list_database_names()

print('simon')

def get_home_page():
    url = 'http://www.luoow.com/'
    bsObj = lib.load_page(url)
    # 根据css样式表查找
    # print(bsObj)
    periods = []
    vol_list = bsObj.findAll("span", {"class": "label"})
    for vol in vol_list:
        print(vol.get_text())
        periods.append(vol.get_text())

    t_vols = threading.Thread(target=save_periods_mongo, args=(periods,))
    t_vols.start()

    t_vols1 = threading.Thread(target=get_vol, args=(periods,))
    t_vols1.start()

    labels = []
    tagList = bsObj.findAll("a", {"class": "item"})
    for tag in tagList:
        print(tag.get_text())
        labels.append(tag.get_text())
    t_tags = threading.Thread(target=save_labels_mongo, args=(labels,))
    t_tags.start()


# 创建一个线程锁
lock = threading.Lock()


def get_vol(vols):
    for i in range(0, 4):
        t = threading.Thread(target=get_vol_items, args=(vols,))
        # 启动线程
        t.start()
    # get_vol_items(vols)


def get_vol_items(vols):
    while vols:
        # 加锁
        lock.acquire()
        # 取出第一个元素
        vol = vols[0]
        # 将取出的元素从列表中删除，避免重复加载
        del vols[0]
        # 释放锁
        lock.release()

        url = 'http://www.luoow.com'
        tp = ''
        if vol == '音乐电台':
            tp = '/r/'
        elif vol == '其他':
            tp = '/e/'
        else:
            tp = '/' + vol[4:].replace('-', '_') + '.html'

        url += tp
        idx = random.randint(0, 10)

        bsObj = lib.load_page(url)
        # print(bsObj)
        # sleep(3)
        colList = bsObj.findAll("div", {"class": "thumbnail theborder"})
        cols = []
        for col in colList:
            # print(col)
            item = {}
            a = col.findAll('a')
            item['title'] = a[1].get_text()
            item['href'] = a[1].get('href')
            img = col.find('img')
            item['cover'] = img.get('src')
            cols.append(item)
        t_cols = threading.Thread(target=save_cols_mongo, args=(cols,))
        t_cols.start()
        print(cols)


#  保存mongo
def save_periods_mongo(periods):
    for i in range(0, int(len(periods) / 2)):
        # 插入mongo
        # vol_db.save({'vol': vols[i], "_id": i}, )
        new_period = db.add_period(period_name=periods[i])
        if new_period:
            # 插入成功
            print('new_period 插入成功')
        else:
            print('------------ label %s: Add Failed! ----------' % periods[i])


def save_labels_mongo(labels):
    for label in labels:
        # 插入mongo
        # tag_db.insert({'tag': tag})
        new_label = db.add_label(label_name=label)
        if new_label:
            # 插入成功
            print('new_label 插入成功')
        # else:
        #     print('------------ label %s: Add Failed! ----------' % label)


def save_cols_mongo(cols):
    for col in cols:
        # col['_id'] = hash(col['title'])
        # col_db.save(col)
        new_col = db.add_col(title=col['title'], href=col['href'], cover=col['cover'])
        if new_col:
            # 插入成功
            print('col 插入成功')
        # else:
            # print('------------ col %s: Add Failed! ----------' % col)







get_home_page()


def get_vol_detail():
    url = 'http://www.luoow.com/999/'
    print(url)
    bsObj = lib.load_page(url)
    print(bsObj)


# get_vol_detail()