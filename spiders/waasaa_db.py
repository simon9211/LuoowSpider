import threading

import mongoengine as db

db.connect('waasaa')


class Log(db.Document):
    def __init__(self):
        super(Log, self).__init__()

    date = db.DateTimeField(required=True)
    ip = db.StringField(required=True)
    api = db.StringField(required=True)


class Col(db.Document):
    def __init__(self, *args, **kwargs):
        super(Col, self).__init__(*args, **kwargs)

    href = db.StringField(required=True, unique=True, sparse=True)
    title = db.StringField(required=True)
    date = db.StringField(required=True, )
    img = db.StringField(required=True)
    desc = db.StringField(required=True)
    page_type = db.IntField(required=True)


def add_col(href, title, date, img, desc, page_type, player_list):

    t = threading.Thread(target=add_singles, args=(player_list, href))
    t.start()

    # add_singles(player_list, href)

    if Col.objects(href=href).__len__() == 0:
        new_col = Col(title=title, href=href, date=date, img=img, desc=desc, page_type=page_type)
        new_col.save()
        return True
    return False


lock = threading.Lock()


class Single(db.Document):
    def __init__(self, *args, **kwargs):
        super(Single, self).__init__(*args, **kwargs)

    src = db.StringField(required=True, unique=True, sparse=True)
    title = db.StringField(required=False)
    type = db.StringField(required=False)
    caption = db.StringField(required=False)
    description = db.StringField(required=False)
    metas = db.StringField(required=False)

    href = db.StringField(required=True)
    page_type = db.IntField(required=True)


def add_singles(player_list, href):
    for single in player_list:
        # lock.acquire()
        add_single(src=single['src'], title=single['title'], type=single['type'], caption=single['caption'], description=single['description'], metas=str(single['meta']), page_type=single['page_type'], href=href,)
        # lock.release()


def add_single(src, title, type, caption, description, metas, page_type, href):
    single = Single.objects(src=src)
    print('llllllllllll' + str(len(single)))
    if len(single) == 0:
        new_single = Single(
            src=src,
            title=title,
            type=type,
            caption=caption,
            description=description,
            metas=metas,
            page_type=page_type,
            href=href,
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


class Daily(db.Document):
    def __init__(self, *args, **kwargs):
        super(Daily, self).__init__(*args, **kwargs)
    did = db.IntField(required=True,)
    year = db.StringField(required=True)
    month = db.StringField(required=True)
    day = title = db.StringField(required=True)
    title = db.StringField(required=True)
    artist = db.StringField(required=True)
    aword = db.StringField(required=True)
    mp3 = db.StringField(required=True, unique=True)
    favs = db.IntField(required=True)
    likes = db.IntField(required=True)
    page = db.StringField(required=True)
    thumb = db.StringField(required=True)
    poster = db.StringField(required=True)
    author = db.StringField(required=True)
    author_link = db.StringField(required=True)


def add_daily(did, year, month, day, title, artist, aword, mp3, favs, likes, page, thumb, poster, author, author_link):
    if Daily.objects(did=did).__len__() == 0:
        new_col = Daily(did=did, year=year, month=month, day=day, title=title, artist=artist, aword=aword, mp3=mp3, favs=favs, likes=likes, page=page, thumb=thumb, poster=poster, author=author, author_link=author_link)
        new_col.save()
        return True
    return False


def add_dailies(l):
    for i in l:
        add_daily(**i)

