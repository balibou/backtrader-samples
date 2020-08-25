import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = dict(fast_ma=10, slow_ma=20,)

    def __init__(self):
        self.stopLossList = []
        self.TakeProfitList = []
        self.shouldUpdateSLSize = False
        self.SLSizeToUpdate = 0

        fast_ma = bt.ind.EMA(period=self.p.fast_ma)
        slow_ma = bt.ind.EMA(period=self.p.slow_ma)
        self.crossup = bt.ind.CrossUp(fast_ma, slow_ma)

class MultipleTPWithSL(BaseStrategy):
    params = dict(
        stop_loss_percentage=3,
    )

    def notify_order(self, order):
        if not order.status == order.Completed: # Be sure that the broker set the order
            return  # discard any other notification

        otypetxt = 'Buy' if order.isbuy() else 'Sell'

        if order.status == order.Completed:
            print(
                ('{} - {} Order Completed - '
                 'Size: {} @Price: {} '
                 'Value: {:.2f} Comm: {:.2f}').format(
                self.date, otypetxt, order.executed.size, order.executed.price,
                order.executed.value, order.executed.comm)
            )

        if (otypetxt == 'Sell'):
            # For each triggered TP, we update SL size
            if (order.ref == self.TakeProfitList[0].ref):
                print('Update size of the SL (TP 1)')
                self.shouldUpdateSLSize = True
                self.SLSizeToUpdate += order.executed.size
            elif (order.ref == self.TakeProfitList[1].ref):
                print('Update size of the SL (TP 2)')
                self.shouldUpdateSLSize = True
                self.SLSizeToUpdate += order.executed.size
            elif (order.ref == self.TakeProfitList[2].ref):
                print('Update size of the SL (TP 3)')
                self.shouldUpdateSLSize = True
                self.SLSizeToUpdate += order.executed.size
            elif (order.ref == self.TakeProfitList[3].ref):
                self.stopLossList[0].cancel()
                self.stopLossList = []
                self.shouldUpdateSLSize = False
            elif (order.ref == self.stopLossList[0].ref): # if SL is triggered, we cancel all TP orders
                self.TakeProfitList[0].cancel()
                self.TakeProfitList[1].cancel()
                self.TakeProfitList[2].cancel()
                self.TakeProfitList[3].cancel()
                self.TakeProfitList = []
                self.shouldUpdateSLSize = False
            return
        elif(otypetxt == 'Buy'):
            # We have entered the market
            self.buyPrice = order.executed.price

            # ---- Create Stop Loss list ----
            stop_price = order.executed.price * (1 - (self.p.stop_loss_percentage) / 100)
            print("STOP LOSS @price: {}".format(stop_price))
            self.stopLossList = [
                self.sell(exectype=bt.Order.Stop, price=stop_price)
            ]
            # ---------------------------------

            # ---- Create Take Profit list ----
            firstTPSize = order.size * 0.25
            secondTPSize = order.size * 0.25
            thirdTPSize = order.size * 0.25
            fourthTPSize = order.size - firstTPSize - secondTPSize - thirdTPSize

            print('TP1 size: {}, TP2 size: {}, TP3 size: {}, TP4 size: {}'.format(
                firstTPSize, secondTPSize, thirdTPSize, fourthTPSize
            ))

            self.TakeProfitList = [
                self.sell(exectype=bt.Order.Limit, price=self.data.close * 1.03, size= firstTPSize),
                self.sell(exectype=bt.Order.Limit, price=self.data.close * 1.06, size= secondTPSize),
                self.sell(exectype=bt.Order.Limit, price=self.data.close * 1.12, size= thirdTPSize),
                self.sell(exectype=bt.Order.Limit, price=self.data.close * 1.20, size= fourthTPSize)
            ]
            # ---------------------------------

    def next(self):
        self.date = self.data.datetime.date()
        print("{} {:.2f}".format(self.date, self.data[0]))
        if len(self.stopLossList): print(self.stopLossList[0].alive())

        if len(self.stopLossList) > 0 and self.shouldUpdateSLSize:
            print('SL size: {}, Next SL Size position: {}'.format(self.stopLossList[0].created.size, self.position.size))
            print("{} Stop size changed to: {:.20f}".format(self.date, self.position.size))

            # delete previous SL and create new SL with updated size
            self.stopLossList[0].cancel()
            new_stop_price = self.buyPrice * (1 - 3 / 100)
            self.stopLossList = [
                self.sell(exectype=bt.Order.Stop, price=new_stop_price, size=self.position.size)
            ]

            self.shouldUpdateSLSize = False
            self.SLSizeToUpdate = 0

        else:
            pass

        if not self.position and self.crossup > 0:
            # not in the market and signal triggered
            o1 = self.buy()
