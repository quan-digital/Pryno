# -*- coding: utf-8 -*-

# - Tools -
# * Quan.digital *

import math
import os
from decimal import Decimal
import pryno.util.settings as settings

def XBt_to_XBT(XBt):
    '''Satoshi to XBT converter.'''
    return float(XBt) / 100000000

def toNearest(num, tickSize = 0.5):
    '''Given a number, round it to the nearest tick. 
    Use this after adding/subtracting/multiplying numbers.
    More reliable than round().'''
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))

def order_leaves_quantity(order):
    '''Empty order checker.'''
    if order['leavesQty'] is None:
        return True
    return order['leavesQty'] > 0

def find_by_keys(keys, table, matchData):
    '''Utility method for finding an item in the store.
    When an update comes through on the websocket, we need to figure out which item in the array it is
    in order to match that item.

    Helpfully, on a data push (or on an HTTP hit to /api/v1/schema), we have a "keys" array. These are the
    fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through all
    provided keys.'''
    for item in table:
        if all(item[k] == matchData[k] for k in keys):
            return item

def findItemByKeys(keys, table, matchData):
    '''Different way of doing the same thing, legacy.'''
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item

def create_dirs():
    '''Creates data directories'''
    try:
        os.mkdir(settings.LOG_DIR.replace('/', ''))
        os.mkdir(settings.FIN_DIR.replace('/', ''))
        os.mkdir('pids')
        print("Directories created.")
    except FileExistsError:
        print("Directories already exist.")

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0

def kill_cd():
    '''Kill bot and forever processes.'''
    with open('pids/bot.pid', 'r') as r1:
        pid1 = r1.read()
    with open('pids/forever.pid', 'r') as r2:
        pid2 = r2.read()
    # with open('pids/app.pid', 'r') as r3:
    #     pid3 = r3.read()
    os.popen('kill %s' % pid1)
    os.popen('kill %s' % pid2)
    # os.popen('kill %s' % pid3)

def kill_pids():
    '''Kill bot and app processes.'''
    with open('pids/app.pid', 'r') as r1:
        pid1 = r1.read()
    with open('pids/bot.pid', 'r') as r2:
        pid2 = r2.read()
    os.popen('kill %s' % pid1)
    os.popen('kill %s' % pid2)