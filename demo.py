# -*- coding:utf-8 -*-
import re
import urllib.request
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

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
    jd_url = 'http://www.luoow.com/'
    # # response = requests.get(jd_url1)
    # response = requests.get(jd_url, headers={'User-Agent': USER_AGENT[1]})
    # print(response.text)
    # ids = re.findall('data-pid="(.*?)"', response.text, re.S)
    # print(ids)

    html = urlopen(jd_url)
    bsObj = BeautifulSoup(html, 'html5lib')
    print(bsObj)
    # 根据css样式表查找
    vol_List = bsObj.findAll("span", {"class": "label"})
    for vol in vol_List:
        print(vol.get_text())

    tagList = bsObj.findAll("a", {"class": "item"})
    for tag in tagList:
        print(tag.get_text())

    colList = bsObj.findAll("div", {"class": "thumbnail theborder"})

    cols = []
    for col in colList:
        # print(col)
        item = {}
        a = col.findAll('a')
        item['title'] = a[1].get_text()
        item['href'] = a[1].get('href')
        img = col.find('img')

        cols.append(item)

    print(cols)

    # head = {'User-Agent': USER_AGENT[2]}
    # request = urllib.request.Request(headers=head, url=jd_url)
    #
    # try:
    #     response = urllib.request.urlopen(request)
    #     print(response.read())
    #     #return response.read() if raw else BeautifulSoup(response.read(), 'html5lib')
    #
    # except urllib.error.URLError or urllib.error.HTTPError as e:
    #     print(e)


def get_page():
    head = {'User-Agent': USER_AGENT[0]}
    request = urllib.request.Request(headers=head, url="https://www.baidu.com/")

    try:
        response = urllib.request.urlopen(request)
        # response.read() if True else BeautifulSoup(response.read(), 'html5lib')
    except urllib.error.URLError or urllib.error.HTTPError as e:
        print('Load Page Failed. Retry %ss later' % (str(100)))
        print(e)
    # print(BeautifulSoup(response.read(), 'html5lib'))
    return BeautifulSoup(response.read(), 'html.parser')


def get_vol(page):
    def tag_data_to_tag(each):
        return each and each.get_text()

    # 获得 Vol 信息
    print(page)
    # <a href="http://news.baidu.com" target="_blank" class="mnav">新闻</a>
    name = page.find({'a'}, {'href': 'http://news.baidu.com'}).get_text()
    print(name)
    # title = page.find({'span'}, {'class': 'vol-title'}).get_text()
    # vol = int(page.find({'span'}, {'class': 'vol-number rounded'}).get_text())
    # cover = page.find({'img'}, {'class': 'vol-cover'}).attrs['src']
    # description = page.find({'div'}, {'class': 'vol-desc'}).get_text().replace('\n', '<br>')
    # date = page.find({'span'}, {'class': 'vol-date'}).get_text()
    # tags_data = page.findAll({'a'}, {'class': 'vol-tag-item'})
    # tag = map(tag_data_to_tag, tags_data)
    # color = lib.get_average_color(cover)

    # 获得 Track 信息
    # list_data = page.findAll({'li'}, {'class': 'track-item rounded'})
    # length = len(list_data)

    # 如果 Vol 已存在但任务未完成, 删除该 Vol 的所有 Track并删除该 Vol

get_home_page()