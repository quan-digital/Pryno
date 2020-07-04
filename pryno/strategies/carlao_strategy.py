# -*- coding: utf-8 -*-

# - Pryno Position Strategy -
# * Quan.digital *

from time import sleep
import datetime
import sys
import os
from os.path import getmtime
import random
import atexit
import traceback
import json
import pryno.util.mail as mail
import pryno.util.tools as tools
import pryno.util.settings as settings
import pryno.telegram_bot.quan_bot as telegram_bot
from pryno.util.api_bitmex import BitMEX
from pryno.util import logger
import numpy as np

# Used for reloading the bot - saves modified times of key files
watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]

class Carlao_Strategy:

    def __init__(self, bitmex_url="https://testnet.bitmex.com/api/v1/", force_operate=True):
        settings.STRATEGY_NAME = 'Carlao Strategy'
        logger.setup_error_logger()
        sys.excepthook = logger.log_exception
        atexit.register(self.__on_close)
        # self.logger = logger.setup_logger()
        self.logger = logger.setup_logbook(name="Carlao Strategy")
        self.logger.info("Pryno is starting.")
        self.SLEEP_TELEGRAM = settings.SLEEP_TELEGRAM

        # Setup loggers
        self.status_logger = logger.setup_dictlogger('status')
        self.wallet_logger = logger.setup_db('wallet')
        self.exec_logger = logger.setup_db('exec_http')

        # Initialize exchange
        self.symbol = settings.SYMBOL
        self.exchange = BitMEX(base_url=bitmex_url,
                symbol=self.symbol, apiKey=settings.BITMEX_KEY, apiSecret=settings.BITMEX_SECRET)

        # Class parameters
        self.wallet_amount = 0
        self.available_margin = {}
        self.instrument = {}
        self.actualPrice = 0
        self.last_execution = ''
        self.position = []
        self.starting = True
        self.quantity = 0
        self.above_price = 0
        self.below_price = 0

        ## State Machine ##
        self.reached_stop = False
        self.reached_target = False
        self.state_short = 0
        self.state_long = 0

        # Write operation file for bot control
        if force_operate:
            with open(settings.LOG_DIR + 'operation.json', 'w') as op:
                json.dump(dict(operation=True), op)

        
        telegram_bot.send_group_message(msg="🔁 Bot for {0} starting with strategy {1} v {2}".format(settings.CLIENT_NAME,
                settings.STRATEGY_NAME, settings.BOT_VERSION))

        self.logger.info("-\*---------------------|Pryno|---------------------*/-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("-\*                        .                        */-")
        self.logger.info("Pryno Carlao Strategy starting, connecting to BitMEX.")
        self.logger.info("Using symbol %s." % self.symbol)
        self.logger.info("Version 0.0")
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

        # Path for register the billing invoice from the client
        charging_file_path = settings.FIN_DIR + 'biling/'
        # getting bitmex wallet information
        wallet = self.exchange.get_funds()
        file_alter = False
        checking_alterations = {}
        self.wallet_amount = wallet['amount']
        self.logger.info('wallet info {0}'.format(self.wallet_amount))
        try:
            with open(profit_file_path) as f:
                checking_alterations = json.loads(f.read())
                payday = datetime.datetime.strptime(checking_alterations['dueDate'], "%Y-%m-%d %H:%M:%S.%f")

                # Deposits
                if wallet['deposited'] != checking_alterations['lastDeposit']:
                    delta = float(wallet['deposited']) - float(checking_alterations['lastDeposit'])
                    checking_alterations['lastDeposit'] = wallet['deposited']
                    checking_alterations['initialBalance'] = float(checking_alterations['initialBalance']) + delta
                    file_alter = True
                    # send thorugh telegram the deposited amount
                    telegram_bot.send_group_message(msg ="🔽 Client {0} deposited XBT to his account. Satoshis: {1} xBT".format(settings.CLIENT_NAME, delta))
                # Withdrawals
                if wallet['withdrawn'] != checking_alterations['lastWithdrawal']:
                    delta = float(wallet['withdrawn']) - float(checking_alterations['lastWithdrawal'])
                    checking_alterations['lastWithdrawal'] = wallet['withdrawn']
                    checking_alterations['initialBalance'] = float(checking_alterations['initialBalance']) - delta
                    file_alter = True
                    telegram_bot.send_group_message(msg ="🔼 Client {0} withdrew {1} XBT from his account. Balance: {2} XBT.".format(settings.CLIENT_NAME, tools.XBt_to_XBT(delta), tools.XBt_to_XBT(float(checking_alterations['initialBalance']))))
                # Register the amount owed from client to us and renew bot operation for the next week to come
                if  payday < datetime.datetime.now():
                    start_date = datetime.datetime.strptime(checking_alterations['timestamp'],"%Y-%m-%d %H:%M:%S.%f")
                    totalProfit = float(self.wallet_amount) - float(checking_alterations['initialBalance'])
                    client_debt = totalProfit/2
                    self.logger.info('Mister {0} owns Quan Digital a total of {1} BTC'.format(checking_alterations['clientName'], tools.XBt_to_XBT(client_debt)))
                    operationweek = int((payday-start_date).days/7)
                    charging_file_path = charging_file_path + 'week' + str(operationweek)
                    chargefile = {
                        'totalProfit': totalProfit,
                        'client_debt': client_debt,
                        'client_name': settings.CLIENT_NAME,
                        'profit_file_last_week': checking_alterations
                    }
                    #Mail the Quan board about the amount owed
                    mailMessage = str("Hello Admins," \
                    + " it's payday and {0} owns us a total of {1} BTC,".format(checking_alterations['clientName'], tools.XBt_to_XBT(client_debt)) \
                    + " his total profit was {0}".format(tools.XBt_to_XBT(totalProfit)))
                    mail.send_email(mailMessage,settings.MAIL_ACTIVITY)
                    with open(charging_file_path,'w') as bills:
                        json.dump(chargefile,bills)

                    newpayday = payday + datetime.timedelta(days=7)
                    checking_alterations['initialBalance'] = self.wallet_amount
                    checking_alterations['dueDate'] = str(newpayday)
                    file_alter = True
                    # #---------------TODO--------------------------------------------
                    #create condition do raise up risk divisor after 24 hours and stop it after 4 days
                    #probably schedule a function for it and set a boolean true with a timestamp
                    # we could link with deposit check or simple button confirmation at admin dashboard
                    #send email automatically(probably only after infra ready) but get the quan billing template and rewrite on the needed fields
                    #if you read this congratulation!! sent me a message saying 'alleblaus hot potatto' so I can see that you're cool

            #If there's change write again over balance file
            if(file_alter == True):
                with open(profit_file_path,'w') as f:
                    f.seek(0) 
                    json.dump(checking_alterations, f)

        #Client first week with the bot operating at his account
        except FileNotFoundError:
            start_date = datetime.datetime.now()
            payday = start_date + datetime.timedelta(days=7)
            #wallet = self.exchange.get_funds()
            profit_data = {
                'timestamp': str(start_date),
                'initialBalance': self.wallet_amount,
                'lastDeposit': wallet['deposited'],
                'lastWithdrawal': wallet['withdrawn'],
                'dueDate': str(payday),
                'clientName': settings.CLIENT_NAME 
            }

            with open(profit_file_path,'w') as f:
                json.dump(profit_data, f)

        #If profit check callback fails notify through email
        except: 
            mail.send_email('Some weird error at \
                                Profit check {0} '.format(traceback.format_exc()), settings.MAIL_TO_ERROR)

    def exit(self):
        self.__on_close()

    def __on_close(self):
        '''Handling exit.'''
        if(self.position):
            if self.position[0]['currentQty'] == 0:
                self.exchange.cancel_every_order()
                self.logger.info('No positions, all orders cancelled.')
                telegram_bot.send_group_message(msg=' ✅ No position, all orders cancelled and bot paused for {0}'.format(settings.CLIENT_NAME))
            else:
                self.logger.warning('Position found, orders still active!')
                mailMessage = str('🚨🚨🚨 Position found, and bot its turning off, orders still active for {0}:'.format(settings.CLIENT_NAME))
                telegram_bot.send_group_message(msg =mailMessage)
                #mail.send_email(mailMessage)
        else:
            telegram_bot.send_group_message(msg ='✅ No position and no open orders, bot is shutting down for {0}'.format(settings.CLIENT_NAME))
        # os.popen('killall python3')
        # sys.exit(0)

    def check_execution_status(self):
        '''
        Check through HTTP request the last execution and if it's one of a kind we are monitoring
        save it locally to avoid repetitions and set flags to send notifications accordingly
        '''
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
                    
                    # Stop reached case
                    if str(item['clOrdID'][settings.STM_INDICATOR_INIT:settings.STM_INDICATOR_END]) == 'Stm':
                        self.reached_stop = True  
                        
                    # Target reached case
                    elif str(item['clOrdID'][settings.STM_INDICATOR_INIT:settings.STM_INDICATOR_END]) == 'Tgt':
                        self.reached_target = True   
        else:
            #Placing market orders on Bitmex 
            self.exchange.place_order(quantity = 1,price = 0,type_order='Market',side ='Buy')
            self.exchange.place_order(quantity = -1,price = 0,type_order='Market',side ='Sell')

        #Save last execution
        self.last_execution = item
        return item
   
    def daily_digest(self):
        '''Daily profits digest for bot.'''

        profit_file_path = settings.FIN_DIR + 'initialBalance.json'
        with open(profit_file_path,'r') as f:
            client_info = json.loads(f.read())

        message_time = datetime.datetime.now()
        profit = (self.wallet_amount - self.daily_balance)/self.daily_balance 
        message  = "☑️ A day has passed, now its {0}/{1} and {2} had a gain of {3:.2%},\
        now his balance is {4} XBT".format(str(message_time.month),str(message_time.day),
            settings.CLIENT_NAME,profit,tools.XBt_to_XBT(self.wallet_amount))
        telegram_bot.send_group_message(msg=message)
        sleep_time = random.uniform(0.1, 1)*self.SLEEP_TELEGRAM
        sleep(sleep_time)

    def calc_correcao(self,N1,N2):
        SSC1 = 2/(N1+1) #rápida
        SSC2 = 2/(N2+1) #lenta
        a1= 1 - SSC1
        a2= 1 - SSC2
        return (a2-a1)/((1-a1)*(1-a2))
    
    def calc_med_ema(self,candles,N):
        ema = np.zeros(len(candles))
        ema[0] = candles[0]
        SSC = 2/(N+1)
        for i in range(1,len(candles)):            
            ema[i] = ema[i-1]*(1-SSC) + candles[i]*SSC
        return ema

    def MACD(self,candles,N1,N2,N3):
        correcao = self.calc_correcao(N1,N2)
        emaN1 = self.calc_med_ema(candles,N1)
        emaN2 = self.calc_med_ema(candles,N2)
        linha_MACD = (emaN1 - emaN2)/correcao # rápida - lenta (1 derivada)
        linha_sinal = self.calc_med_ema(linha_MACD,N3) # lenta
        return linha_sinal[-1]

    def sorting_index(self,candles,N=130,prec=1e-3):
        # Obtém séries de dados ordenadas de forma crescente e decrescente
        # Critério de corte em 92% e 130 periodos
        
        y_alta = np.sort(candles)
        y_queda = y_alta[::-1]
        den =  np.sum(np.power((candles - np.mean(candles)),2))

        # Cálcula R2 de alta
        num_H =  np.sum(np.power((candles - y_alta),2))
        R2_alta  = (100*(1 - num_H/(den+prec))) if (100*(1 - num_H/(den+prec))) > 0 else 0
        
        # Cálcula R2 de queda
        num_L =  np.sum(np.power((candles - y_queda),2))
        R2_queda  = (100*(1 - num_L/(den+prec))) if (100*(1 - num_L/(den+prec))) > 0 else 0
    
        # Tomada de decisão: Qual a tendência preponderante
        if R2_alta > R2_queda:
            R2 = R2_alta
        else:
            R2 = -R2_queda
        return R2

    def run_loop(self):
        '''
        Main bot loop
        operationParameters: lastPrice
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
            #telegram_bot.send_group_message('the actual price {} for {}, '.format(self.actualPrice,settings.CLIENT_NAME))		

            # Requesting HTTP needed info for bot operation
            self.available_margin = self.exchange.get_margin()
            self.position = self.exchange.http_get_position()
            self.instrument = self.exchange.get_instrument()[0]
            #Getting candles for MACD avaliarion
            self.candles = self.exchange.get_close("XBTUSD", settings.CANDLE_TIME_INTERVAL, "1m")

            #Check client execution status 
            self.check_execution_status()
            
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

            #Definir em quanto quer alavancar o bot
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

            # Define  entry quantity, stop and target
            self.quantity = round(tools.XBt_to_XBT(self.available_margin['availableMargin']) * self.actualPrice * settings.ISOLATED_MARGIN_FACTOR *0.98)
            self.above_price = tools.toNearest(self.actualPrice * 1.003)
            self.below_price = tools.toNearest(self.actualPrice * 0.997)

            self.logger.info("/////////////////////////////")
            self.logger.info('------TESTE PARÂMETROS-------')
            self.logger.info("=============================")
            self.logger.info('Sorting Index: {}'.format(self.sorting_index(self.candles)))
            self.logger.info('MACD Long: {}'.format(self.MACD(self.candles,84,182,63)))
            self.logger.info('MACD Short: {}'.format(self.MACD(self.candles,7, 14, 13)))
            self.logger.info('walletBalance in Dol: {}'.format(tools.toNearest(tools.XBt_to_XBT(self.exchange.get_margin()['walletBalance']) * self.actualPrice)))
            self.logger.info('walletBalance in XBT: {}'.format(round(tools.XBt_to_XBT(self.exchange.get_margin()['walletBalance']),8)))
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")
            self.logger.info('position Contracts: {}'.format(self.positionContracts))
            self.logger.info('open orders {}'.format(self.amountOpenOrders))
            self.logger.info('State Short: {}'.format(self.state_short))
            self.logger.info('State Long: {}'.format(self.state_long))
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")
            self.logger.info('lquantity {}'.format(self.quantity))
            self.logger.info('above_price {}'.format(self.above_price))
            self.logger.info('below_price {}'.format(self.below_price))
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")
            self.logger.info("/////////////////////////////")

            # If reached Stop Loss   
            if self.reached_stop:
                self.state_short = 0
                self.state_long = 0
                self.exchange.cancel_every_order()
                self.reached_stop = False

                # Notify if Stop order was executed
                telegram_message = "🛑 Stop order executed for {0} at ${1}".format(
                                settings.CLIENT_NAME,self.last_execution["stopPx"])
                telegram_bot.send_group_message(msg =telegram_message)

            # If reached Profit Target
            if self.reached_target:
                self.state_short = 0
                self.state_long = 0
                self.exchange.cancel_every_order()
                self.reached_target = False

                # Notify if Profit target order was executed
                telegram_message = "✅ Profit Target order executed for {0} at ${1}".format(
                                settings.CLIENT_NAME,self.last_execution["price"])
                telegram_bot.send_group_message(msg =telegram_message)
            
            if(self.available_margin['availableMargin'] > 0):
                #Check user balance if theres money
                self._profit_check()
                if(self.starting):
                    self.daily_balance = self.wallet_amount
                    self.starting = False

            # Check if bot is ON or OFF
            if not(operation):
                self.logger.info("~: Bot is Paused :~")
            else:
                self.logger.info("~: Bot is Running :~") 

                # # Check if user has minimun balance to operate
                # if(self.available_margin['availableMargin'] > settings.MIN_FUNDS):
                	
                #Maquina de estados estratégia carlão
                print('State Machine for bot operation')
                if self.positionContracts == 0:
            
                    # self.exchange.place_order(quantity = self.quantity,price = 0, type_order='Market', side ='Buy')
                    # telegram_message = "🚨 TESTE Long entry found for {0} at ${1}".format(
                    #                 settings.CLIENT_NAME,self.actualPrice)
                    # telegram_bot.send_group_message(msg =telegram_message)

                    # self.exchange.place_order(quantity = -self.quantity,price = self.below_price,type_order='Stop',side ='Buy')
                    # self.exchange.place_order(quantity= -self.quantity, price= self.above_price,type_order = 'Limit', side = 'Buy', target= 'Buy')

                    # Long / Tendência de alta
                    if self.MACD(self.candles,84,182,63) > 0 and self.sorting_index(self.candles) > 85:
                        # Condição necessária  (convergência: linhas de mesmo sinal)
                        if self.MACD(self.candles,7,14,13) > self.MACD(self.candles,84,182,63) and self.state_long == 0:
                            self.state_long = 1

                            telegram_message = 'STATE LONG 1 REACHED'
                            telegram_bot.send_group_message(msg =telegram_message)

                        # Condição suficiente 1 (princípio da divergência) (sinal opostos)
                        if self.MACD(self.candles,7,14,13) < 0 and self.state_long == 1:
                            self.exchange.place_order(quantity = self.quantity,price = 0, type_order='Market', side ='Buy')
                            self.exchange.place_order(quantity = -self.quantity,price = self.below_price,type_order='Stop',side ='Buy')
                            self.exchange.place_order(quantity= -self.quantity, price= self.above_price,type_order = 'Limit', side = 'Buy', target= 'Buy')
                            self.state_long = 2
                        
                            telegram_message = "🚨 Long entry found for {0} at ${1}".format(
                                        settings.CLIENT_NAME,self.actualPrice)
                            telegram_bot.send_group_message(msg =telegram_message)

                    # Short / Tendência de queda
                    elif self.MACD(self.candles,84,182,63) < 0 and self.sorting_index(self.candles) < -85:
                        # Condição necessária (convergência: linhas de mesmo sinal)
                        if self.MACD(self.candles,7,14,13)< self.MACD(self.candles,84,182,63) and self.state_short == 0:
                            self.state_short = 1

                            telegram_message = 'STATE SHORT 1 REACHED'
                            telegram_bot.send_group_message(msg =telegram_message)

                        #  %Condição suficiente 1 (princípio da divergência) (sinais opostos)
                        if self.MACD(self.candles,7,14,13) > 0 and self.state_short == 1:
                            self.exchange.place_order(quantity = -self.quantity,price = 0, type_order='Market', side ='Sell')       
                            self.exchange.place_order(quantity = self.quantity,price = self.above_price,type_order='Stop',side ='Sell')
                            self.exchange.place_order(quantity= self.quantity,price = self.below_price,type_order = 'Limit', side = 'Sell', target= 'Sell')
                            self.state_short = 2 

                            telegram_message = "🚨 Short entry found for {0} at ${1}".format(
                                    settings.CLIENT_NAME,self.actualPrice)
                            telegram_bot.send_group_message(msg =telegram_message)
                    else:
                        if (self.state_short == 1) or (self.state_long == 1):
                            telegram_message = 'NON TREND RESET AFTER STATE 1'
                            telegram_bot.send_group_message(msg =telegram_message)
                        self.state_short = 0
                        self.state_long = 0

                elif (self.positionContracts > 0 and self.state_long == 2) or (self.positionContracts < 0 and self.state_short == 2):
                    if self.amountOpenOrders != 2:
                        self.exchange.cancel_every_order()
                        self.state_short = 0
                        self.state_long = 0

                        telegram_message = 'DIVERGANCE IN CONTRACTS, CANCELING ALL ORDERS AND RESET STATE'
                        telegram_bot.send_group_message(msg =telegram_message)

                # else:
                #     self.logger.info('There are not enough funds on the account.')
                #     # telegram_bot.send_group_message(msg ='💲There are not enough funds on client {1} account, turning bot off.'.format(
                #     #                                 settings.CLIENT_NAME))
                #     raise SystemExit('Not enough funds on account')

            self.logger.info("Waiting %d seconds ..." % settings.LOOP_INTERVAL)
            self._data_dump()# write data to dashboard status

            # If day changes, restart
            res_date = datetime.datetime.today().strftime('%Y-%m-%d')
            res_path = str(settings.LOG_DIR + 'status_' + res_date + '.json')
            if not(os.path.exists(res_path)):
                sleep_time = random.uniform(0.1, 1)*self.SLEEP_TELEGRAM
                sleep(sleep_time)
                self.daily_digest()
                self.logger.warning('Day changed.')
                logger.log_error('Restarting...')
                sleep(self.SLEEP_TELEGRAM)
                self.restart()
            sleep(settings.LOOP_INTERVAL)