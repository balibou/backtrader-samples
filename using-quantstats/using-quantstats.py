from datetime import datetime
import backtrader as bt
import quantstats as qs
import pandas as pd
import csv

class CashMarket(bt.analyzers.Analyzer):
  def start(self):
    super(CashMarket, self).start()

  def create_analysis(self):
    self.rets = {}
    self.vals = 0.0

  def notify_cashvalue(self, cash, value):
    self.vals = (cash, value)
    self.rets[self.strategy.datetime.datetime().strftime("%Y-%m-%d")] = self.vals

  def get_analysis(self):
    return self.rets

class SmaCross(bt.Strategy):
  params = dict(
    pfast=10,
    pslow=30
  )

  def __init__(self):
    sma1 = bt.ind.SMA(period=self.p.pfast)
    sma2 = bt.ind.SMA(period=self.p.pslow)
    self.crossover = bt.ind.CrossOver(sma1, sma2)

  def next(self):
    if not self.position:  # not in the market
      if self.crossover > 0:
        self.buy()

    elif self.crossover < 0:  # in the market & cross to the downside
      self.close()


cerebro = bt.Cerebro()

data = bt.feeds.Quandl(
  dataname='MSFT',
  fromdate = datetime(2017,1,1),
  todate = datetime(2017,12,28),
  buffered= True
)

cerebro.adddata(data)
cerebro.addstrategy(SmaCross)
cerebro.addanalyzer(CashMarket, _name='cashmarket')
results = cerebro.run()

# ---- Format the values from results ----
df_values = pd.DataFrame(results[0].analyzers.getbyname("cashmarket").get_analysis()).T
df_values = df_values.iloc[:, 1]
returns = qs.utils.to_returns(df_values)
returns.index = pd.to_datetime(returns.index)
# ----------------------------------------

# ---- Format the benchmark from SPY.csv ----
with open('SPY.csv', mode='r') as infile:
  reader = csv.reader(infile)
  mydict = {
    datetime.strptime(rows[0], "%Y-%m-%d"): float(rows[4]) for rows in reader
  }

benchmark = (
  pd.DataFrame.from_dict(mydict, orient="index")
)
returns_bm = qs.utils.to_returns(benchmark)
returns_bm.index = pd.to_datetime(returns_bm.index)
# -------------------------------------------

qs.extend_pandas()
qs.reports.full(returns, "SPY")
# qs.reports.html(df_values, "SPY", output="qs.html")