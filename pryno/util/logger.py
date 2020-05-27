# -*- coding: utf-8 -*-

# - Log tools -
# * Quan.digital *

import logging
import traceback
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pryno.util import settings, tools
from pryno.telegram_bot import quan_bot as telegram_bot

def setup_logger():
    '''Prints logger info to terminal'''
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def setup_logbook(name, extension='.txt', level=logging.INFO):
    """Setup logger that writes to file, supports multiple instances with no overlap.
       Available levels: DEBUG|INFO|WARN|ERROR"""
    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d (%(name)s) - %(message)s', datefmt='%d-%m-%y %H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = str(settings.LOG_DIR + name +'_' + date + extension)
    handler = RotatingFileHandler(log_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_db(name, extension='.csv',level=logging.INFO, getHandler = False):
    """Setup writer that formats data to csv, supports multiple instances with no overlap."""
    formatter = logging.Formatter(fmt='%(asctime)s,%(message)s', datefmt='%d-%m-%y,%H:%M:%S')
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = str(settings.LOG_DIR + name + '_' + date + extension)

    handler = RotatingFileHandler(log_path, maxBytes=100000000, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if getHandler:
        return logger, handler
    else:
        return logger

def setup_dictlogger(name, extension='.json', level=logging.INFO):
    formatter = logging.Formatter(fmt='%(message)s')
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = str(settings.LOG_DIR + name + '_' + date + extension)

    handler = RotatingFileHandler(log_path, maxBytes=100000000, backupCount=1)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Logs orders into csv
def log_orders(orders, stop=False):
    '''Log orders into csv'''
    order_logger, order_handler = setup_db('orders', getHandler = True)
    try:
        # Multi-input case
        for order in orders:
            order_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s" % 
            (order['orderID'], order['account'], order['symbol'],order['side'], order['orderQty'],order['stopPx'] if stop else order['price'], order['ordStatus'],
            order['clOrdID'], order['timestamp']))
    except:
        try:
            # Single order case
            order_logger.info("%s, %s, %s, %s, %s, %s, %s, %s, %s" % 
            (orders['orderID'], orders['account'], orders['symbol'],orders['side'], orders['orderQty'],orders['stopPx'] if stop else  orders['price'], orders['ordStatus'],
            orders['clOrdID'], orders['timestamp']))
        except:
            log_error(orders)

    # Close logger
    order_logger.removeHandler(order_handler)

    # Increase unix open file limit
    # ulimit -n 2048

    return

# Global error_logger so all functions can use it
error_logger = logging.getLogger('errors')

def setup_error_logger():
    '''Basic handler setup for error_logger'''
    date = datetime.today().strftime('%Y-%m-%d')
    log_path = settings.LOG_DIR + 'errors_' + date + '.txt'

    global error_logger
    error_logger = logging.getLogger('errors')
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=settings.MAX_FILE_SIZE, backupCount=1) # stream=sys.stdout
    error_logger.addHandler(handler)

def close_error_logger():
    error_logger.removeHandler(error_logger.handlers[0])
    return

def log_exception(exc_type, exc_value, exc_traceback):
    '''Log unhandled exceptions'''
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info(str(datetime.now()))
    error_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info('')
    message = ''.join(str(exc_type) + str(exc_value)).join(traceback.format_tb(exc_traceback))
    telegram_bot.send_group_message(msg="❗ Exception ocurred for {0} at {1}, here's the traceback: \n {2}".format(
                                                    settings.CLIENT_NAME,str(datetime.now()),message))

    tools.kill_pids()
    # os.popen('killall python3')
    # os.popen('sudo killall -9 python3') # force kill extreme
    # os.popen('python3 main.py')
    return
# then set sys.excepthook = logger.log_exception on main file

def log_error(message):
    '''Log handled errors'''
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info(str(datetime.now()))
    error_logger.error(message)
    error_logger.info('-----------------------------------------------------------------')
    error_logger.info('')
    if 'Restarting...' not in message:
        telegram_bot.send_group_message(msg="🚨 Error ocurred for {0} at {1}, here's the traceback: {2}".format(
                                                    settings.CLIENT_NAME,str(datetime.now()),message))
    tools.kill_pids()
    # os.popen('killall python3')
    return