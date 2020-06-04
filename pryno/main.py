# -*- coding: utf-8 -*-

import sys
import os
from threading import Thread

# Checks for settings.py and creates it accordingly
try:
	from pryno.util import settings
except:
	print('No settings.py found!')
	from pryno.config import configure
	configure.create_settings(base_path='config/settings_base.py', config_path='config/config.json' , out_path = 'util/settings.py')
	from pryno.util import settings
	settings.VALID_USERNAME_PASSWORD_PAIRS.update({settings.CLIENT_NAME: settings.CLIENT_PWD})

from pryno.config import configure
from pryno.util import tools, logger
from pryno.strategies import pps
from pryno.dashboard import app


def build_bot():
	'''Wrapper to run strategy due to path conflicts.'''
	try:
		os.popen("python3 -c 'import main; main.build_mm()'")
		return True
	except:
		return False


def build_mm():
	try:
		mm = pps.PPS()
		return True
	except:
		return False


def build_app():
	try:
		Thread(target=app.run_server).start()
		return True
	except:
		return False


if __name__ == '__main__':
	try:
		logger.setup_logger()
		tools.create_dirs()
		# Build new settings to handle updates
		configure.create_settings(base_path='config/settings_base.py', config_path='config/config.json', out_path='util/settings.py')
		settings.VALID_USERNAME_PASSWORD_PAIRS.update({settings.CLIENT_NAME: settings.CLIENT_PWD})
		settings.STM_INDICATOR_INIT = len(settings.BOT_NAME) + len(settings.BOT_VERSION) + 2
		settings.GRADLE_INDICATOR_INIT = len(settings.BOT_NAME) + len(settings.BOT_VERSION) + 2
		settings.STM_INDICATOR_END = len(settings.STM_INDICATOR)+ len(settings.BOT_NAME) + len(settings.BOT_VERSION)+1
		settings.GRADLE_INDICATOR_END = len(settings.BUY_INDICATOR)+ len(settings.BOT_NAME) + len(settings.BOT_VERSION)+1
		settings.STM_NUMBER = settings.STM_INDICATOR_END
		settings.GRADLE_NUMBER = settings.GRADLE_INDICATOR_END
		pid = os.getpid()
		with open('pids/bot.pid', 'w') as w:
			w.write(str(pid))
		mm = pps.PPS(settings.BASE_URL)
		Thread(target=app.run_server).start()
		mm.run_loop()
	except (KeyboardInterrupt, SystemExit):
		# mm.exchange.cancel_every_order()
		mm.exit()
		# sys.exit()
		# os.popen('killall python3')
