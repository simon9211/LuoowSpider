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
import requests

from spiders import waasaa_db
from spiders import lib

ssl._create_default_https_context = ssl._create_unverified_context

# 创建一个线程锁
lock = threading.Lock()

categories = [
    {
        'category': 'word',
        'pages': 0,
        'pageType': 0
    },
    {
        'category': 'sy',
        'pages': 0,
        'pageType': 1
    },
    {
        'category': 'qikan',
        'pages': 0,
        'pageType': 2
    },
    {
        'category': 'xc',
        'pages': 0,
        'pageType': 3
    },
    # {
    #     'category': 'daily',
    #     'pages': 0,
    #     'pageType': 4
    # },
    {
        'category': 'luoo',
        'pages': 0,
        'pageType': 5
    },
    {
        'category': 'b-b',
        'pages': 0,
        'pageType': 6
    },
    ]


class pageType():
    Word = 0
    Voice = 1
    Period = 2
    Live = 3
    Daily = 4
    Luoo = 5
    Bb = 6


# 获取所有的标签的页数
def get_page_count():
    for category in categories:
        url = 'https://www.waasaa.com/category/' + category['category']
        bsObj = lib.load_page(url)
        pages = bsObj.findAll("a", {"class": "page-numbers"})
        if len(pages) > 0:
            page_count = pages[-2].get_text()
            print(pages[-2].get_text())
            category['pages'] = page_count
        else:
            category['pages'] = 1

        for page in range(1, int(category['pages']) + 1):
            t_period = threading.Thread(target=get_list_page, args=(category['category'] + '/page/{}'.format(page), category['pageType']))
            t_period.start()
        # get_list_page(category['category'] + '/page/1', category['pageType'])

    # get_list_page(categories[1]['category'] + '/page/1', categories[1]['pageType'])


def get_list_page(params, page_type):
    url = 'https://www.waasaa.com/category/' + params
    bs_obj = lib.load_page(url)
    # 根据css样式表查找
    # print(bsObj)
    container_div = bs_obj.find("div", {"class": "section"})
    title = container_div.find("h3", {"class": "dynamic-subtitle section-title subtitle"}).get_text()
    print(title)

    items = []

    first_item = container_div.find('div', {'class': 'first-blog-post-item'}).find('a', {'class': 'big-archive blog-post-image-link-block w-inline-block'})

    first_title = first_item.get('title')
    first_href = first_item.get('href')
    first_img = first_item.get('style').split("'")[1]
    first_date = first_item.find('div', {'class': 'blog-date'}).get_text()
    print(first_title + ' date: ' + first_date + ' href: ' + first_href + ' img: ' + first_img)
    items.append({'title': first_title, 'href': first_href, 'img': first_img, 'date': first_date, 'page_type': page_type})
    item_divs = container_div.findAll('div', {'class': 'blog-post-item'})
    for item in item_divs:
        t = item.find('a', {'class': 'blog-post-image-link-block medium w-inline-block'})
        title = t.get('title')
        href = t.get('href')
        img = t.get('style').split("'")[1]
        date = t.find('div', {'class': 'blog-date small'}).get_text()
        items.append({'title': title, 'href': href, 'img': img, 'date': date, 'page_type': page_type})
        print(title + ' date: ' + date + ' href: ' + href + ' img: ' + img)

    # for item in items:
    #     t_period = threading.Thread(target=get_detail_page, args=(item, page_type))
    #     t_period.start()
        # get_detail_page(item, page_type)

    get_detail_page(items)


# 获取详情
def get_detail_page(items):
    while items:
        # 加锁
        lock.acquire()
        # 取出第一个元素
        item = items[0]
        # 将取出的元素从列表中删除，避免重复加载
        del items[0]
        # 释放锁
        lock.release()
        page_type = item['page_type']
        bs_obj = lib.load_page(item['href'])
        # bs_obj = lib.load_page(item)
        if page_type == pageType.Word:
            # 文字
            # 文字获取音频
            container_div = bs_obj.find('div', {'class': 'white-content-block'})
            img = container_div.find('div', {'class': 'blog-post-image-block'}).get('style').split("'")[1]
            div_rich_text_div = container_div.find('div', {'class': 'rich-text-block w-richtext'})
            div_ps = div_rich_text_div.findAll('p')
            desc = ''
            for p in div_ps:
                desc = desc + str(p)
            audio_url = container_div.find('source', {'type': 'audio/mpeg'}).get('src')
            item['desc'] = desc
            # src=single['src'], title=single['title'], type=single['type'], caption=single['caption'], description=single['description'], meta=single['meta'], page_type=single['page_type']
            playlist = [
                {
                    'src': audio_url,
                    'title': '',
                    'type': 'audio\\/mpeg',
                    'caption': '',
                    'description': '',
                    'meta': '',
                    'page_type': page_type
                }
            ]
            waasaa_db.add_col(href=item['href'], title=item['title'], date=item['date'], img=item['img'], desc=item['desc'], page_type=page_type, player_list=playlist)
            print('img: ' + img + ' audio_url: ' + audio_url + 'div_p: ' + desc)
        elif page_type in [pageType.Voice, pageType.Period, pageType.Luoo, pageType.Bb]:
            # 声音 期刊 回落 李志
            container_div = bs_obj.find('div', {'class': 'white-content-block'})
            img = container_div.find('div', {'class': 'blog-post-image-block'}).get('style').split("'")[1]
            div_rich_text_div = container_div.find('div', {'class': 'rich-text-block w-richtext'})
            div_ps = div_rich_text_div.findAll('p')
            desc = ''
            for p in div_ps:
                desc = desc + str(p)
            # 声音 期刊 获取播放列表
            play_list_div = container_div.find('div', {'class': 'wp-playlist wp-audio-playlist wp-playlist-light'})
            play_list_str, play_list_dic, playlist = '', {}, []
            if play_list_div is not None:
                play_list_str = play_list_div.find('script', {'class': 'wp-playlist-script'}).get_text()
                play_list_str = play_list_str.replace('true', "'true'")
                play_list_dic = eval(play_list_str)
                for i in play_list_dic['tracks']:
                    i['page_type'] = page_type
                    playlist.append(i)
                    print(i)
            else:
                audio_url = container_div.find('source', {'type': 'audio/mpeg'}).get('src')
                playlist.append({
                    'src': audio_url,
                    'title': '',
                    'type': 'audio\\/mpeg',
                    'caption': '',
                    'description': '',
                    'meta': '',
                    'page_type': page_type
                })
            print('img: ' + img + ' div_p: ' + desc)

            item['desc'] = desc
            # src=single['src'], title=single['title'], type=single['type'], caption=single['caption'], description=single['description'], meta=single['meta'], page_type=single['page_type']

            waasaa_db.add_col(href=item['href'], title=item['title'], date=item['date'], img=item['img'], desc=item['desc'], page_type=page_type,player_list=playlist)
        elif page_type == pageType.Live:
            # 现场
            container_div = bs_obj.find('div', {'class': 'white-content-block'})
            img = container_div.find('div', {'class': 'blog-post-image-block'}).get('style').split("'")[1]
            div_rich_text_div = container_div.find('div', {'class': 'rich-text-block w-richtext'})
            video_url = div_rich_text_div.find('video').get('src')
            item['desc'] = ''
            # src=single['src'], title=single['title'], type=single['type'], caption=single['caption'], description=single['description'], meta=single['meta'], page_type=single['page_type']
            playlist = [
                {
                    'src': video_url,
                    'title': '',
                    'type': 'video\\/mpeg',
                    'caption': '',
                    'description': '',
                    'meta': '',
                    'page_type': page_type
                }
            ]
            waasaa_db.add_col(href=item['href'], title=item['title'], date=item['date'], img=item['img'], desc=item['desc'], page_type=page_type,
                              player_list=playlist)
            print('img: ' + img + ' video_url: ' + video_url)


def get_daily_playlist():
    url = 'https://www.waasaa.com/wp-admin/admin-ajax.php?action=get_daily_playlist'
    response = requests.get(url)
    html = response.text
    if html.startswith(u'\ufeff'):
        html = html.encode('utf8')[3:].decode('utf8')
    # 删除无用字符
    # html = html.replace('fetchJSON_comment98vv53282(', '').replace(');', '')
    data = json.loads(html)
    playlist = data['playlist']
    for play in playlist:
        print(str(play))
        play['did'] = play['id']
        del play['id']
        waasaa_db.add_daily(**play)
        # waasaa_db.add_daily(did=play['id'], year=play['year'], month=play['month'], day=play['day'], title=play['title'], artist=play['artist'], aword=play['aword'], mp3=play['mp3'], favs=play['favs'], likes=play['likes'], page=play['page'], thumb=play['thumb'], poster=play['poster'], author=play['author'], author_link=play['author_link'])
    # waasaa_db.add_dailies(playlist)


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

    new_col = waasaa_db.add_col(title=item['title'], href=item['href'], cover_min=item['cover_min'], cover=cover,
                         desc=str(desc),
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
        new_period = waasaa_db.add_period(period_name=periods[i])
        if new_period:
            # 插入成功
            print('new_period 插入成功')
        else:
            print('------------ label %s: Add Failed! ----------' % periods[i])


def save_labels_mongo(labels):
    for label in labels:
        # 插入mongo
        # tag_db.insert({'tag': tag})
        new_label = waasaa_db.add_label(label_name=label)
        if new_label:
            # 插入成功
            print('new_label 插入成功')
        # else:
        #     print('------------ label %s: Add Failed! ----------' % label)


def save_cols_mongo(cols):
    for col in cols:
        # col['_id'] = hash(col['title'])
        # col_db.save(col)
        new_col = waasaa_db.add_col(title=col['title'], href=col['href'], cover_min=col['cover_min'], cover='', desc='',
                                    tags=[], player_list=[])
        if new_col:
            # 插入成功
            print('col 插入成功')
        # else:
        # print('------------ col %s: Add Failed! ----------' % col)



def get_singles_json(singles_str):
    # print('singles_str:' + singles_str)
    beg = singles_str.index('[')
    end = singles_str.rindex(']')
    if beg < end:
        s = singles_str[beg:end + 1]
        print('sssss:' + s)
        return s
    return '[]'


# get_page_count()
# https://www.waasaa.com/52640.html # 文字
# get_detail_page('https://www.waasaa.com/52640.html', pageType.Word)
#
# # https://www.waasaa.com/23188.html # 声音
# get_detail_page('https://www.waasaa.com/23188.html', pageType.Voice)
#
# # https://www.waasaa.com/52668.html # 期刊
# get_detail_page('https://www.waasaa.com/52668.html', pageType.Period)
#
# # https://www.waasaa.com/52463.html # 现场
# get_detail_page('https://www.waasaa.com/52463.html', pageType.Live)
#
# # https://www.waasaa.com/daily # 心情
get_daily_playlist()
#
# # https://waasaa.com/50900.html # 回落
# get_detail_page('https://waasaa.com/50900.html', pageType.Luoo)
#
# # https://waasaa.com/25057.html # 李志
# get_detail_page('https://waasaa.com/25057.html', pageType.Bb)