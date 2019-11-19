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






def init_user(uID: str, uname: str):
    user = Users.get(Users.userID==uID)
    if user:
        if user.username != uname:
            user.username = uname
            user.save()
    else:
        Users.create(userID= uID, username=uname, yikes=0)



def get_id(rname: str) -> str:
    try:
        return Users.get(Users.realname==rname).userID
    except User.DoesNotExist:
        raise UserNotFound



def add_yikes(uID: str):
    user = Users.get(Users.userID==uID)
    user.yikes += 1
    user.save()