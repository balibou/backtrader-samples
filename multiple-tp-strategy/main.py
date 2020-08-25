from pytz import timezone
from datetime import datetime, timedelta
import backtrader as bt
from config import CustomDataset, FullMoney
from stopLossWithBracketOrders import MultipleTPWithSL

startDate = datetime(2018, 8, 15, 0, 0, 0, 0, timezone('UTC'))
endDate = datetime(2019, 10, 15, 0, 0, 0, 0, timezone('UTC'))
data = CustomDataset(
    dataname="dataset/BTCUSDT-1m.csv",
    timeframe=bt.TimeFrame.Minutes,
    fromdate=startDate,
    todate=endDate,
)

cerebro = bt.Cerebro()
cerebro.addstrategy(MultipleTPWithSL)
cerebro.addsizer(FullMoney)

# ---- Resample minutes to 4 hours timeframe ----
timeframe = 240

def _new_load(self):
    ret = self._old_load()
    if ret:
        datetime = self.datetime.datetime(0)
        self.datetime[0] = bt.date2num(datetime - timedelta(minutes=timeframe-1))

    return ret

rd = cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=timeframe)
rd._old_load, rd._load = rd._load, _new_load.__get__(rd, rd.__class__)
# -----------------------------------------------

broker = cerebro.getbroker()
broker.setcommission(commission=0.001)
broker.setcash(100000.0)

cerebro.broker.getvalue()
cerebro.run()
cerebro.broker.getvalue()

cerebro.plot(style='candlestick', barup='green', bardown='red')
