import sys
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
        str = '{}: {} from chat {} and user {}'.format(self.date, self.action, self.chat_id, self.usr_id)
        return str


bots = {}
for i, t in enumerate(Actions.select().where(Actions.action == 'New bot')):
    bots[i+1] = t.app_id
    print('{}. {}'.format(i+1, t.app_id))
i = input('Enter bot number: ')
BOT_NAME = bots[int(i)]
print('{} was selected.'.format(BOT_NAME))


def log(from_datetime):
    chats = {}
    for action in Actions.select().where(Actions.app_id == BOT_NAME, Actions.date >= from_datetime):
        chat = action.usr_name if action.chat_name is None else action.chat_name
        if chat not in chats:
            chats[chat] = {}
        if action.action not in chats[chat]:
            chats[chat][action.action] = 0

        chats[chat][action.action] += 1

    text = '{} today statistics:'.format(BOT_NAME)

    for chat in chats:
        text += '\nIn chat {}:'.format(chat)
        for act in chats[chat]:
            text += '\n  {} {} times.'.format(act, chats[chat][act])

    return text


while(True):
    # cntrl-c to quit
    try:
        input_text = input('stats$ ')

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        print('\nKeyboard Interrupt. Good bye.\n')
        sys.exit()

    if input_text is '':
        continue

    input_text = input_text.split()

    # list of all actions
    if input_text[0] == 'all':
        for action in Actions.select().where(Actions.app_id == BOT_NAME):
            print(action)
    # list of all chats
    elif input_text[0] == 'chats':
        for action in Actions.select().where(fn.Substr(Actions.action, 1, 5) == 'New c', Actions.app_id == BOT_NAME):
            if action.chat_name is None:
                print('User: {} Id: {}'.format(action.usr_name, action.usr_id))
            else:
                print('Chat: {} Id: {}'.format(action.chat_name, action.chat_id))
    # clean all actions
    elif input_text[0] == 'clean':
        Actions.delete().where(Actions.app_id == BOT_NAME, Actions.action != 'New bot').execute()
    # change bot
    elif input_text[0] == 'change':
        for i, t in enumerate(Actions.select().where(Actions.action == 'New bot')):
            print('{}. {}'.format(i+1, t.app_id))
        i = input('Enter bot number: ')
        BOT_NAME = bots[int(i)]
    # today log
    elif input_text[0] == 'today':
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day)
        print(log(start))

    # error
    else:
        print('error')
