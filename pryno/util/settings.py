# -*- coding: utf-8 -*-

# - Settings -
# * Quan.digital *

import pkg_resources  

# API URL
BASE_URL = "https://testnet.bitmex.com/api/v1/"
# BASE_URL = "https://www.bitmex.com/api/v1/"

# Bot email
CLIENT_NAME = 'Cthulhu'
STRATEGY_NAME = 'PPS'

# Bitmex API Key Pairs

# kaue@gmail : pryno : TESTNET
BITMEX_KEY = "0aV6qmThEH680-8OKSlnx__J"
BITMEX_SECRET = "2G74dk7eCLhEErpTmFq6TTOj8HX_NvRZ2hfOmunJ7U9fxCnx"

# kaue@gmail : seila : TESTNET
# BITMEX_KEY = "rolMDEfUQwwASTckmugBkeM5"
# BITMEX_SECRET = "anR6vCI74u10ggGAxAlCVN05ITrtC8bwiK4_s86vtXRARddP"

#DALLAS
# bitmex_key = "kduY6LrC2NGcTKMalNgzgiHD"
# bitmex_secret =  "RiEKMY2Xxuk4AGDjmXhQImxMpQ6FSHusyPgHaGwPOAMiE6gP"

#MATT
# bitmex_key = "gApIJjnEDjpx5cK9BiTYc22r"
# bitmex_secret =  "LPQFjdUnf1bZZMi12YdUVQWlq_VfllDpwdSb-C1WWPFOsLxa"

# kaue@elint : 211 : TESTNET
# bitmex_key = "xN_wtdAuDF8H3EPjDE_VkqEW"
# bitmex_secret = "0Q9fxMmz9cxgkLnHKYm00ZAFrqBaFYreqnMheASq8f9CgBKQ"

# elintdata@gmail.com : bot1 : BITMEX
# bitmex_key = "7JEjfUfpt7T9gMno8NSw86Ld"
# bitmex_secret = "Qya14PDUSNc8w7gRG_XGrv_Gy0IczQeeKrumVxsPhF6JnFdr"


#####################################################
# Operation Parameters
#####################################################

# Number of steps with lower price step
LOW_RISK_ORDER = 4  
MEDIUM_RISK_ORDER= 11
ORDER_INCREASE_INTERVAL = 7

#Contracts Percentual
CONTRACT_PCT = 1.75/100
#Activate Fixed Margin
FIXED_MARGIN_FLAG = False
ISOLATED_MARGIN_FACTOR = 5
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
    'fonfon':'zangief',
    'carlao':'cafetao',
    'felipe':'comunista',
    'pynoclient' : 'capile123',
    'dallas' : 'KARMAdemo2020',
    'matt' : 'KARMAdemo2020'
}

ADMIN_USERS = {
    'claudin':'cafefrio',
    'kaue':'greekgod',
    'antonio':'gayragnar',
    'xande':'bumbumza1',
    'fonfon':'zangief',
    'carlao':'cafetao',
    'felipe':'comunista'
}


#####################################################
# API
#####################################################

# Sets postOnly order type, guarantees fee rebate but risks not being fulfilled right away
POST_ONLY = False

# Time interval to analyse candles
CANDLE_TIME_INTERVAL = 60

# Number of times sanity check must be false in order to restart the websocket
SANITY_LIMIT = 2

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
# Websocket
#####################################################

# Don't grow a table larger than 200. Helps cap memory usage.
MAX_TABLE_LEN = 200

# Timeout for Websocket, in seconds
WS_TIMEOUT = 5

# You can sub to orderBookL2 for all levels, or orderBook10 for top 10 levels & save bandwidth
ORDERBOOK = "orderBook10"


#####################################################
# Constants & Misc
#####################################################

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"

# Bot name, up to 5 characters
BOT_NAME = "pryno"

# Strategy name
BOT_NAME = "PPS"

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
BOT_VERSION = str(pkg_resources.require("pryno")[0].version).replace(".","")

#####################################################
# Mail & Telegram
#####################################################

BOT_MAIL = "pipryno@gmail.com"
BOT_PWD = "SurubaoParaiso123"
# Birth date 10/03/2000

# Email receipients
MAIL_TO_ERROR = ['kauecano@gmail.com', 'claudiocarvalhovilasboas@gmail.com']
MAIL_ACTIVITY = ['kauecano@gmail.com', 'claudiocarvalhovilasboas@gmail.com','antoniodelimaesilva@gmail.com','alexandre.c.bandarra01@gmail.com']

#Telegram Bots Token
TOKEN_MAIN_BOT = "1199841211:AAHi1GPjTQJ0dkBTTXSm8zHcQEUzIwBThcs"
DEBUGGER_BOT = "1242980549:AAHuWBWEo33pViTpHxMeeN97gCs5V7YHDlA"
DEBUGGER_BOT_GROUP = -459197842