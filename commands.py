import json
from datetime import datetime

import telegram

from models import Tracking, User
from util import with_touched_chat, escape_markdown


def cmd_ping(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Pong!')

def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)    

def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def addTracking(bot, update, args, chat=None):
    if len(args) < 1:
        bot.reply(update, "Use /sub username1 username2 username3 ...")
        return
    amazonItems = args
    not_found = []
    already_subscribed = []
    successfully_subscribed = []

    for item in amazonItems:
        #tg_user = bot.get_tracking(tw_username)
        tg_user = update.message.chat_id

        #if tw_user is None:
        #    not_found.append(tw_username)
        #    continue
        
        if  User.select().where(User.telegramId == tg_user).count() == 1:
            #already_subscribed.append(tw_user.full_name)
            continue

        User.create(telegramId=tg_user)
        #successfully_subscribed.append(tw_user.full_name)

    reply = ""

    if len(not_found) is not 0:
        reply += "Sorry, I didn't find username{} {}\n\n".format(
                     "" if len(not_found) is 1 else "s",
                     ", ".join(not_found)
                 )

    if len(already_subscribed) is not 0:
        reply += "You're already subscribed to {}\n\n".format(
                     ", ".join(already_subscribed)
                 )

    if len(successfully_subscribed) is not 0:
        reply += "I've added your subscription to {}".format(
                     ", ".join(successfully_subscribed)
                 )

    bot.send_message(chat_id=update.message.chat_id, text=reply)

@with_touched_chat
def cmd_start(bot, update, chat=None):
    bot.reply(
        update,
        "Hello! This bot lets you subscribe to twitter accounts and receive their tweets here! "
        "Check out /help for more info.")


@with_touched_chat
def cmd_help(bot, update, chat=None):
        bot.reply(update, """
Hello! This bot forwards you updates from twitter streams!
Here's the commands:
- /sub - subscribes to updates from users
- /unsub - unsubscribes from users
- /list  - lists current subscriptions
- /export - sends you a /sub command that contains all current subscriptions
- /all - shows you the latest tweets from all subscriptions
- /wipe - remove all the data about you and your subscriptions
- /auth - start Twitter authorization process
- /verify - send Twitter verifier code to complete authorization process
- /export\_friends - generate /sub command to subscribe to all your Twitter friends (authorization required)
- /set\_timezone - set your [timezone name]({}) (for example Asia/Tokyo)
- /source - info about source code
- /help - view help text
This bot is being worked on, so it may break sometimes. Contact @franciscod if you want {}
""")


@with_touched_chat
def cmd_sub(bot, update, args, chat=None):
    if len(args) < 1:
        bot.reply(update, "Use /sub username1 username2 username3 ...")
        return
    tw_usernames = args
    not_found = []
    already_subscribed = []
    successfully_subscribed = []

    for tw_username in tw_usernames:
        tw_user = bot.get_tw_user(tw_username)

        if tw_user is None:
            not_found.append(tw_username)
            continue

        if Tracking.select().where(
                Tracking.tw_user == tw_user,
                Tracking.tg_chat == chat).count() == 1:
            already_subscribed.append(tw_user.full_name)
            continue

        Tracking.create(tg_chat=chat, tw_user=tw_user)
        successfully_subscribed.append(tw_user.full_name)

    reply = ""

    if len(not_found) is not 0:
        reply += "Sorry, I didn't find username{} {}\n\n".format(
                     "" if len(not_found) is 1 else "s",
                     ", ".join(not_found)
                 )

    if len(already_subscribed) is not 0:
        reply += "You're already subscribed to {}\n\n".format(
                     ", ".join(already_subscribed)
                 )

    if len(successfully_subscribed) is not 0:
        reply += "I've added your subscription to {}".format(
                     ", ".join(successfully_subscribed)
                 )

    bot.reply(update, reply)