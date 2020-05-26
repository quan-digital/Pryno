# -*- coding: utf-8 -*-

# - Tools -
# * Quan.digital *

import math
import os
from decimal import Decimal
import pryno.util.settings as settings

# Satoshi to XBT converter
def XBt_to_XBT(XBt):
    return float(XBt) / 100000000

# Given a number, round it to the nearest tick. 
# Use this after adding/subtracting/multiplying numbers.
# More reliable than round()
def toNearest(num, tickSize = 0.5):
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))

# Empity order checker
def order_leaves_quantity(order):
    if order['leavesQty'] is None:
        return True
    return order['leavesQty'] > 0

# Utility method for finding an item in the store.
# When an update comes through on the websocket, we need to figure out which item in the array it is
# in order to match that item.
#
# Helpfully, on a data push (or on an HTTP hit to /api/v1/schema), we have a "keys" array. These are the
# fields we can use to uniquely identify an item. Sometimes there is more than one, so we iterate through all
# provided keys.
def find_by_keys(keys, table, matchData):
    for item in table:
        if all(item[k] == matchData[k] for k in keys):
            return item
    
# Different way of doing the same thing, legacy
def findItemByKeys(keys, table, matchData):
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item

# Legacy
def set_tickLog(self, instrument):
    instrument['tickLog'] = Decimal(str(instrument['tickSize'])).as_tuple().exponent * -1
    #instrument['tickLog'] = int(math.fabs(math.log10(instrument['tickSize'])))
    return 

def create_dirs():
    '''Creates data directories'''
    try:
        os.mkdir(settings.LOG_DIR.replace('/', ''))
        os.mkdir(settings.FIN_DIR.replace('/', ''))
        print("Directories created.")

    except FileExistsError:
        print("Directories already exist.")

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    return os.path.exists(file_path) and os.stat(file_path).st_size == 0