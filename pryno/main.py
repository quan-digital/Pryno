# -*- coding: utf-8 -*-

from time import sleep
import sys
import datetime as dt
import os
from threading import Thread
from pryno.util import settings
from pryno.util import logger
from pryno.strategies import pps
from pryno.dashboard import app

if __name__ =='__main__':
	try:
		mm = pps.PPS(settings.BASE_URL)
		Thread(target = app.run_server).start()
		mm.run_loop()
	except (KeyboardInterrupt, SystemExit):
		#mm.exchange.cancel_every_order()
		mm.exit()
		sys.exit()
		# os.popen('killall python3')