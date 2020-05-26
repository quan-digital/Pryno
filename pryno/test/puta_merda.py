from pyno.util.api_bitmex import BitMEX
import pyno.util.secret as secret
import pyno.util.settings as settings

bitmex_key = secret.bitmex_key
bitmex_secret = secret.bitmex_secret
print("Pyno is cancelling all orders")
exchange = BitMEX(base_url=settings.BASE_URL, symbol="XBTUSD", apiKey=bitmex_key, apiSecret=bitmex_secret)
exchange.cancel_every_order()
print('Open orders: %s' % str(exchange.http_open_orders()))
print('Position: %s' % str(exchange.http_get_position()[0]['currentQty']))
print('Balance: %s' % str(exchange.ws.get_balance()))