import peewee
from exceptions import *



db = peewee.SqliteDatabase('users.db', pragmas={
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,
            'foreign_keys': 1,
            'ignore_check_counstraints': 0,
            'synchronous': 0
            })


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Users(BaseModel):
    userID = peewee.CharField(unique=True)
    username = peewee.CharField()
    realname = peewee.CharField(null=True, unique=True)
    yikes = peewee.IntegerField()


class Clips(BaseModel):
    name = peewee.CharField()
    total_play_count = peewee.IntegerField()
    roulette_play_count = peewee.IntegerField()
    soundboard_play_count = peewee.IntegerField()


class Reminders(BaseModel):
    time = peewee.FloatField()
    msg = peewee.CharField()
    pings = peewee.CharField()
    active = peewee.BooleanField()


db.create_tables([Users, Clips, Reminders])



def init_user(uID: str, uname: str):
    '''
    changes a user's username if it is changed
    adds new users into the database if they aren't in
    '''
    uname = uname.lower()
    try:
        user = Users.get(Users.userID==uID)
        if user:
            if user.username != uname:
                user.username = uname
                user.save()
    except peewee.DoesNotExist:
        Users.create(userID= uID, username=uname, yikes=0)



def get_id(rname: str) -> str:
    rname = rname.lower()
    try:
        return Users.get(Users.realname==rname).userID
    except Users.DoesNotExist:
        raise UserNotFound



def get_nicknames() -> [dict]:
    user_list = []
    for user in Users.select().where(Users.realname!=None):
        user_dict = {
            'username': user.username,
            'nickname': user.realname
        }
        user_list.append(user_dict)
    return user_list



def add_yikes(uID: str):
    user = Users.get(Users.userID==uID)
    user.yikes += 1
    user.save()



def get_yikes_from_rname(rname: str) -> int:
    try:
        user = Users.get(Users.realname==rname)
        return user.yikes
    except Users.DoesNotExist:
        raise UserNotFound



def get_yikes_from_uname(uname: str) -> int:
    try:
        user = Users.get(Users.username==uname)
        return user.yikes
    except Users.DoesNotExist:
        raise UserNotFound



def add_clip_stat(clip_name: str, type_: str):
    try:
        clip = Clips.get(Clips.name==clip_name)
    except peewee.DoesNotExist:
        clip = Clips.create(name=clip_name, total_play_count=0, roulette_play_count=0, soundboard_play_count=0)
    finally:
        clip.total_play_count += 1
        if type_ == 'roulette':
            clip.roulette_play_count += 1
        elif type_ =='soundboard':
            clip.soundboard_play_count += 1
        clip.save()



def get_clip_stats(sort: str, order: str) -> [str]:
    """Gets all the clip stats saved in the database

    Parameters
    ----------
    sort: {'name', 'soundboard', 'roulette', 'total'}
        The field by which to sort the data.

    order: {'asc', 'desc'}
        Sort by ascending or descending order.

    Returns
    ------------
    [str]
        Each element is a different line (stat)
    """
    sort_type = {'name': Clips.name,
                 'soundboard': Clips.soundboard_play_count,
                 'roulette': Clips.roulette_play_count,
                 'total': Clips.total_play_count}

    stats = []

    if order == 'asc':
        for clip in Clips.select().order_by(+sort_type[sort]):
            stats.append(f'{clip.name[:80]: <80} | {clip.soundboard_play_count: <10} | {clip.roulette_play_count: <8} | {clip.total_play_count: <5}')
    elif order == 'desc':
        for clip in Clips.select().order_by(-sort_type[sort]):
            stats.append(f'{clip.name[:80]: <80} | {clip.soundboard_play_count: <10} | {clip.roulette_play_count: <8} | {clip.total_play_count: <5}')
    return stats



def add_reminder(time: float, msg: str, pings: str):
    Reminders.create(time=time, msg=msg, pings=pings, active=True).save()



def get_reminders(time: float) -> [dict]:
    '''Gets reminders that should be pinged before the given time

    to get all pings (even past ones) use time=10000000000 which is something like 300 years in the future
    to get pings

    Parameters
    ------------
    time : float
        unix time obtained from time.time()

    Returns
    -----------
    [peewee.Model]
        each element of the list is a peewee.Model instance which represents each reminder

    Examples
    ----------
    time=10000000000    returns all pings
    time=0              returns no pings
    time=time.time()    returns all pings that are due
    '''
    return list(Reminders.select().where((Reminders.time<=time) & (Reminders.active==True)))



def remove_reminder(id_: int):
    selected = Reminders.get(Reminders.id==id_)
    selected.active=False
    selected.save()