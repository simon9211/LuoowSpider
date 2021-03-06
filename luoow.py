# -*- coding:utf-8 -*-
import json
import re
import threading
import random
from time import sleep

from urllib.request import urlopen

import pymongo
import ssl

# import db
from spiders import luoow_db
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

# 创建一个线程锁
lock = threading.Lock()


def get_home_page():
    url = 'http://www.luoow.com/'
    bsObj = lib.load_page(url)
    # 根据css样式表查找
    # print(bsObj)

    # 获取往期列表
    periods = []
    period_list = bsObj.findAll("span", {"class": "label"})
    for period in period_list:
        print(period.get_text())
        periods.append(period.get_text())

    #  保存往期列表
    t_period = threading.Thread(target=save_periods_mongo, args=(periods,))
    t_period.start()

    # 获取标签列表
    labels = []
    label_list = bsObj.findAll("a", {"class": "item"})
    for label in label_list:
        print(label.get_text())
        labels.append(label.get_text())

    # 保存标签列表
    t_label = threading.Thread(target=save_labels_mongo, args=(labels,))
    t_label.start()

    # 获取每期详情
    t_col = threading.Thread(target=get_col, args=(periods,))
    t_col.start()


def get_col(cols):
    for i in range(0, 4):
        t = threading.Thread(target=get_col_items, args=(cols,))
        # 启动线程
        t.start()
    # get_vol_items(vols)


def get_col_items(cols):
    while cols:
        # 加锁
        lock.acquire()
        # 取出第一个元素
        vol = cols[0]
        # 将取出的元素从列表中删除，避免重复加载
        del cols[0]
        # 释放锁
        lock.release()

        url = 'http://www.luoow.com'
        tp, col_id = '', -2
        if vol == '音乐电台':
            tp = '/r/'
            col_id = 0
        elif vol == '其他':
            tp = '/e/'
            col_id = -1
        else:
            # string.split(str="", num=string.count(str))
            # string.index(str, beg=0, end=len(string))
            idx = vol.index('-')
            tp = '/' + vol[4:idx] + '_' + str(int(vol[4:idx]) + 99) + '.html'

        url += tp
        idx = random.randint(0, 10)
        # print(url)
        bsObj = lib.load_page(url)
        # print(bsObj)
        # sleep(3)
        col_list = bsObj.findAll("div", {"class": "thumbnail theborder"})
        c = []
        for col in col_list:
            # print(col)
            item = {}
            a = col.findAll('a')
            img = col.find('img')
            item['title'] = a[1].get_text()
            item['href'] = a[1].get('href')[1:-1]
            item['cover_min'] = img.get('src')
            if col_id == -2:
                item['col_id'] = int(str(a[1].get('href')[1:-1]))
            else:
                item['col_id'] = col_id
            c.append(item)
            t_col = threading.Thread(target=get_col_detail, args=(item,))
            t_col.start()

        # t_col = threading.Thread(target=get_col_detail, args=(c[0],))
        # t_col.start()
        # t_cols = threading.Thread(target=save_cols_mongo, args=(cols,))
        # t_cols.start()
        # print(cols)


def get_col_detail(item):
    url = 'http://www.luoow.com/' + item['href'] + '/'
    print(url)
    bsObj = lib.load_page(url)
    # print(bsObj)
    # title, href, cover_min, cover, desc, tags, player_list
    div_container = bsObj.find('div', {'class': 'container'})
    cover = div_container.find('img', {'class': 'img-responsive'}).get('src')
    desc = div_container.find('div', {'class': 'desc'})
    # print(str(desc))
    # print(type(str(desc)))
    tags = []
    div_tags = div_container.find('div', {'class': 'tag'}).findAll('a')
    for div_tag in div_tags:
        tags.append(div_tag.get_text().replace(u'\xa0', u''))
    # print(tags)
    player_list = []

    scr = bsObj.find('body').findAll('script')
    # res = re.split(r'[\[\]]+', scr[-5].get_text())
    # dic_str = '{' + '"data":[' + res[1] + ']}'
    res = get_singles_json(scr[-5].get_text())
    dic_str = '{' + '"data":' + res + '}'
    # print(dic_str)
    dic = eval(dic_str)
    player_list = dic['data']

    new_col = luoow_db.add_col(title=item['title'], href=item['href'], cover_min=item['cover_min'], cover=cover, desc=str(desc),
                         tags=tags, player_list=player_list, col_id=item['col_id'])
    if new_col:
        # 插入成功
        print('col 插入成功')

    # li_players = div_container.find('div', {'id': 'skPlayer'})#.find('ul', {'class': 'skPlayer-list'})#.findAll('li')
    # ul = li_players.find('ul', {'class': 'skPlayer-list'})
    # print(li_players)
    # print(ul)
    # for li in li_players:
    #     print(li)
    print('ssss')


#  保存mongo
def save_periods_mongo(periods):
    for i in range(0, int(len(periods) / 2)):
        # 插入mongo
        # vol_db.save({'vol': vols[i], "_id": i}, )
        new_period = luoow_db.add_period(period_name=periods[i])
        if new_period:
            # 插入成功
            print('new_period 插入成功')
        else:
            print('------------ label %s: Add Failed! ----------' % periods[i])


def save_labels_mongo(labels):
    for label in labels:
        # 插入mongo
        # tag_db.insert({'tag': tag})
        new_label = luoow_db.add_label(label_name=label)
        if new_label:
            # 插入成功
            print('new_label 插入成功')
        # else:
        #     print('------------ label %s: Add Failed! ----------' % label)


def save_cols_mongo(cols):
    for col in cols:
        # col['_id'] = hash(col['title'])
        # col_db.save(col)
        new_col = luoow_db.add_col(title=col['title'], href=col['href'], cover_min=col['cover_min'], cover='', desc='',
                             tags=[], player_list=[])
        if new_col:
            # 插入成功
            print('col 插入成功')
        # else:
        # print('------------ col %s: Add Failed! ----------' % col)


get_home_page()


def get_singles_json(singles_str):
    # print('singles_str:' + singles_str)
    beg = singles_str.index('[')
    end = singles_str.rindex(']')
    if beg < end:
        s = singles_str[beg:end + 1]
        print('sssss:' + s)
        return s
    return '[]'
