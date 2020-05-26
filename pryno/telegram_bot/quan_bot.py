from telegram.ext import Updater, CommandHandler , PrefixHandler
import telegram
import json
import requests
import datetime
from collections import defaultdict
import pryno.util.settings as settings
import pryno.util.mail as mail 

chat_id = []

def start(update, context):
	update.message.reply_text('Welcome to QuanBot, please type your QuanID /quanid')
	update.message.reply_text('For unsubscribe from a notification id please type /unsub and the QuanID')

def getName(update,context):
	nome = context.args[0]
	#update.message.reply_text('Your custom callback youngpadawan ' + cpf)
	global chat_id
	if(nome == settings.CLIENT_NAME):
		#mybots[update.message.chat_id] = bot
		update.message.reply_text('Hello {}!'.format(
												update.effective_chat.first_name))
		print(update.message.chat_id)
		chat_id.append(update.message.chat_id)
		update.message.reply_text('The Bot from {0} is {1}, to know better the execution state of your\
		bot access url, but we will keep you posted of the relevant information \
			through this channel'.format(nome,'off' if settings._PAUSE_BOT == True  else 'on'))

def unsub(update, context):
	qid = context.args[0]
	if(qid == settings.CLIENT_NAME):
		for chat in chat_id:
			if(chat == update.message.chat_id):
				chat_id.remove(update.message.chat_id)
				update.message.reply_text('Sucessfuly removed {0} from your notification list'.format(settings.CLIENT_NAME))

#To Send custom message after user logged/bot1199841211:AAHi1GPjTQJ0dkBTTXSm8zHcQEUzIwBT
def send_message(msg):
    print(chat_id)
    if(chat_id):
    	bot = telegram.Bot(token="1199841211:AAHi1GPjTQJ0dkBTTXSm8zHcQEUzIwBThcs")
    	for chat in chat_id:
    		bot.send_message(chat, text=msg)
    else:
    	print('no one registered in this channel')

def send_group_message(msg,bot_token=settings.TOKEN_MAIN_BOT,chat_id = -496268763):
	try:
		bot = telegram.Bot(token=bot_token)
		bot.send_message(chat_id, text=msg)
	except:
		mail.send_email(msg + " telegram bot is overloaded")
		print("cant send message through the bot now")
def InitialiseBot():
	updater = Updater("1242980549:AAHuWBWEo33pViTpHxMeeN97gCs5V7YHDlA", use_context=True)
	# Get the dispatcher to register handlers-496268763
	dp = updater.dispatcher

	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", start))
	dp.add_handler(CommandHandler("quanid",getName))
	dp.add_handler(CommandHandler("unsub",unsub))

     # Start the Bot
	updater.start_polling()