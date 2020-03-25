# -*- coding:utf-8 -*-
import mongoengine as db

db.connect('luoow')


class Task(db.document):
    def __init__(self):
        super(Task, self).__init__()

    done = db.BooleanField(default=False)
    vol = db.IntField(required=True, unique=True)
    url = db.StringField(required=True)


class Track(db.document):
    def __init__(self):
        super(Track, self).__init__()

    track_id = db.IntField(required=True)
    vol = db.IntField(required=True)
    name = db.StringField(required=True)
    artist = db.StringField(required=True)
    album = db.StringField(required=True)
    cover = db.StringField(required=True)
    order = db.IntField(required=True)
    url = db.StringField(required=True)
    lyric = db.StringField(required=False)
    color = db.ListField(required=True)


class Vol(db.document):
    def __init__(self):
        super(Vol, self).__init__()

    vol_id = db.IntField(required=True)
    title = db.StringField(required=True)
    vol = db.IntField(required=True, unique=True)
    cover = db.StringField(required=True, unique=False)
    description = db.StringField(required=False, unique=False)
    date = db.StringField(required=True)
    length = db.IntField(required=True)
    tag = db.ListField()
    color = db.ListField(required=True)


class Single(db.document):
    def __init__(self):
        super(Single, self).__init__()

    single_id = db.IntField(required=True)
    from_id = db.IntField(required=True)
    name = db.StringField(required=True)
    artist = db.StringField(required=True)
    cover = db.StringField(required=True)
    url = db.StringField(required=True)
    description = db.StringField(required=True)
    date = db.IntField(required=True)
    recommender = db.StringField(required=True)
    color = db.ListField(required=True)


class Log(db.document):
    def __init__(self):
        super(Log, self).__init__()

    date = db.DateTimeField(required=True)
    ip = db.StringField(required=True)
    api = db.StringField(required=True)


def add_vol(id, title, vol, cover, description, date, length, tag, color):
    if Vol.objects(vol=vol).__len__() == 0:
        new_vol = Vol(
            vol_id=id,
            title=title,
            vol=vol,
            cover=cover,
            description=description,
            date=date,
            length=length,
            tag=tag,
            color=color
        )

        new_vol.save()
        return True
    return False


def add_track(id, vol, name, artist, album, cover, order, url, color, lyric=None):
    new_vol = Vol.objects(vol=vol)
    if new_vol.__len__() == 1:
        track = Track(
            vol=int(vol),
            track_id=id,
            name=name,
            artist=artist,
            album=album,
            cover=cover,
            order=order,
            url=url,
            lyric=lyric,
            color=color
        )
        track.save()
        return True
    return False


def add_task(vol, url):
    if Task.objects(vol=vol).__len__() == 0:
        task = Task(
            vol=vol,
            url=url
        )
        task.save()
        return True
    return False


def add_single(id, from_id, name, artist, cover, url, description, date, recommender, color):
    if Single.objects(date=date).__len__() == 0:
        new_single = Single(
            single_id=id,
            from_id=from_id,
            name=name,
            artist=artist,
            cover=cover,
            url=url,
            description=description,
            date=date,
            recommender=recommender,
            color=color
        )
        new_single.save()
        return True
    return False