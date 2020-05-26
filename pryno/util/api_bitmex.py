# -*- coding: utf-8 -*-

# - Bitmex API Wrapper -
# * Quan.digital *

# author: canokaue & claudiovb
# date: 01/02/2020
# kaue.cano@quan.digital

# HTTP functions on top of _curl_bitmex for order
# manipulation.

# Bimex times out Keep Alive sessions after 90 seconds
# so a session timeout at 60 seconds is implemented in 
# order to get fast, persistent performance.

# https://www.bitmex.com/api/explorer/
# https://www.bitmex.com/api/explorer/#!/Order/Order_new

import requests
import json
import time
import datetime as dt
import base64
import sys
import uuid
from pryno.util.api_auth import APIKeyAuthWithExpires
import pryno.util.settings as settings
import pryno.util.logger as logger
from pryno.util import tools

class BitMEX(object):

    """BitMEX API Connector."""
    def __init__(self, base_url=None, symbol=None, apiKey=None, apiSecret=None):
        """Init connector."""
        logger.setup_error_logger()
        sys.excepthook = logger.log_exception
        self.logger = logger.setup_logbook('api')
        self.base_url = base_url
        self.symbol = symbol
        self.postOnly = settings.POST_ONLY
        if (apiKey is None):
            logger.log_error("Set an API key and Secret.")
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.orderIDPrefix = str(settings.BOT_NAME + "_" + settings.BOT_VERSION)
        if len(self.orderIDPrefix) > 13:
            logger.log_error("Order prefix must be at most 13 characters long!")

        self.retries = 0  # initialize counter

        # Prepare HTTPS session
        self.session = requests.Session()
        # These headers are always sent
        self.session.headers.update({'user-agent': 'pryno'})
        self.session.headers.update({'content-type': 'application/json'})
        self.session.headers.update({'accept': 'application/json'})

        self.timeout = settings.API_TIMEOUT
        self._lastPrice = 0

    def __del__(self):
        self.exit()

    def exit(self):
        self.logger.info('Bitmex API closed.')
        self.logger.removeHandler(self.logger.handlers[0])
        print('Bitmex API closed.')

    #
    # Public methods
    #

    def get_full_status(self,lastPrice,operationParameters,wallet_balance,amountOpenOrders,openOrders,
                    positionQty,positionLeverage,liquidationPrice,unrealisedPnl,realisedPnl,
                       avgEntryPrice,breakEvenPrice,unrealisedProfit,availableMargin,markPrice,
                         fundingRate,volumeInst,bidPrice,askPrice):
        #operationParameters = self.get_operationParameters("XBTUSD",CANDLE_TIME_INTERVAL,"1m")
        my_orders = [(order['side'], order['orderQty'],order['price'] if order['price'] else order['stopPx'],
            order['text']) for order in openOrders]
        status_dict = {'timestamp' : str(dt.datetime.now()),
                'latest_price' : lastPrice,
                'mark_price' : markPrice,
                'balance' : wallet_balance,
                'order_num' : amountOpenOrders,
                'open_orders' : my_orders,
                'position' : positionQty,
                'leverage' : positionLeverage,
                'liquidation' : liquidationPrice,
                'funding_rate' : fundingRate,
                'unrealized_pnl' : unrealisedPnl,
                'realized_pnl' : realisedPnl,
                'volume' : volumeInst,
                'avg_entry_price' : avgEntryPrice,
                'break_even' : breakEvenPrice,
                'unrealized_profit' : unrealisedProfit,
                'available_margin' : availableMargin,
                'dollar_minute' : operationParameters['average_dollarMinute'],
                'amplitude' : operationParameters['amplitude'],
                'highest_price' : operationParameters['highestPrice'],
                'lowest_price' : operationParameters['lowestPrice'],
                'ask_price' : askPrice,
                'bid_price' : bidPrice,
                'lock_anomaly' : operationParameters['lockAnomaly']
                }
        return status_dict


    def instruments(self, filter=None):
        query = {}
        if filter is not None:
            query['filter'] = json.dumps(filter)
        return self._curl_bitmex(path='instrument', query=query, verb='GET')



    def get_instrument(self):
        path = 'instrument'
        postdict={
            'symbol':'XBTUSD',
            'count': 1
        }
        return self._curl_bitmex(path='instrument', postdict=postdict, verb='GET')
    #
    # Authentication required methods
    #
    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not (self.apiKey):
                logger.log_error("You must be authenticated to use this method")
            else:
                return fn(self, *args, **kwargs)
        return wrapped

    @authentication_required
    def isolate_margin(self, symbol, leverage, rethrow_errors=False):
        """Set the leverage on an isolated margin position"""
        path = "position/leverage"
        postdict = {
            'symbol': symbol,
            'leverage': leverage
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="POST", rethrow_errors=rethrow_errors)


    @authentication_required
    def place_order(self, quantity, price, target = '',type_order = 'Limit', side = ' '):
        """Place an order."""
        if price < 0:
            logger.log_error("Price must be positive.")

        endpoint = "order"
        # Generate a unique clOrdID with our prefix so we can identify it.
        if(target == ''):
            if type_order == 'Stop':  
                clOrdID = self.orderIDPrefix + '_Stm' + side[0] + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
                postdict = {
                    'symbol': self.symbol,
                    'orderQty': quantity,
                    'stopPx': price,
                    'clOrdID': clOrdID,
                    'ordType': type_order,
                    'execInst': 'LastPrice',
                    'text': 'Stm'+side[0]
                }
            elif type_order == 'Market':
                clOrdID = self.orderIDPrefix + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
                postdict = {
                    'symbol': self.symbol,
                    'orderQty': quantity,
                    'clOrdID': clOrdID,
                    'ordType': type_order
                }
            else: 
                clOrdID = self.orderIDPrefix + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
                postdict = {
                    'symbol': self.symbol,
                    'orderQty': quantity,
                    'price': price,
                    'clOrdID': clOrdID,
                    'ordType': type_order
                }

            
            
        else:
            clOrdID = self.orderIDPrefix + '_Tgt' + target[0] + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
            postdict = {
                'symbol': self.symbol,
                'orderQty': quantity,
                'price': price,
                'clOrdID': clOrdID,
                'text': 'Target' + target[0]
            }


        return self._curl_bitmex(path=endpoint, postdict=postdict, verb="POST", max_retries= settings.ORDER_MAX_RETRIES)


    def format_order(self, quantity, price, orderNumber):

        if price < 0:
            logger.log_error("Price must be positive.")

        if quantity > 0:
            #order['side'] = 'Buy'
            Sufix = 'Buy'
        else:
            #order['side'] = 'Sell'
            Sufix = 'Sel'

        # Generate a unique clOrdID with our prefix so we can identify it.
        clOrdID = self.orderIDPrefix + '_' + Sufix + str(orderNumber) + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
        #clOrdID = ''
        postdict = {
            'symbol': self.symbol,
            'orderQty': quantity,
            'price': price,
            'clOrdID': clOrdID,
            'text': Sufix + str(orderNumber)
        }
        return postdict

    # Broken
    @authentication_required
    def amend_bulk_orders(self, orders):
        """Amend multiple orders."""
        # Note rethrow; if this fails, we want to catch it and re-tick
        return self._curl_bitmex(path='order/bulk', postdict={'orders': orders}, verb='PUT', rethrow_errors=True)
    

    @authentication_required
    def create_bulk_orders(self, orders):
        """Create multiple orders."""
        for order in orders:
           # order['clOrdID'] = self.orderIDPrefix + base64.b64encode(uuid.uuid4().bytes).decode('utf8').rstrip('=\n')
            order['symbol'] = self.symbol
            if self.postOnly:
                order['execInst'] = 'ParticipateDoNotInitiate'
        return self._curl_bitmex(path='order/bulk', postdict={'orders': orders}, verb='POST',max_retries=settings.ORDER_MAX_RETRIES)

    @authentication_required
    def http_open_orders(self):
        """Get open orders via HTTP. Used on close to ensure we catch them all."""
        path = "order"
        orders = self._curl_bitmex(
            path=path,
            query={
                'filter': json.dumps({'ordStatus.isTerminated': False, 'symbol': self.symbol}),
                'count': 500
            },
            verb="GET",
            max_retries= settings.HTTP_MAX_RETRIES
        )
        # Only return orders that start with our clOrdID prefix.
        return [o for o in orders if str(o['clOrdID']).startswith(self.orderIDPrefix)]

    @authentication_required
    def orders_history(self):
        """Get open orders via HTTP. Used on close to ensure we catch them all."""
        path = "order"
        startDate = (dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        orders = self._curl_bitmex(
            path=path,
            query={
                'filter': json.dumps({'ordStatus.isTerminated': False, 'symbol': self.symbol}),
                'count': 500,
                'startTime': startDate,
                'endTime': dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            verb="GET",
            max_retries= settings.HTTP_MAX_RETRIES
        )
        # Only return orders that start with our clOrdID prefix.
        return [o for o in orders if str(o['clOrdID']).startswith(self.orderIDPrefix)]


    @authentication_required
    def http_get_position(self):
        
        http_position = self._curl_bitmex(path = "position",
            verb="GET",
            max_retries= settings.HTTP_MAX_RETRIES)

        return http_position

    def get_candles(self,symbol,count,size):
        candlesHistory = self._curl_bitmex(
            path="trade/bucketed",
            verb="GET",
            query={
                "symbol":  symbol,
                "count":   count,
                "reverse": True,
                "partial": False,
                "binSize": size
            }
        )
        return candlesHistory


    def get_operationParameters(self,symbol,count,size):
        candlesHistory = self.get_candles(symbol,count,size)
        if(candlesHistory == None):
            raise Exception("Error fetching candle history")
        arrayPriceClose = []
        arrayPriceHigh = []
        arrayPriceLow = []
        arrayPriceVolume = []
        arrayPriceOpen = []
        arrayDate = []
        arrayTrade = []
        arrayClose = []
        lockAnomaly = False
        for candles in candlesHistory:
            arrayPriceClose.append(candles['close'])
            if candles['high'] != None:
                arrayPriceHigh.append(candles['high'])
            if candles['low'] != None:
                arrayPriceLow.append(candles['low'])
            arrayPriceVolume.append(candles['volume'])
            arrayPriceOpen.append(candles['open'])
            arrayDate.append(candles['timestamp'])
            arrayTrade.append(candles['trades'])
            arrayClose.append(candles['close'])
        auxSum = sum(arrayPriceVolume)
        highestPrice = max(arrayPriceHigh)
        lowestPrice = min(arrayPriceLow)
        amplitude = round(highestPrice - lowestPrice)
        average_dollarMinute = round(auxSum/count)
        auxTrade = sum(arrayTrade)
        countLoopAnomaly = 14
        majorVolume = 0
        avgTrade = auxSum/auxTrade
        if avgTrade >= 3000:
            countLoopAnomaly = 25
        for index in range(0,countLoopAnomaly):
            if(arrayPriceVolume[index] > settings.VOLUME_TOLERANCE):
                lockAnomaly = True
                if(majorVolume < arrayPriceVolume[index]):
                    majorVolume = arrayPriceVolume[index]

        # Immediate amplitudes
        current_close = candlesHistory[0]['close']
        amp1m = abs(current_close - candlesHistory[1]['close'])
        amp5m = max(arrayClose[:5]) - min(arrayClose[:5])

        if self._lastPrice:
            delta_amp = abs(current_close - self._lastPrice)
            self._lastPrice = current_close
        else:
            delta_amp = None
            self._lastPrice = current_close

        parameters = {
            'highestPrice': highestPrice,
            'lowestPrice': lowestPrice,
            'amplitude': amplitude,
            'delta_amp' : delta_amp,
            'amp1m' : amp1m,
            'amp5m' : amp5m,
            'average_dollarMinute': average_dollarMinute,
            'Date': arrayDate[0],
            'volume': arrayPriceVolume[len(arrayPriceVolume) - 2],
            'lockAnomaly': lockAnomaly,
            'lastPrice': arrayPriceClose[0],
            'major_volume': majorVolume,
            'avgTrade': avgTrade
        }

        return parameters


    @authentication_required
    def cancel(self, orderID):
        """Cancel an existing order."""
        path = "order"
        postdict = {
            'orderID': orderID,
        }

        return self._curl_bitmex(path=path, postdict=postdict, verb="DELETE")

    @authentication_required
    def cancel_bulk(self, orders):
        path = "order"
        postdict = {
            'orderID': orders,
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="DELETE")

    @authentication_required
    def cancel_every_order(self):
        self.logger.info("Resetting current position. Canceling all existing orders.")
        path = "order/all"
        postdict = {
            'symbol':"XBTUSD"
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="DELETE")

    # ExchangeInterface
    @authentication_required
    def cancel_order(self, order):
        tickLog = 1
        self.logger.info("Canceling: %s %d @ %.*f" % (order['side'], order['orderQty'], tickLog, order['price']))
        while True:
            try:
                self.cancel(order['orderID'])
                time.sleep(1)
            except ValueError as e:
                self.logger.info(e)
                time.sleep(1)
            else:
                break

    # ExchangeInterface
    @authentication_required
    def cancel_all_orders(self):
        self.logger.info("Resetting current position. Canceling all existing orders.")

        # In certain cases, a WS update might not make it through before we call this.
        # For that reason, we grab via HTTP to ensure we grab them all.
        orders = self.http_open_orders()

        for order in orders:
            self.logger.info("Canceling: %s %d @ %.*f" % (order['side'], order['orderQty'], order['price']))

        if len(orders):
            self.cancel([order['orderID'] for order in orders])

        time.sleep(1)

    @authentication_required
    def withdraw(self, amount, fee, address):
        path = "user/requestWithdrawal"
        postdict = {
            'amount': amount,
            'fee': fee,
            'currency': 'XBt',
            'address': address
        }
        return self._curl_bitmex(path=path, postdict=postdict, verb="POST", max_retries=0)


    @authentication_required
    def get_margin(self):
        path = "user/margin"
        # postdict = {
        #     'currency': 'XBt'
        # }
        return self._curl_bitmex(path=path,verb="GET")


    @authentication_required
    def get_funds(self):
        path = "user/wallet"

        return self._curl_bitmex(path=path,verb="GET")


    @authentication_required
    def get_fundsHistory(self,startDate):
        path = "user/walletHistory"
        postdict = {
            'currency': 'XBt',
            'count': 100,
            'start': startDate
        }
        self.logger.info('Here we are')
        return self._curl_bitmex(path=path,postdict=postdict,verb="GET")



    @authentication_required
    def get_executionHistory(self,startDate):
        path = "user/executionHistory"
        postdict = {
            'symbol': 'XBTUSD',
            'timestamp': startDate
        }
        return self._curl_bitmex(path=path,postdict=postdict,verb="GET")

    @authentication_required
    def get_execution(self):
        path = "execution"
        postdict = {
            'symbol': 'XBTUSD',
            'reverse': True,
            'count': 1
        }
        return self._curl_bitmex(path=path,postdict=postdict,verb="GET")

    def getLastPrice(self):
        LastBtc = self._curl_bitmex(
            path="trade?symbol=XBTUSD&count=1&reverse=true",
            verb="GET"
        )
        # Only return orders that start with our clOrdID prefix.
        return [LastBtc[0]['price']]
        


    def _curl_bitmex(self, path, query=None, postdict=None, timeout=None, verb=None, rethrow_errors=False,
                     max_retries=None):
        """Send a request to BitMEX Servers."""
        # Handle URL
        url = self.base_url + path

        if timeout is None:
            timeout = self.timeout

        # Default to POST if data is attached, GET otherwise
        if not verb:
            verb = 'POST' if postdict else 'GET'

        # By default don't retry POST or PUT. Retrying GET/DELETE is okay because they are idempotent.
        # In the future we could allow retrying PUT, so long as 'leavesQty' is not used (not idempotent),
        # or you could change the clOrdID (set {"clOrdID": "new", "origClOrdID": "old"}) so that an amend
        # can't erroneously be applied twice.
        if max_retries is None:
            max_retries = 0 if verb in ['POST', 'PUT'] else 3

        # Auth: API Key/Secret
        auth = APIKeyAuthWithExpires(self.apiKey, self.apiSecret)

        def exit_or_throw(e):
            if rethrow_errors:
                raise e
            else:
                exit(1)

        def retry():
            self.retries += 1
            if self.retries > max_retries:
                logger.log_error("Max retries on %s (%s) hit, raising." % (path, json.dumps(postdict or '')))
            return self._curl_bitmex(path, query, postdict, timeout, verb, rethrow_errors, max_retries)

        # Make the request
        response = None
        try:
            #self.logger.info("sending req to %s: %s" % (url, json.dumps(postdict or query or '')))
            req = requests.Request(verb, url, json=postdict, auth=auth, params=query)
            prepped = self.session.prepare_request(req)
            response = self.session.send(prepped, timeout=timeout)
            # Make non-200s throw
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            if response is None:
                raise e

            # 401 - Auth error. This is fatal.
            if response.status_code == 401:
                self.logger.error("API Key or Secret incorrect, please check and restart.")
                self.logger.error("Error: " + response.text)
                if postdict:
                    self.logger.error(postdict)
                # Always exit, even if rethrow_errors, because this is fatal
                exit(1)

            # 502 - Bitmex Bad Gateway error, just chill and retry
            if response.status_code == 502:
                self.logger.error("Bad Gateway, retrying.")
                self.logger.error("Error: " + response.text)
                self.logger.info("Waiting %s seconds for retry..." % settings.HTTP_RETRY_TIME)
                time.sleep(settings.HTTP_RETRY_TIME)
                # Retry the request.
                return retry()

            # 500 - Bitmex Maintenance error, just chill and retry
            if response.status_code == 500:
                self.logger.error("Bitmex internal deploy, retrying.")
                self.logger.error("Error: " + response.text)
                self.logger.info("Waiting %s seconds for retry..." % settings.HTTP_RETRY_TIME)
                time.sleep(settings.HTTP_RETRY_TIME)
                # Retry the request.
                return retry()

            # 404, can be thrown if order canceled or does not exist.
            elif response.status_code == 404:
                if verb == 'DELETE':
                    self.logger.error("Order not found: %s" % postdict['orderID'])
                    return
                self.logger.error("Unable to contact the BitMEX API (404). " +
                                  "Request: %s \n %s" % (url, json.dumps(postdict)))
                exit_or_throw(e)

            # 429, ratelimit; cancel orders & wait until X-RateLimit-Reset
            elif response.status_code == 429:
                self.logger.error("Ratelimited on current request. time.Sleeping, then trying again. Try fewer " +
                                  "order pairs or contact support@bitmex.com to raise your limits. " +
                                  "Request: %s \n %s" % (url, json.dumps(postdict)))

                # Figure out how long we need to wait.
                ratelimit_reset = response.headers['X-RateLimit-Reset']
                to_sleep = int(ratelimit_reset) - int(time.time())
                reset_str = dt.datetime.fromtimestamp(int(ratelimit_reset)).strftime('%X')

                # We're ratelimited, and we may be waiting for a long time. Cancel orders.
                self.logger.warning("Canceling all known orders in the meantime.")
                #self.cancel([o['orderID'] for o in self.open_orders()])
                self.cancel_every_order()
                self.logger.error("Your ratelimit will reset at %s. time.Sleeping for %d seconds." % (reset_str, to_sleep))
                time.sleep(to_sleep)

                # Retry the request.
                return retry()

            # 503 - BitMEX temporary downtime, likely due to a deploy. Try again
            elif response.status_code == 503:
                self.logger.warning("Unable to contact the BitMEX API (503), retrying. " +
                                    "Request: %s \n %s" % (url, json.dumps(postdict)))
                time.sleep(3)
                return retry()

            elif response.status_code == 400:
                error = response.json()['error']
                message = error['message'].lower() if error else ''

                # Duplicate clOrdID: that's fine, probably a deploy, go get the order(s) and return it
                if 'duplicate clordid' in message:
                    orders = postdict['orders'] if 'orders' in postdict else postdict

                    IDs = json.dumps({'clOrdID': [order['clOrdID'] for order in orders]})
                    orderResults = self._curl_bitmex('/order', query={'filter': IDs}, verb='GET')

                    for i, order in enumerate(orderResults):
                        if (
                                order['orderQty'] != abs(postdict['orderQty']) or
                                order['side'] != ('Buy' if postdict['orderQty'] > 0 else 'Sell') or
                                order['price'] != postdict['price'] or
                                order['symbol'] != postdict['symbol']):
                            logger.log_error('Attempted to recover from duplicate clOrdID, but order returned from API ' +
                                            'did not match POST.\nPOST data: %s\nReturned order: %s' % (
                                                json.dumps(orders[i]), json.dumps(order)))
                    # All good
                    return orderResults

                elif 'insufficient available balance' in message:
                    self.logger.error('Account out of funds. The message: %s' % error['message'])
                    exit_or_throw(logger.log_error('Insufficient Funds'))


            # If we haven't returned or re-raised yet, we get here.
            self.logger.error("Unhandled Error: %s: %s" % (e, response.text))
            self.logger.error("Endpoint was: %s %s: %s" % (verb, path, json.dumps(postdict)))
            exit_or_throw(e)

        except requests.exceptions.Timeout as e:
            # Timeout, re-run this request
            self.logger.warning("Timed out on request: %s (%s), retrying..." % (path, json.dumps(postdict or '')))
            return retry()

        except requests.exceptions.ConnectionError as e:
            self.logger.warning("Unable to contact the BitMEX API (%s). Please check the URL. Retrying. " +
                                "Request: %s %s \n %s" % (e, url, json.dumps(postdict)))
            time.sleep(1)
            return retry()

        # Reset retry counter on success
        self.retries = 0
        return response.json()