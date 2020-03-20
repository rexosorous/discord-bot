import peewee



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


db.create_tables([Users, Clips])



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
    except User.DoesNotExist:
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
    except User.DoesNotExist:
        raise UserNotFound



def get_yikes_from_uname(uname: str) -> int:
    try:
        user = Users.get(Users.username==uname)
        return user.yikes
    except User.DoesNotExist:
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



def get_clip_stats() -> str:
    stats = '```Clip Name                                                                        | Soundboard | Roulette | Total\n'
    for clip in Clips.select():
        stats += '%(name)-.80s | %(soundboard_play_count)-10i | %(roulette_play_count)-8i | %(total_play_count)-5i\n' % clip.__dict__['__data__']
    stats += '```'
    return stats