import sys
import cmd
from peewee import *

from datetime import datetime, timedelta

db_location = 'bot_statistics.db'
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
        str = '{}: {} from chat {} and user {}'.format(self.date, self.action, self.chat_id, self.usr_id)
        return str


bots = {}
for i, t in enumerate(Actions.select().where(Actions.action == 'New bot')):
    bots[i+1] = t.app_id
    print('{}. {}'.format(i+1, t.app_id))


class StatisticsCmd(cmd.Cmd):
    prompt = 'stats$ '

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        i = input('Enter bot number: ')
        self.BOT_NAME = bots[int(i)]
        print('{} was selected.'.format(self.BOT_NAME))

    def log(self, from_datetime):
        chats = {}
        for action in Actions.select().where(Actions.app_id == self.BOT_NAME, Actions.date >= from_datetime):
            chat = action.usr_name if action.chat_name is None else action.chat_name
            if chat not in chats:
                chats[chat] = {}
            if action.action not in chats[chat]:
                chats[chat][action.action] = 0

            chats[chat][action.action] += 1

        text = ''

        for chat in chats:
            text += '\nIn chat {}:'.format(chat)
            for act in chats[chat]:
                text += '\n  {} {} times.'.format(act, chats[chat][act])

        return text

    def do_all(self, arg):
        for action in Actions.select().where(Actions.app_id == self.BOT_NAME):
            print(action)

    def do_chats(self, arg):
        for action in Actions.select().where(fn.Substr(Actions.action, 1, 5) == 'New c', Actions.app_id == self.BOT_NAME):
            if action.chat_name is None:
                print('User: {} Id: {}'.format(action.usr_name, action.usr_id))
            else:
                print('Chat: {} Id: {}'.format(action.chat_name, action.chat_id))

    def do_today(self, arg):
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)

        text = '{} today statistics:'.format(self.BOT_NAME)
        text += self.log(start)
        print(text)

    def do_week(self, arg):
        today = datetime.utcnow().date()
        start = today - timedelta(days=7)

        text = '{} week statistics:'.format(self.BOT_NAME)
        text += self.log(start)
        print(text)

    def do_clean(self, arg):
        Actions.delete().where(Actions.app_id == BOT_NAME, Actions.action != 'New bot').execute()

    def do_change(self, arg):
        for i, t in enumerate(Actions.select().where(Actions.action == 'New bot')):
            print('{}. {}'.format(i+1, t.app_id))
        i = input('Enter bot number: ')
        self.BOT_NAME = bots[int(i)]

    def do_exit(self, arg):
        print("Exit")
        return True

    do_EOF = do_exit


def parse(arg):
    return tuple(map(int, arg.split()))


if __name__ == "__main__":
    StatisticsCmd().cmdloop()
