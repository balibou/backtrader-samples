import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = dict(fast_ma=10, slow_ma=20,)

    def __init__(self):
      self.orefs = list()
      fast_ma = bt.ind.EMA(period=self.p.fast_ma)
      slow_ma = bt.ind.EMA(period=self.p.slow_ma)
      self.crossup = bt.ind.CrossUp(fast_ma, slow_ma)

class MultipleTPWithSL(BaseStrategy):
  def notify_order(self, order):
      print('{}: Order ref: {} / Type {} / Status {}'.format(
        self.data.datetime.date(0),
        order.ref, 'Buy' * order.isbuy() or 'Sell',
        order.getstatusname()
      ))

      if order.status == order.Completed:
        self.holdstart = len(self)

      if not order.alive() and order.ref in self.orefs:
        self.orefs.remove(order.ref)


  def next(self):
    self.date = self.data.datetime.date()
    print("{} {:.2f}".format(self.date, self.data[0]))

    if self.orefs:
      return  # pending orders do nothing
    
    print("Size is: {}".format(self.position.size))

    if not self.position and self.crossup > 0:
      # not in the market and signal triggered
      close = self.data.close[0]
      p1 = close
      p2 = p1 - 0.03 * close
      p3 = p1 + 0.03 * close
      p4 = p1 + 0.06 * close
      p5 = p1 + 0.12 * close
      p6 = p1 + 0.24 * close

      o1 = self.buy(
        exectype=bt.Order.Limit,
        price=p1,
        transmit=False
      )

      print('{}: Oref {} / Buy at {}'.format(
          self.datetime.date(), o1.ref, p1))

      o2 = self.sell(
        exectype=bt.Order.Stop,
        price=p2,
        parent=o1,
        transmit=False
      )

      print('{}: Oref {} / Sell Stop at {}'.format(self.datetime.date(), o2.ref, p2))

      o3 = self.sell(
        exectype=bt.Order.Limit,
        price=p3,
        parent=o1,
        transmit=True
      )

      print('{}: Oref {} / Sell Limit at {}'.format(self.datetime.date(), o3.ref, p3))

      print('------------------------------------------------------------------------')
      o4 = self.buy(
        exectype=bt.Order.Limit,
        price=p1,
        transmit=False
      )

      print('{}: Oref {} / Buy at {}'.format(
          self.datetime.date(), o4.ref, p1))

      o5 = self.sell(
        exectype=bt.Order.Stop,
        price=p2,
        parent=o4,
        transmit=False
      )

      print('{}: Oref {} / Sell Stop at {}'.format(self.datetime.date(), o5.ref, p2))

      o6 = self.sell(
        exectype=bt.Order.Limit,
        price=p4,
        parent=o4,
        transmit=True
      )

      print('{}: Oref {} / Sell Limit at {}'.format(self.datetime.date(), o6.ref, p4))

      print('------------------------------------------------------------------------')
      o7 = self.buy(
        exectype=bt.Order.Limit,
        price=p1,
        transmit=False
      )

      print('{}: Oref {} / Buy at {}'.format(self.datetime.date(), o7.ref, p1))

      o8 = self.sell(
        exectype=bt.Order.Stop,
        price=p2,
        parent=o7,
        transmit=False
      )

      print('{}: Oref {} / Sell Stop at {}'.format(self.datetime.date(), o8.ref, p2))

      o9 = self.sell(
        exectype=bt.Order.Limit,
        price=p5,
        parent=o7,
        transmit=True
      )

      print('{}: Oref {} / Sell Limit at {}'.format(self.datetime.date(), o9.ref, p5))

      self.orefs = [
        o1.ref, o2.ref, o3.ref,
        o4.ref, o5.ref, o6.ref,
        o7.ref, o8.ref, o9.ref,
      ]

