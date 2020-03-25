# -*- coding:utf-8 -*-
import re
import threading

import urllib.request

import random
from random import choice
from time import sleep

from urllib.request import urlopen

import pymongo
import requests
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
# 数据库

db = client.luoow
# vol表,没有自动创建
vol_db = db.vols
tag_db = db.tags
col_db = db.cols


dblist = client.list_database_names()

print('simon')

USER_AGENT = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]


def get_home_page():
    # jd_url = 'http://www.luoow.com/'
    jd_url = 'http://www.luoow.com/101_200.html'
    # jd_url = 'http://www.luoow.com/701_800.html'
    # response = requests.get(jd_url1)
    res = requests.get(jd_url, headers={'User-Agent': USER_AGENT[1]})
    # print(res.text)
    # html = urlopen(jd_url)
    bsObj = BeautifulSoup(res.text, 'html5lib')
    # 根据css样式表查找
    print(bsObj)
    vols = []
    vol_List = bsObj.findAll("span", {"class": "label"})
    for vol in vol_List:
        print(vol.get_text())
        vols.append(vol.get_text())

    t_vols = threading.Thread(target=save_vols_mongo, args=(vols,))
    t_vols.start()

    t_vols1 = threading.Thread(target=get_vol, args=(vols,))
    t_vols1.start()

    tags = []
    tagList = bsObj.findAll("a", {"class": "item"})
    for tag in tagList:
        print(tag.get_text())
        tags.append(tag.get_text())
    t_tags = threading.Thread(target=save_tags_mongo, args=(tags,))
    t_tags.start()


    # colList = bsObj.findAll("div", {"class": "thumbnail theborder"})
    # cols = []
    # for col in colList:
    #     # print(col)
    #     item = {}
    #     a = col.findAll('a')
    #     item['title'] = a[1].get_text()
    #     item['href'] = a[1].get('href')
    #     img = col.find('img')
    #     item['src'] = img.get('src')
    #     cols.append(item)
    # t_cols = threading.Thread(target=save_cols_mongo, args=(cols,))
    # t_cols.start()
    # print(cols)

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
        res = requests.get(url, headers={'User-Agent': USER_AGENT[idx]})
        print(url)
        # print(res.text)
        bsObj = BeautifulSoup(res.text, 'html5lib')
        print(bsObj)
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
            item['src'] = img.get('src')
            cols.append(item)
        t_cols = threading.Thread(target=save_cols_mongo, args=(cols,))
        t_cols.start()
        print(cols)


#  保存mongo
def save_vols_mongo(vols):
    for i in range(0, int(len(vols) / 2)):
        # 插入mongo
        vol_db.save({'vol': vols[i], "_id": i}, )

def save_tags_mongo(tags):
    for tag in tags:
        # 插入mongo
        tag_db.insert({'tag': tag})

def save_cols_mongo(cols):
    for col in cols:
        col_db.insert(col)




get_home_page()