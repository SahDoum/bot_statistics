from peewee import *

from datetime import datetime

db_location = '/Users/sah/Documents/BOTS/bot_statistics.db'
table_name = 'bot_stats'

database = SqliteDatabase(db_location, **{})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Actions(BaseModel):
    action = TextField(null=True)
    app_id = TextField()
    usr_id = IntegerField()
    usr_name = TextField(null=True)
    chat_id = IntegerField(null=True)
    chat_name = TextField(null=True)
    date = DateTimeField(default=datetime.now)

    class Meta:
        db_table = table_name

    def __str__(self):
        str = '{}: {} from chat {}'.format(self.date, self.action, self.chat_id)
        return str


def init_track(app_id):
    try:
        Actions.get(Actions.action == 'New bot', Actions.app_id == app_id)
    except Exception:
        Actions.create(
            action='New bot',
            app_id=app_id,
            usr_id=0
        )


def track_by_message(app_id, track, message):
    usr_id = message.from_user.id
    usr_name = message.from_user.username if message.from_user.username is not None else None
    usr_name = message.from_user.first_name if usr_name is None else usr_name
    chat_id = message.chat.id
    chat_name = message.chat.title if message.chat.title is not None else None

    try:
        Actions.get(Actions.action == 'New chat', Actions.chat_id == chat_id, Actions.app_id == app_id)
    except Exception:
        Actions.create(
            action = 'New chat',
            app_id = app_id,
            usr_id = usr_id,
            usr_name = usr_name,
            chat_id = chat_id,
            chat_name = chat_name
        )

    Actions.create(
        action=track,
        app_id=app_id,
        usr_id=usr_id,
        usr_name=usr_name,
        chat_id=chat_id,
        chat_name=chat_name
    )


def track_by_user(app_id, track, user):
    usr_id = user.id
    usr_name = user.username if user.username is not None else None
    chat_id = None
    chat_name = None

    try:
        Actions.get(Actions.action == 'New user', Actions.usr_id == usr_id, Actions.app_id == app_id)
    except Exception:
        Actions.create(
            action = 'New user',
            app_id = app_id,
            usr_id = usr_id,
            usr_name = usr_name,
            chat_id = chat_id,
            chat_name = chat_name
        )

    Actions.create(
        action=track,
        app_id=app_id,
        usr_id=usr_id,
        usr_name=usr_name,
        chat_id=chat_id,
        chat_name=chat_name
    )


def print_log():
    for action in Actions.select():
        print(action)


if __name__ == '__main__':
    if True:
        try:
            Actions.drop_tables()
        except:
            pass
        database.create_tables([Actions])

    print_log()
