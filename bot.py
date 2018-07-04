import logging

import telegram
from telegram import Bot
from telegram.error import TelegramError

from models import Tracking, User
from util import escape_markdown


class AmazonBot(Bot):

    def __init__(self, token, update_offset=0):
        super().__init__(token=token)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing")
        self.update_offset = update_offset

    def reply(self, update, text, *args, **kwargs):
        self.sendMessage(chat_id=update.message.chat.id, text=text, *args, **kwargs)

    def get_tracking(self, tg_chat):
        db_chat, _created = Tracking.get_or_create(
            chat_id=tg_chat.id,
            tg_type=tg_chat.type,
        )
        return db_chat

