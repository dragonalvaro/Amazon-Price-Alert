import os
import re
import json
import time
import requests
import smtplib
import argparse
from urllib.parse import urlparse
from urllib.parse import urljoin
import datetime,random
import UserAgent
import telegram
import logging

from copy import copy
from lxml import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date, datetime, timedelta

from telegram.ext import Job
from threading import Event

ua = UserAgent.UserAgent()
intervalTimeBetweenCheck = 0
dateIndex = datetime.now()
emailinfo = {}

IFTTT_Key = ""
IFTTT_EventName = ""


def send_Notification(msg_content):
    global send_Mode
    telegram_alert(msg_content)

def telegram_alert(msg_content):
    global botToken
    global chatId

    # 1 is success
    # 2 is server working msg
    # 3 is server shutdown
    if msg_content['code'] == 1:
        message = "Congratulations! " + str(msg_content['Price']) +"  "+ msg_content['Product'] + " " + " " + msg_content['URL']

    elif msg_content['code'] == 2:
        message = '🔴' + msg_content['Content']

    elif msg_content['code'] == 3:
        message = msg_content['Content']

    bot.send_message(chat_id=chatId, text=message)
    print ("Mesage posted to telegram:",chatId)


# send notified mail once a day.
def checkDayAndSendMail():
    todayDate = datetime.now()
    start = datetime(todayDate.year, todayDate.month, todayDate.day)
    end = start + timedelta(days=1)
    global dateIndex

    # if change date
    if dateIndex < end :
        dateIndex = end
        # send mail notifying server still working
        msg_content = {}
        msg_content['Subject'] = '[Amazon Price Alert] Server working !'
        msg_content['Content'] = 'Amazon Price Alert still working until %s !' % (todayDate.strftime('%Y-%m-%d %H:%M:%S'))
        msg_content['Price'] = ""
        msg_content['Time'] = todayDate.strftime('%Y-%m-%d %H:%M:%S')
        msg_content['ServerState'] = "Working"
        msg_content['code'] = 2 # 2 is server state
        send_Notification(msg_content)

def get_price(url, selector):
    
    # set random user agent prevent banning
    r = requests.get(url, headers={
        'User-Agent':
            ua.random(),
        'Accept-Language':    'zh-tw',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection':'keep-alive',
        'Accept-Encoding':'gzip, deflate'
    })
    r.raise_for_status()
    tree = html.fromstring(r.text)

    

    # find product name
    productName = ""
    productName_results = tree.xpath(selector['productname'])
    if not productName_results:
        # raise Exception("Product Name does not exist")
        print('Didn\'t find the \'product-name\' element, trying again later...')
    else :
        productName = productName_results[0].text
        productName = productName.strip()

    # find Price
    # try:
    #     # extract the price from the string
    #     price_string = re.findall('\d+.\d+', tree.xpath(selector['price'])[0].text)[0]
    #     return float(price_string.replace(',', '')),productName
    
    # except IndexError, TypeError:
    #     #print('Didn\'t find the \'price\' element, trying again later...')
        
    #     # be banned, send mail then shut down
    #     # send mail notifying server shutdown
    #     msg_content = {}
    #     msg_content['Subject'] = '[Amazon Price Alert] Server be banned !'
    #     msg_content['Content'] = 'Amazon Price Alert be banned at %s !' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #     msg_content['Price'] = ""
    #     msg_content['Time'] = ""
    #     msg_content['ServerState'] = "Banned"
    #     msg_content['code'] = 3 # 3 is server shutdown
    #     send_Notification(msg_content)
    #     return 0,productName




# read config json from path
def get_config(config):
    with open(config, 'r') as f:
        # handle '// ' to json string
        input_str = re.sub(r'// .*\n', '\n', f.read())
        return json.loads(input_str)

# add some arguments 
def parse_args():
    parser = argparse.ArgumentParser()
    #parser.add_argument('-c', default='%s/config.json'job % os.path.dirname(os.path.realpath(__file__)), help='Add your config.json path')
    #parser.add_argument('-t', type=int, default=780,help='Time(second) between checking, default is 780 s.')

    return parser.parse_args()

def run(self,bot):
    #set up arguments
    #args = parse_args()
    #intervalTimeBetweenCheck = args.poll_interval
    global dateIndex
    global emailinfo
    global IFTTT_Key,IFTTT_EventName,send_Mode
    global botToken, chatId
    global bot 

    
    dateIndex = datetime.now()

    # get config from path
    config = get_config(args.config)
    emailinfo = config['email']
    intervalTimeBetweenCheck = config['default-internal-time']
    send_Mode = config['send_Mode']
    IFTTT_Key = config['IFTTT']['key']
    IFTTT_EventName = config['IFTTT']['eventName']
    botToken = config['Telegram']['botToken']
    chatId = config['Telegram']['chatId']

    #initialize telegram bot
    if send_Mode == 3:
        bot = telegram.Bot(botToken)

    #get all items to parse
    items = config['item-to-parse']

    while True and len(items):
        nowtime = datetime.now()
        nowtime_Str = nowtime.strftime('%Y-%m-%d %H:%M:%S')
        print ('[%s] Start Checking' % (nowtime_Str))

        # send mail notify system working everyday
        checkDayAndSendMail()

        itemIndex = 1
        for item in copy(items):
            # url to parse
            item_page_url = urljoin(config['amazon-base_url'], item[0])
            print('[#%02d] Checking price for %s (target price: %s)' % ( itemIndex, item[0], item[1]))

            # get price and product name
            productName = item[2]
            price,productName = get_price(item_page_url, config['xpath_selector'])
            
            
            # Check price lower then you expected
            if not price:
                continue
            elif price <= item[1]:
                print('[#%02d] %s\'s price is %s!! Trying to send email.' % (itemIndex,productName,price))
                msg_content = {}
                msg_content['Subject'] = '[Amazon] %s Price Alert - %s' % (productName,price)
                msg_content['Content'] = '[%s]\nThe price is currently %s !!\nURL to salepage: %s' % (nowtime_Str, price, item_page_url)
                msg_content['Price'] = price
                msg_content['URL'] = item_page_url
                msg_content['Product'] = productName
                msg_content['ServerState'] = ""
                msg_content['code'] = 1 # 2 is server state
                send_Notification(msg_content)
                items.remove(item)
            else:
                print('[#%02d] %s\'s price is %s. Ignoring...' % (itemIndex,productName,price))
            itemIndex += 1


        if len(items):
            # time interval add some random number for preventing banning
            nowtime = datetime.now()
            thisIntervalTime = intervalTimeBetweenCheck + random.randint(0,150)

            #calculate next triggered time
            dt = datetime.now() + timedelta(seconds=thisIntervalTime)
            print('Sleeping for %d seconds, next time start at %s\n' % (thisIntervalTime, dt.strftime('%Y-%m-%d %H:%M:%S')))
            time.sleep(thisIntervalTime)
        else:
            break


#if __name__ == '__main__':
#    main()
