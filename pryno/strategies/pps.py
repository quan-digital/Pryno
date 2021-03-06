# -*- coding: utf-8 -*-

# - Pryno Position Strategy -
# * Quan.digital *


from pryno.util.api_bitmex import BitMEX
from pryno.util import settings
from pryno.util import tools
from pryno.util import logger
from time import sleep
import datetime
import sys
import os
from os.path import getmtime
import random
import atexit
import traceback
import json
from pryno.telegram_bot import quan_bot as telegram_bot

# Used for reloading the bot - saves modified times of key files
watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]


class PPS:

    def __init__(self, bitmex_url="https://testnet.bitmex.com/api/v1/", force_operate=True):
        settings.STRATEGY_NAME = 'PPS'
        logger.setup_error_logger()
        sys.excepthook = logger.log_exception
        atexit.register(self.__on_close)
        self.logger = logger.setup_logbook(name="pps")
        self.logger.info("Pryno is starting.")
        self.SLEEP_TELEGRAM = settings.SLEEP_TELEGRAM
        #Also insert your created bot token on the quan_bot file in TOKEN_INFO)
        # To understand better how to use the telegram bot just access the link below:
            # https://www.codementor.io/@karandeepbatra/part-1-how-to-create-a-telegram-bot-in-python-in-under-10-minutes-19yfdv4wrq
        # telegram_bot.send_group_message(msg="❗ Example to use telegram messages",chat_id= YOUR_CHAT_ID)
        # Setup loggers
        self.status_logger = logger.setup_dictlogger('status')
        self.wallet_logger = logger.setup_db('wallet')
        self.exec_logger = logger.setup_db('exec_http')

        # Initialize exchange
        self.symbol = settings.SYMBOL
        self.exchange = BitMEX(base_url=bitmex_url,
                symbol=self.symbol, apiKey=settings.BITMEX_KEY, apiSecret=settings.BITMEX_SECRET)

        # Class parameters
        self.stopSet = 0
        self.stopMarketSell = ''
        self.stopMarketBuy = ''
        self._contractStep = 10
        self._sanityCounter = 0
        self.offset_index = 0
        self.c1 = 0
        self.c2 = 0
        self.c3 = 0
        self.c4 = 0
        self.wallet_amount = 0
        self.c_old = 0
        self.available_margin = {}
        self.instrument = {}
        self.tickSize = 0
        self.actualPrice = 0
        self._ExecStatusTarget = ''
        self.botHighStepInfo = ''
        self.last_execution = ''
        self.position = []
        self.aboveHighStep = False
        self.step_number = 0
        self.starting = True

        # Write operation file for bot control
        if force_operate:
            with open(settings.LOG_DIR + 'operation.json', 'w') as op:
                json.dump(dict(operation=True), op)

        current_stop_path = settings.LOG_DIR + 'last_stop.json'
        try:
            with open(current_stop_path, 'r') as f:
                self.botStopInfo = json.load(f)
        except:
            self.botStopInfo = ''


        self.logger.info("-\*---------------------|Pryno|---------------------*/-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("Pryno Position Strategy starting, connecting to BitMEX.")
        self.logger.info("Using symbol %s." % self.symbol)
        self.logger.info("Version 1.0")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*------------------|quan.digital|-----------------*/-")

    def restart(self):
        '''Close loggers, wait and restart'''
        self.logger.info('Restarting...')

        # Close loggers
        self.logger.removeHandler(self.logger.handlers[0])
        self.status_logger.removeHandler(self.status_logger.handlers[0])
        self.wallet_logger.removeHandler(self.wallet_logger.handlers[0])
        self.exec_logger.removeHandler(self.exec_logger.handlers[0])

        sleep(1)
        self._data_dump()
        self.__init__(settings.BASE_URL, force_operate=False)
        self.run_loop()

    def _data_dump(self):
        '''Get information needed for status from position, margin and instrument.'''
        positionQty = self.positionContracts
        if(self.leverage is None):
            positionLeverage = 0
        elif(self.leverage == 0):
            positionLeverage = 'Cross'
        else:
            positionLeverage = round(float(self.leverage))

        positionLiquid = self.liquidationPrice
        unrealisedPnl = self.available_margin['unrealisedPnl']
        realisedPnl = self.available_margin['realisedPnl']
        avgEntryPrice = self.avgEntryPrice
        breakEvenPrice = self.breakEvenPrice
        unrealisedProfit = self.available_margin['unrealisedProfit']
        availableMargin = self.available_margin['availableMargin']
        markPrice = self.instrument['markPrice']
        fundingRate = self.instrument['fundingRate']
        volumeInst = self.instrument['volume']
        bidPrice = self.instrument['bidPrice']
        askPrice = self.instrument['askPrice']
        # getting info to log status
        status_dict = self.exchange.get_full_status(self.actualPrice, self.operationParameters, self.wallet_amount,
                    self.amountOpenOrders, self.openOrders, positionQty, positionLeverage, positionLiquid,
                unrealisedPnl, realisedPnl, avgEntryPrice, breakEvenPrice, unrealisedProfit,
                availableMargin, markPrice, fundingRate, volumeInst, bidPrice, askPrice)

        self.status_logger.info(str(json.dumps(status_dict)) + ",")
        current_status_path = settings.LOG_DIR + 'current_status.json'
        with open(current_status_path, 'w') as f:
            json.dump(status_dict, f)
        return


    def _profit_check(self):
        '''
        This function is responsible for all the profit logic, getting information
        whether there is a new deposit or withdrawn or sending the responding email if it's payday
        '''
        # Path for user balance information
        profit_file_path = settings.FIN_DIR + 'initialBalance.json'
        client_file_data = settings.FIN_DIR 
        # getting bitmex wallet information
        wallet = self.exchange.get_funds()
        file_alter = False
        checking_alterations = {}
        self.wallet_amount = wallet['amount']
        self.logger.info('wallet info {0}'.format(self.wallet_amount))
        try:
            with open(profit_file_path) as f:
                checking_alterations = json.loads(f.read())
                weeklyProfit = datetime.datetime.strptime(checking_alterations['dueDate'], "%Y-%m-%d %H:%M:%S.%f")

                # Deposits
                if wallet['deposited'] != checking_alterations['lastDeposit']:
                    delta = float(wallet['deposited']) - float(checking_alterations['lastDeposit'])
                    checking_alterations['lastDeposit'] = wallet['deposited']
                    checking_alterations['initialBalance'] = float(checking_alterations['initialBalance']) + delta
                    file_alter = True

                # Withdrawals
                if wallet['withdrawn'] != checking_alterations['lastWithdrawal']:
                    delta = float(wallet['withdrawn']) - float(checking_alterations['lastWithdrawal'])
                    checking_alterations['lastWithdrawal'] = wallet['withdrawn']
                    checking_alterations['initialBalance'] = float(checking_alterations['initialBalance']) - delta
                    file_alter = True

                if  weeklyProfit < datetime.datetime.now():
                    start_date = datetime.datetime.strptime(checking_alterations['timestamp'],"%Y-%m-%d %H:%M:%S.%f")
                    totalProfit = float(self.wallet_amount) - float(checking_alterations['initialBalance'])
                    self.logger.info('Mister {0} profited a total of {1} BTC with this Strategy'.format(checking_alterations['clientName'], tools.XBt_to_XBT(totalProfit)))
                    operationweek = int((weeklyProfit-start_date).days/7)
                    client_file_data = client_file_data + 'week' + str(operationweek)
                    client_Data = {
                        'totalProfit': totalProfit,
                        'client_name': settings.CLIENT_NAME,
                        'profit_file_last_week': checking_alterations
                    }

                    with open(client_file_data,'w') as week:
                        json.dump(client_Datas,week)

                    nextweeklyProfit = weeklyProfit + datetime.timedelta(days=7)
                    checking_alterations['initialBalance'] = self.wallet_amount
                    checking_alterations['dueDate'] = str(nextweeklyProfit)
                    file_alter = True

            #If there's change write again over balance file
            if(file_alter == True):
                with open(profit_file_path,'w') as f:
                    f.seek(0) 
                    json.dump(checking_alterations, f)

        #Client first week with the bot operating at his account
        except FileNotFoundError:
            start_date = datetime.datetime.now()
            weeklyProfit = start_date + datetime.timedelta(days=7)
            profit_data = {
                'timestamp': str(start_date),
                'initialBalance': self.wallet_amount,
                'lastDeposit': wallet['deposited'],
                'lastWithdrawal': wallet['withdrawn'],
                'dueDate': str(weeklyProfit),
                'clientName': settings.CLIENT_NAME 
            }

            with open(profit_file_path,'w') as f:
                json.dump(profit_data, f)
        except: 
            print('Some weird error at Profit check {0} '.format(traceback.format_exc()))


    def exit(self):
        self.__on_close()

    def __on_close(self):
        '''Handling exit.'''
        if(not self.position):
            if self.position[0]['currentQty'] == 0:
                self.exchange.cancel_every_order()
                self.logger.info('No positions, all orders cancelled.')
            else:
                self.logger.warning('Position found, orders still active!')
   
        else:
            self.logger.warning('Shuting down your system')
            
    def prepare_order_dynamic(self,index,priceStep,one_time):
        '''
        This functions prepare orders with variated price step, starting with a range of 15$ for the
        Low risk orders and rising up to the priceStep for the rest of the orders with an offset   
        '''
        index = index + 1
        acumulado = 0
        offset_price = 15
        step_price = settings.INITIAL_STEP if(index < settings.LOW_RISK_ORDER) else priceStep
        if(one_time):
            self.offset_index = self.offset_index + 1 if(settings.MEDIUM_RISK_ORDER > index >  settings.ORDER_INCREASE_INTERVAL) else self.offset_index
        acumulado = acumulado + step_price*index + offset_price*self.offset_index
        self.logger.info('Contract of {0}, and the price {1}, and offset price {2}'.format(index,acumulado,self.offset_index))
        return acumulado

    def prepare_order_static(self,index,priceStep,one_time):
        '''
        Static priceStep orders, seems to be more secure and profitable than Dinamic PrepareOrder
        '''
        index = index + 1
        acumulado = 0
        acumulado = acumulado + priceStep*index
        return acumulado
        
    def prepare_contract(self,index):
        '''
        Prepare a variated amount of contracts opening in order to try to minimize the stop loss
        pulling the medium price up, but levels up leverage as well
        '''
        index = index + 1
        if index == 1:
            contract = round(settings.SMALL_CONTRACT*self.actualPrice*tools.XBt_to_XBT(self.available_margin['availableMargin']))/settings.RISK_DIVISOR
            self.c1 = contract
        elif  index == 2:
            contract = self.c1 + round(settings.SMALL_CONTRACT*self.actualPrice*tools.XBt_to_XBT(self.available_margin['availableMargin']))/settings.RISK_DIVISOR
            self.c2 = contract
        elif index == 3:
            contract = self.c2 + round(settings.SMALL_CONTRACT*self.actualPrice*tools.XBt_to_XBT(self.available_margin['availableMargin']))/settings.RISK_DIVISOR
        elif index == 4:
            contract = 2*self.c2 + self.c1
            self.c4 = contract 
        elif index == 5:
            contract = self.c4 + self.c1
            self.c_old = contract
        elif 11 > index > 5:
            contract =  self.c_old + self.c1
            self.c_old = contract
        elif index == 11:
            contract = self.c_old
        elif index == 12:
            contract = round(self.c_old*1.3)
            self.c_old = contract
        elif index == 13:
            contract = round(self.c_old*1.5)
        return contract


    def post_gradle_orders(self):
        '''Post gradle orders + stop to both sides'''
        orders = []
        if(self.amountOpenOrders != settings.TOTAL_STEP*2 + settings.STOP_MARKET_ORDERS):
            # Not idle and no gradle - anomaly
            if(self.amountOpenOrders > 0):
                self.logger.warning("Order number anomaly detected")
                self.logger.info("Cancelling every order")
                self.exchange.cancel_every_order()

            accumulation = True
            if(self.operationParameters['avgTrade'] > 2800):
                accumulation = False

            if(self.operationParameters['amplitude'] >self.priceStep*3):
                accumulation = True
            # Filters fulfilled
            if(self.operationParameters['average_dollarMinute'] > settings.MIN_DM*settings.ENABLE_VOLUMAMP):
                if(self.operationParameters['amplitude'] > self.priceStep*2*settings.ENABLE_VOLUMAMP):
                    if(settings.ENABLE_VOLUMAMP == 0):
                        self.operationParameters['lockAnomaly'] = False
                    if(not self.operationParameters['lockAnomaly']):
                        if (self.operationParameters['amplitude']*settings.ENABLE_VOLUMAMP < self.priceStep*10):
                            # Double checking http parameters
                            if(self.volumeActual > 0 and self.actualPrice > 0):
                                self.stopSet = 0
                                self.totalContracts = 0
                                if(settings.ISOLATED_MARGIN_FACTOR > 1 and settings.FIXED_MARGIN_FLAG):
                                    self._contractStep = round(settings.ISOLATED_MARGIN_FACTOR*settings.CONTRACT_PCT*self.actualPrice*tools.XBt_to_XBT(self.available_margin['availableMargin']))/settings.RISK_DIVISOR
                                else:
                                    self._contractStep = round(settings.CONTRACT_PCT*self.actualPrice*tools.XBt_to_XBT(self.available_margin['availableMargin']))/settings.RISK_DIVISOR
                                lastPrice = tools.toNearest(self.actualPrice, self.tickSize)
                                for index in range(settings.TOTAL_STEP):
                                    #Regular gordo contract step
                                    orderBuy = self.exchange.format_order(round(self._contractStep * (1 + index)), lastPrice - self.prepare_order_static(index,self.priceStep,True),index)
                                    orders.append(orderBuy)
                                    orderSell = self.exchange.format_order(round(-(self._contractStep * (1 + index))), lastPrice + self.prepare_order_static(index,self.priceStep,False),index)
                                    orders.append(orderSell)
                                    # Total amount contracts for stops
                                    self.totalContracts = self.totalContracts + round(self._contractStep * (1+index))

                                
                                self.logger.info("Posting gradle orders")
                                sent_orders = self.exchange.create_bulk_orders(orders)
                                logger.log_orders(sent_orders)

                                # Stop market orders
                                self.logger.info("Posting stop orders")
                                self.stopMarketSell = self.stop_market('Sell')
                                self.stopMarketBuy = self.stop_market('Buy')
                                self.offset_index = 0

        # Filters conditions not met
        else:
            if(self.operationParameters['average_dollarMinute'] < settings.MIN_DM_CANCEL*settings.ENABLE_VOLUMAMP or 
                                    (self.operationParameters['amplitude'] < self.priceStep*2*settings.ENABLE_VOLUMAMP and self.operationParameters['amplitude'] > 0)
                                            or self.operationParameters['lockAnomaly']):
                # No position, keep waiting for better market conditions
                if(self.position[0]['currentQty'] == 0 ):
                    self.logger.info("Bitmex flow is too innocuous, halting every order")
                    self.exchange.cancel_every_order()
    def position_loop(self,side):
        '''Buy/sell position loop
        Cancel opposite side orders, post target and stop market'''

        found = False #Target
        foundStop = False
        switchOpenOrder={
            "Buy": tools.toNearest(self.positionPrice - settings.PROFIT_TARGET,self.tickSize),
            "Sell": tools.toNearest(self.positionPrice + settings.PROFIT_TARGET,self.tickSize),
        }
        toCancel = []
        # Order loop
        for openOrder in self.openOrders:
            if openOrder['ordType'] != 'Stop':
                if openOrder['side'] ==side:
                    if openOrder['price'] == switchOpenOrder.get(side):
                        if openOrder['orderQty'] == abs(self.positionContracts):
                            self.logger.info("Found target")
                            found = True
                        else:
                            toCancel.append(openOrder['orderID'])	
                    else:
                        self.logger.info("Appending order from the side: {0} and the order anyways {1}".format(side,openOrder))
                        toCancel.append(openOrder['orderID'])
            else:
                foundStop = True
                self.logger.info("Stop found {0}".format(openOrder))
                # Cancel opposite stop
                if(openOrder['side'] != side):
                    toCancel.append(openOrder['orderID'])

        # Double check for stop also for when the bot resets if cancels orderns in position
        if(not foundStop):
            self.logger.info('Stop not found')
            if(side == 'Sell'):
                self.exchange.place_order(quantity = -self.position[0]['currentQty'],price = self.actualPrice - 240,type_order='Stop',side ='Buy')
            elif(side == 'Buy'):
                self.exchange.place_order(quantity = -self.position[0]['currentQty'],price = self.actualPrice + 240,type_order='Stop',side ='Sell')
        
        # Cancels every order except for target
        if len(toCancel):
            self.logger.info("Deleting {0} orders".format(side))
            canceled_orders = self.exchange.cancel_bulk(toCancel)
            logger.log_orders(canceled_orders)

        if(found == False):
            # Checks if there is an open position and places target
            if(self.position[0]['currentQty']):
                while(self.positionPrice <= 0):
                    self.positionPrice = round(abs(self.position[0]['avgEntryPrice']))
                    self.logger.info("Position price is {0}".format(self.positionPrice))
                orderTarget = self.exchange.place_order(-self.position[0]['currentQty'], switchOpenOrder.get(side),target = side)
                self.logger.info("Placing target at {0}".format(orderTarget))

                logger.log_orders(orderTarget)
                settings._REACHED_TARGET = True
        #This is for canceling order gradle before
        if(self.operationParameters['lockAnomaly'] ):
            if(not self.aboveHighStep):
                self.logger.info('Lock anomaly is true and bot is above highStep')
            else:
                self.logger.info('Lock anomaly is true and bot is below highStep')

                
    def stop_market(self,side):
        '''
            Create the stop markets Orders to aviod account liquidation
            Currently creating stop on the place of settings.TOTAL_STEP + 1
        '''
        self.stopSet = 1
        lastPrice = tools.toNearest(self.actualPrice, self.tickSize)
        if(side == 'Buy'):
            orderStopMarket = self.exchange.place_order(quantity = -self.totalContracts,price = tools.toNearest(lastPrice - self.prepare_order_static(settings.TOTAL_STEP,self.priceStep,False),self.tickSize),type_order='Stop',side ='Buy')
        else:
            orderStopMarket = self.exchange.place_order(quantity = self.totalContracts,price = tools.toNearest(lastPrice + self.prepare_order_static(settings.TOTAL_STEP,self.priceStep,False),self.tickSize),type_order='Stop',side ='Sell')
        logger.log_orders(orderStopMarket)
        return orderStopMarket['orderID']

    def check_execution_status(self):
        '''
        Check through HTTP request the last execution and if it's one of a kind we are monitoring
        save it locally to avoid repetitions and set flags to send notifications accordingly
        '''
        # High step case
        _ExecStatusHighStep = ''
        _ExecStatusStop = ''
        _ExecStatusTarget = ''
        #Get last execution http request
        try:
            item = self.exchange.get_execution()[0]
            execution_flag = True
        except:
            item = ''
            execution_flag = False

        if(execution_flag):
        #check if it is not the same execution from last loop iteraction
            if(self.last_execution != item):
                self.logger.info("Execution: %s %d Contracts of %s at %.*f" %
                    (item['side'], item['cumQty'], item['symbol'],
                # here used to be tickLog but lets make it simple
                        1, item['stopPx'] if item['stopPx'] else (item['price'] or 0)))

                #save the execution on logs/exec_http_date.csv
                self.exec_logger.info("%s, %s, %s, %s, %s" %
                    (item['text'], item['side'], item['cumQty'], 
                        item['symbol'], item['stopPx'] if item['stopPx'] else (item['price'] or 0)))

            #Check notifications orders
            if item['cumQty'] > 0 and item['clOrdID'] != '':
                if str(item['clOrdID'][settings.GRADLE_INDICATOR_INIT:settings.GRADLE_INDICATOR_END]) == ('Buy' or 'Sel'):
                    self.step_number = item['clOrdID'][settings.GRADLE_NUMBER]
                    if int(item['clOrdID'][settings.GRADLE_NUMBER]) > settings.SEND_EMAIL_GRADLE:
                        self.aboveHighStep = True
                        if(self.botHighStepInfo != ''):
                            if(self.botHighStepInfo['orderID'] != item['orderID']):
                                settings._HIGH_STEP_ORDER = True
                                _ExecStatusHighStep = item
                        else:
                            settings._HIGH_STEP_ORDER = True
                            _ExecStatusHighStep = item
                    else:
                        self.aboveHighStep = False

                # Stop reached case
                elif str(item['clOrdID'][settings.STM_INDICATOR_INIT:settings.STM_INDICATOR_END]) == 'Stm':
                    if(self.botStopInfo != ''):
                        _ExecStatusStop = item
                        if(self.botStopInfo['orderID'] != item['orderID']):
                            settings._REACHED_STOP = True
                            current_stop_path = settings.LOG_DIR + 'last_stop.json'
                            with open(current_stop_path, 'w') as f:
                                json.dump(_ExecStatusStop, f)
                    else:
                        settings._REACHED_STOP = True
                        _ExecStatusStop = item
                        current_stop_path = settings.LOG_DIR + 'last_stop.json'
                        with open(current_stop_path, 'w') as f:
                            json.dump(_ExecStatusStop, f)

                # Target reached case
                elif str(item['clOrdID'][settings.STM_INDICATOR_INIT:settings.STM_INDICATOR_END]) == 'Tgt':
                    if(self._ExecStatusTarget != ''):
                        if(self._ExecStatusTarget['execID'] != item['execID']):
                            settings._REACHED_TARGET = True
                            _ExecStatusTarget = item
                    else:
                        settings._REACHED_TARGET = True
                        _ExecStatusTarget = item
        else:
            #Placing market orders on Bitmex 
            self.exchange.place_order(quantity = 1,price = 0,type_order='Market',side ='Buy')
            self.exchange.place_order(quantity = -1,price = 0,type_order='Market',side ='Sell')

        #Save last execution
        self.last_execution = item
        return [_ExecStatusHighStep,_ExecStatusStop,_ExecStatusTarget]

    def run_loop(self):
        '''
        Main bot loop
        operationParameters: highestPrice, lowestPrice, amplitude, Date, volume, lastPrice
        '''
        while(True):

            # Operation check
            with open (settings.LOG_DIR + 'operation.json', 'r') as op:
                operation = json.load(op)['operation']

            self.logger.info("=============================")
            self.logger.info("~: Main Loop :~")

            # Operation Parameters Request
            self.operationParameters = self.exchange.get_operationParameters("XBTUSD", settings.CANDLE_TIME_INTERVAL, "1m")
            self.actualPrice = self.operationParameters['lastPrice']
            self.volumeActual = round(self.operationParameters['volume'])
            
                        # Requesting HTTP needed info for bot operation
            self.available_margin = self.exchange.get_margin()
            self.position = self.exchange.http_get_position()
            self.instrument = self.exchange.get_instrument()[0]

            #Check if there is no open position open(HTTP request returns null when no position open)
            if(not len(self.position)):
                self.logger.info("position {}".format(self.position))
                self.liquidationPrice = 0
                self.positionPrice = 0
                self.positionContracts = 0
                self.leverage = None
                self.avgEntryPrice = 0
                self.breakEvenPrice = 0
            else:
                self.liquidationPrice = self.position[0]['liquidationPrice']
                self.positionPrice = self.position[0]['avgEntryPrice']
                self.positionContracts = self.position[0]['currentQty']
                self.leverage = self.position[0]['leverage']
                self.avgEntryPrice = self.position[0]['avgEntryPrice']
                self.breakEvenPrice = self.position[0]['breakEvenPrice']

            if(settings.FIXED_MARGIN_FLAG):
                if(self.leverage != None):
                    if(self.leverage != settings.ISOLATED_MARGIN_FACTOR):
                        self.exchange.isolate_margin('XBTUSD',settings.ISOLATED_MARGIN_FACTOR)
                    else:
                        self.logger.info('Leverage set to {0}'.format(settings.ISOLATED_MARGIN_FACTOR))
                else:
                    self.logger.info('no leverage to be setted for now')

            #Check client orders
            self.openOrders = self.exchange.http_open_orders()
            self.amountOpenOrders = len(self.openOrders)

            #Check client execution status 
            self.botHighStepInfo,self.botStopInfo,self._ExecStatusTarget = self.check_execution_status()

            # Calculating Bot Price Step and TickSize
            self.tickSize = self.instrument['tickSize']
            #try: # thats only for testnet bug
            self.priceStep = 10*round(self.actualPrice*settings.STEP_PCT/10)
            #except:
                #self.priceStep = self.priceStep  

            # Setting priceStep boundaries
            if self.priceStep < settings.MIN_STEP: 
                self.priceStep = settings.FIXED_STEP
            elif self.priceStep > settings.MAX_STEP:
                self.priceStep = settings.MAX_STEP
            # Fixed PriceStep, comment it if you want priceStep relative to bitcoin actual price
            self.priceStep = settings.FIXED_STEP

            if(self.available_margin['availableMargin'] > 0):
                #Check user balance if theres money
                self._profit_check()
                if(self.starting):
                    self.daily_balance = self.wallet_amount
                    self.starting = False

            #Notify if High Step Order executed
            if(settings._HIGH_STEP_ORDER):
                self.logger.info("High step order executed, alerting bot masters")
                settings._HIGH_STEP_ORDER = False

            #Notify if client been stopped
            if(settings._REACHED_STOP):
                self.available_margin = self.exchange.get_margin()
                profit_file_path = settings.FIN_DIR + 'initialBalance.json'
                with open(profit_file_path) as f:
                    checking_alterations = json.loads(f.read())
                    initial_balance = checking_alterations['initialBalance']

                loss = (self.available_margin['walletBalance'] - initial_balance)/initial_balance
        
                if(self.botStopInfo != ''):
                    self.logger.info('Bot stopped, check log')
                else:
                    self.logger.info('Check logs')
                self.logger.info("Stop order executed, halting bot for 1 day.")
                self.exchange.cancel_every_order()
                sleep(settings._SLEEP_FOR_ONE_DAY)
                settings._REACHED_STOP = False

            # Check if bot is ON or OFF
            if not(operation):
                self.logger.info("~: Bot is Paused :~")
            else:
                self.logger.info("~: Bot is Running :~") 

                # Check if user has minimun balance to operate
                if(self.available_margin['availableMargin'] > settings.MIN_FUNDS):

                    # Check if it's in position
                    if(self.positionContracts == 0):
                        self.logger.info("No open position, starting idle loop...")
                        self.post_gradle_orders()

                    elif(self.positionContracts < 0):
                        self.logger.info("Short position found, beginning Buy Target loop.")
                        self.position_loop('Buy')

                    elif(self.positionContracts > 0):
                        self.logger.info("Long position found, beginning Sell Target loop.")
                        self.position_loop('Sell')
                else:
                    self.logger.info('There are not enough funds on the account.')
                    raise SystemExit('Not enough funds on account')

            self.logger.info("Waiting %d seconds ..." % settings.LOOP_INTERVAL)
            self._data_dump()# write data to dashboard status

            # If day changes, restart
            res_date = datetime.datetime.today().strftime('%Y-%m-%d')
            res_path = str(settings.LOG_DIR + 'status_' + res_date + '.json')
            if not(os.path.exists(res_path)):
                sleep_time = random.uniform(0.1, 1)*self.SLEEP_TELEGRAM
                sleep(sleep_time)
                self.logger.warning('Day changed.')
                logger.log_error('Restarting...')
                sleep(self.SLEEP_TELEGRAM)
                self.restart()
            sleep(settings.LOOP_INTERVAL)