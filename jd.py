# -*- coding:utf-8 -*-
import json
import threading
import urllib.request
import pymongo as pymongo
import requests
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
import re
from bs4 import BeautifulSoup

from pylab import plt, np

# import pylab
# mongo服务
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
# jd数据库
db = client.jd
# product表,没有自动创建
product_db = db.product

dblist = client.list_database_names()

print(dblist)

# 统计以下几个颜色
color_arr = ['肤色', '黑色', '紫色', '粉色', '蓝色', '白色', '灰色', '香槟色', '红色']

color_num_arr = []
sizes = 0
for i in color_arr:
    num = product_db.count({'product_color': i})
    color_num_arr.append(num)
    sizes += 1

# 显示的颜色
color_arrs = ['bisque', 'black', 'purple', 'pink', 'blue', 'white', 'gray', 'peru', 'red']

# labeldistance，文本的位置离远点有多远，1.1指1.1倍半径的位置
# autopct，圆里面的文本格式，%3.1f%%表示小数有三位，整数有一位的浮点数
# shadow，饼是否有阴影
# startangle，起始角度，0，表示从0开始逆时针转，为第一块。一般选择从90度开始比较好看
# pctdistance，百分比的text离圆心的距离
# patches, l_texts, p_texts，为了得到饼图的返回值，p_texts饼图内部文本的，l_texts饼图外label的文本
# patches,l_text,p_text = plt.pie(color_num_arr, labels=color_arr, colors=color_arrs,
#                                       labeldistance=1.1, autopct='%3.1f%%', shadow=False,
#                                       startangle=90, pctdistance=0.6)
# 改变文本的大小
# 方法是把每一个text遍历。调用set_size方法设置它的属性
# for t in l_text:
#     t.set_size=(30)
# for t in p_text:
#     t.set_size=(20)
# 设置x，y轴刻度一致，这样饼图才能是圆的
# plt.axis('equal')
# plt.title("内衣颜色比例图", fontproperties="SimHei") #
# plt.rcParams['font.sans-serif']=['SimHei']
# plt.legend()
# plt.show()

index = ["A", "B", "C", "D"]

value = []
for i in index:
    num = product_db.count({'product_size': i})
    value.append(num)

# plt.bar(len(index), left=0, height=value, color="green", width=0.5)
xlocation = np.linspace(5, len(value) * 0.6, len(value))
plt.bar(xlocation, height=value, color="green", width=0.5)
plt.xticks(xlocation, index, fontsize=12, rotation=20)
plt.show()


#  保存mongo
def save_mongo(comments):
    for comment in comments:
        product_data = {}
        # 颜色
        # flush_data清洗数据的方法
        product_data['product_color'] = flush_data(comment['productColor'])
        # size
        product_data['product_size'] = flush_data(comment['productSize'])
        # 评论内容
        product_data['comment_content'] = comment['content']
        # create_time
        product_data['create_time'] = comment['creationTime']
        # 插入mongo
        print('insert to db')
        product_db.insert(product_data)


def flush_data(data):
    if '肤' in data:
        return '肤色'
    if '黑' in data:
        return '黑色'
    if '紫' in data:
        return '紫色'
    if '粉' in data:
        return '粉色'
    if '蓝' in data:
        return '蓝色'
    if '白' in data:
        return '白色'
    if '灰' in data:
        return '灰色'
    if '槟' in data:
        return '香槟色'
    if '琥' in data:
        return '琥珀色'
    if '红' in data:
        return '红色'
    if '紫' in data:
        return '紫色'
    if 'A' in data:
        return 'A'
    if 'B' in data:
        return 'B'
    if 'C' in data:
        return 'C'
    if 'D' in data:
        return 'D'


"""
查询商品id
"""

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


def find_product_id(key_word):
    jd_url1 = 'https://search.jd.com/search?keyword=%E5%86%85%E8%A1%A3&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%86%85%E8%A1%A3&cid2=1345&cid3=1364&page=3&s=56&click=0'
    'https://search.jd.com/search?keyword=%E5%86%85%E8%A1%A3&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E5%86%85%E8%A1%A3&cid2=1345&cid3=1364&page=3&s=56&click=0'
    jd_url = 'https://search.jd.com/Search'
    product_ids = []
    # response = requests.get(jd_url1)
    # 商品id
    # 爬前3页的商品
    for i in range(1, 4):
        param = {'keyword': key_word, 'enc': 'utf-8', 'page': i,
                 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 Edg/80.0.361.66'}
        response = requests.get(jd_url, params=param, headers={'User-Agent': USER_AGENT[1]})
        # 商品id
        # print(response.text)
        ids = re.findall('data-pid="(.*?)"', response.text, re.S)
        print(ids)
        product_ids += ids
    return product_ids


"""
获取评论内容
"""


# https://club.jd.com/comment/productPageComments.action?productId=53732706684&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
def get_comment_message(product_id):
    urls = ['https://sclub.jd.com/comment/productPageComments.action?' \
            'productId={}' \
            '&score=0&sortType=5&' \
            'page={}' \
            '&pageSize=10&isShadowSku=0&rid=0&fold=1'.format(product_id, page) for page in range(1, 20)]
    # uuu = ['https://club.jd.com/comment/productPageComments.action?productId=53732706684&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1']
    for url in urls:
        response = requests.get(url)
        html = response.text
        # 删除无用字符
        # html = html.replace('fetchJSON_comment98vv53282(', '').replace(');', '')
        data = json.loads(html)
        comments = data['comments']
        print(comments)
        t = threading.Thread(target=save_mongo, args=(comments,))
        t.start()


# 创建一个线程锁
lock = threading.Lock()


# 获取评论线程
def spider_jd(ids):
    while ids:
        # 加锁
        lock.acquire()
        # 取出第一个元素
        id = ids[0]
        # 将取出的元素从列表中删除，避免重复加载
        del ids[0]
        # 释放锁
        lock.release()
        # 获取评论内容
        get_comment_message(id)

# product_ids = find_product_id('胸罩') #['8663878']
#
# for i in (0, 6):
#     # 增加一个获取评论的线程
#     t = threading.Thread(target=spider_jd, args=(product_ids,))
#     # 启动线程
#     t.start()

# spider_jd(product_ids)
# get_comment_message(product_ids[i])
