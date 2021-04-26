# -*- coding: utf-8 -*-

# - Telegram API Wrapper -
# * Quan.digital *

from telegram.ext import Updater, CommandHandler , PrefixHandler
import telegram
import json
import requests
import datetime
from collections import defaultdict
import pryno.util.settings as settings
import pryno.util.mail as mail 

chat_id = []
TOKEN_INFO = ""


def send_group_message(msg,chat_id,bot_token=TOKEN_INFO):
	try:
		bot = telegram.Bot(token=bot_token)
		bot.send_message(chat_id, text=msg)
	except:
		mail.send_email(msg + " telegram bot is overloaded")
		print("cant send message through the bot now")
