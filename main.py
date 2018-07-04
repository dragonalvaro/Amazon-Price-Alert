import logging

from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext.messagehandler import MessageHandler
from telegram.ext import Filters 

from commands import *
from bot import AmazonBot
from job import CrawlerJob


if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARNING)

    logging.getLogger(AmazonBot.__name__).setLevel(logging.DEBUG)
    #logging.getLogger(FetchAndSendTweetsJob.__name__).setLevel(logging.DEBUG)

    # initialize telegram API
    token = '285896652:AAEjzg55_oFFRyEN-sQi1V7aLqHdGWqKSZE'
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    
    # set commands
    dispatcher.add_handler(CommandHandler('start', cmd_start))
    dispatcher.add_handler(CommandHandler('help', cmd_help))
    dispatcher.add_handler(CommandHandler('ping', cmd_ping))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))
    dispatcher.add_handler(CommandHandler('add', addTracking, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))


    # put job
    #updater.job_queue
    #myqueue._queue(CrawlerJob(), next_t=0)

    # poll
    updater.start_polling()
    updater.idle()

