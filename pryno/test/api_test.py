from pyno.util.api_bitmex import BitMEX
import pyno.util.secret as keys
from pyno.util.logger import setup_logger
from time import sleep
import sys
# from pyno.strategies import MarketMaker


def run():
    logger = setup_logger()
    bitmex = BitMEX(base_url="https://www.bitmex.com/api/v1/", symbol="XBTUSD",
                         apiKey=keys.bitmex_key, apiSecret=keys.bitmex_secret)


    numberOrders = 1
    while(bitmex.ws.ws.sock.connected):
        #logger.info("Long 300 @ 8800: %s" % bitmex.buy(300, 8800))
        #logger.info("Short 300 @ 9600: %s" % bitmex.sell(300, 9600))
        #logger.info("Position: %s" % bitmex.position('XBTUSD'))
        #logger.info("Funds: %s" % bitmex.funds())
        #logger.info("Delta: %s" % bitmex.delta())
        #logger.info("Open orders: %s" % bitmex.open_orders())
        #logger.info("Open http orders: %s" % bitmex.http_open_orders())
        #logger.info("Isolate Margin: %s" % bitmex.isolate_margin('XBTUSD', 1.2, True))

        logger.info("Full status: %s" % bitmex.get_full_status())
        #first_order = bitmex.ws.get_order_id('pyno_v0')[0]
        #logger.info("Cancelling: %s" % bitmex.cancel(first_order))

        '''        
        orders = []
        order1 = bitmex.format_order(300, 8800)
        orders.append(order1)
        order2 = bitmex.format_order(300, 9600)
        orders.append(order2)
        logger.info("Bulk order: %s" % bitmex.create_bulk_orders(orders))
        '''

        # Amend not working
        '''
        orders[0] = bitmex.format_order(290, 8800)
        orders[1] = bitmex.format_order(290, 8800)
        logger.info("Amending orders: %s" % bitmex.amend_bulk_orders(orders))
        '''

        # try:
            
        #     if numberOrders < 10:
        #         orders = []
        #         order1 = bitmex.format_order(300, 8800,numberOrders)
        #         orders.append(order1)
        #         order2 = bitmex.format_order(-300, 9600,numberOrders)
        #         orders.append(order2)
        #         logger.info("Bulk order: %s" % bitmex.create_bulk_orders(orders))
        #         #logger.info("Bulk order: %s" % bitmex.place_order(300, 8800))
        #         #logger.info("Bulk order: %s" % bitmex._curl_bitmex(path='order/bulk', postdict={'orders': orders}, verb='POST') )

        #     numberOrders = numberOrders + 1
        # except (KeyboardInterrupt, SystemExit):
        #     logger.info("Wrong place pal")
        #     sys.exit()
        

        sleep(5)
        

if __name__ == "__main__":
    run()