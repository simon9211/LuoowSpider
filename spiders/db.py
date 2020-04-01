# -*- coding:utf-8 -*-
import threading

import mongoengine as db

db.connect('luoow')


class Single(db.Document):
    def __init__(self, *args, **kwargs):
        super(Single, self).__init__(*args, **kwargs)

    src = db.StringField(required=True, unique=True, sparse=True)
    href = db.StringField(required=True,)
    author = db.StringField(required=True)
    name = db.StringField(required=True)
    cover = db.StringField(required=True)


class Log(db.Document):
    def __init__(self):
        super(Log, self).__init__()

    date = db.DateTimeField(required=True)
    ip = db.StringField(required=True)
    api = db.StringField(required=True)


class Period(db.Document):
    def __init__(self, *args, **kwargs):
        super(Period, self).__init__(*args, **kwargs)

    period_name = db.StringField(required=True, unique=True)


def add_period(period_name):
    if Period.objects(period_name=period_name).__len__() == 0:
        new_period = Period(period_name=period_name)
        new_period.save()
        return True
    return False


class Label(db.Document):
    def __init__(self, *args, **kwargs):
        super(Label, self).__init__(*args, **kwargs)

    label_name = db.StringField(required=True, unique=True)


def add_label(label_name):
    if Label.objects(label_name=label_name).__len__() == 0:
        new_label = Label(label_name=label_name)
        new_label.save()
        return True
    return False


class Col(db.Document):
    def __init__(self, *args, **kwargs):
        super(Col, self).__init__(*args, **kwargs)

    title = db.StringField(required=True, unique=True)
    href = db.StringField(required=True, unique=True)
    cover_min = db.StringField(required=True, unique=True)
    cover = db.StringField(required=True, unique=True)
    desc = db.StringField(required=True)
    tags = db.ListField()
    # player_list = db.ListField(required=False)


def add_col(title, href, cover_min, cover, desc, tags, player_list):

    t = threading.Thread(target=add_singles, args=(player_list, href))
    t.start()

    # add_singles(player_list, href)

    if Col.objects(href=href).__len__() == 0:
        new_col = Col(title=title, href=href, cover_min=cover_min, cover=cover, desc=desc, tags=tags, )
        new_col.save()
        return True
    return False


lock = threading.Lock()


def add_singles(player_list, href):
    for single in player_list:
        # href, src, author, name, cover
        # lock.acquire()
        add_single(src=single['src'], author=single['author'], name=single['name'], href=href, cover=single['cover'])
        # lock.release()



def add_single(href, src, author, name, cover):
    single = Single.objects(src=src)
    print('llllllllllll' + str(len(single)))
    if len(single) == 0:
        new_single = Single(
            src=src,
            href=href,
            author=author,
            name=name,
            cover=cover
        )
        new_single.save()
        return True
    else:
        print(src)
        # h = single[0].href
        # print('aaaaaaa:' + h[0] + ' href:' + href)
        # if href not in h:
        #     print('zzzzzzzz' + src)
        #     Single.objects(src=src).update(href=h + [href])

    return False
