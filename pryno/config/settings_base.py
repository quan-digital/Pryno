# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

import pkg_resources  

# API URL
BASE_URL = "https://testnet.bitmex.com/api/v1/"
# BASE_URL = "https://www.bitmex.com/api/v1/"

# Bot email
CLIENT_NAME = ''
CLIENT_PWD = ''
STRATEGY_NAME = 'Carlao Strategy'

# Bitmex API Key Pair
BITMEX_KEY = ""
BITMEX_SECRET = ""

#####################################################
# Operation Parameters
#####################################################

# Risk in percent for each trade
RISK_PER_TRADE = 3

# Number of steps with lower price step
LOW_RISK_ORDER = 4  
MEDIUM_RISK_ORDER= 11
ORDER_INCREASE_INTERVAL = 7

#Contracts Percentual
CONTRACT_PCT = 1.75/100
#Activate Fixed Margin
FIXED_MARGIN_FLAG = False
ISOLATED_MARGIN_FACTOR = 0
#Margin funds percentual to get for amount of contracts as steps increases, for dynamic contract steps 
SMALL_CONTRACT = 0.215
MEDIUM_CONTRACT = 0.2375
LARGE_CONTRACT = 0.3 
# Enable=1 or disable=0 volume profile and amplitude 
ENABLE_VOLUMAMP = 1
MIN_DM = 1450000
MIN_DM_CANCEL = 800000
MAX_VOLUME = 11450000

# Set FIXED_STEP to None if you want to use limits, otherwise specify an integer
FIXED_STEP = 30
MIN_STEP = 20
MAX_STEP = 40
INITIAL_STEP = 15

# Delta for target order
PROFIT_TARGET = 2

# Contract number divisor for each order
RISK_DIVISOR = 1

# Percentage of actual price to calculate order step
STEP_PCT = 0.0043

# Number of steps on each gradle side
TOTAL_STEP = 5

# Total number of stop orders
STOP_MARKET_ORDERS = 2

#####################################################
# Telegram Parameters
#####################################################

SLEEP_TELEGRAM = 30

#####################################################
# Structural Parameters
#####################################################

# Time in seconds to wait after each loop
LOOP_INTERVAL = 8

# Send Email if a order higher then this step is executed
SEND_EMAIL_GRADLE = 3

# If any of these files (and this file) changes, reload the bot.
#WATCHED_FILES = ['strategies/pps.py', 'util/api_bitmex.py', 'util/settings.py']
WATCHED_FILES = []

#####################################################
# Dashboard
#####################################################

# Server settings
DEBUG_DASH = False

# Dashboard update interval in seconds
DASH_INTERVAL = 10

# Authentication
VALID_USERNAME_PASSWORD_PAIRS = {
    'claudin':'cafefrio',
    'kaue':'greekgod',
    'antonio':'gayragnar',
    'xande':'bumbumza1',
    'pynoclient' : 'capile123'

}

ADMIN_USERS = {
    'claudin':'cafefrio',
    'kaue':'greekgod',
    'antonio':'gayragnar',
    'xande':'bumbumza1',
}


#####################################################
# API
#####################################################

# Sets postOnly order type, guarantees fee rebate but risks not being fulfilled right away
POST_ONLY = False

# Time interval to analyse candles
CANDLE_TIME_INTERVAL = 130

# In seconds
AUTH_EXPIRE_TIME = 10
API_TIMEOUT = 7

# Retry wait time in seconds
HTTP_RETRY_TIME = 8

# Max retry number for getting open orders via http
HTTP_MAX_RETRIES = 10

# Max retry number for order placement
ORDER_MAX_RETRIES = 10

VOLUME_TOLERANCE = 10000000


#####################################################
# Constants & Misc
#####################################################

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"

# Strategy name
BOT_NAME = "CDC"

# path/to/logdir
LOG_DIR = 'logs/'

# Max file size in bytes
MAX_FILE_SIZE = 100000000 # 100MB

#path/to/financedir
FIN_DIR = 'fin/'

# Numbers of seconds in a day
_SLEEP_FOR_ONE_DAY = 86400

_HIGH_STEP_ORDER = False
_REACHED_STOP  = False
_REACHED_TARGET  = False

_PAUSE_BOT = False

# Project version from setuptools
BOT_VERSION = str(pkg_resources.require("pryno")[0].version)

STM_INDICATOR = '_Stm'
TGT_INDICATOR = '_Tgt'
BUY_INDICATOR = '_Buy'
SELL_INDICATOR = '_Sel'

#Stop and Buy orders indicators
STM_INDICATOR_INIT = 0
GRADLE_INDICATOR_INIT = 0
STM_INDICATOR_END = 0
GRADLE_INDICATOR_END = 0
STM_NUMBER = 0
GRADLE_NUMBER = 0

#####################################################
# Mail & Telegram
#####################################################

BOT_MAIL = "pipryno@gmail.com"
BOT_PWD = "SurubaoParaiso123"
# Birth date 10/03/2000

# Email receipients
MAIL_TO_ERROR = ['gthomquan@gmail.com']
MAIL_ACTIVITY = ['gthomquan@gmail.com']

#Telegram Bots Token
TOKEN_MAIN_BOT = "1199841211:AAHi1GPjTQJ0dkBTTXSm8zHcQEUzIwBThcs"
DEBUGGER_BOT = "1242980549:AAHuWBWEo33pViTpHxMeeN97gCs5V7YHDlA"
DEBUGGER_BOT_GROUP = -459197842



#####################################################
# Instance Parameters
#####################################################

