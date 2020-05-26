from pyno.util.api_bitmex import BitMEX
import pyno.util.secret as secret
import pyno.util.settings as settings

bitmex_key = secret.bitmex_key
bitmex_secret = secret.bitmex_secret
print("Pyno is fetching user wallet history")
startDate = 0
exchange = BitMEX(base_url=settings.BASE_URL, symbol="XBTUSD", apiKey=bitmex_key, apiSecret=bitmex_secret)
print('Open orders: %s' % str(exchange.http_open_orders()))
# response = exchange.get_fundsHistory(startDate)
# print('Olha ai: \n')
# # print(response)
# response = exchange.get_margin()
# print('margin:')
# print(response['availableMargin'])
# tick = exchange.instruments()[2]['tickSize']
# print('tickSize:')
# print(tick)
# tick = exchange.get_instrument()[0]['tickSize']
# print('tickSize:')
# print(tick)
# execution = exchange.get_execution()
# print('execution')
# print(execution[0]['cumQty'])
operationsParameter = exchange.get_operationParameters("XBTUSD",settings.CANDLE_TIME_INTERVAL,"1m")