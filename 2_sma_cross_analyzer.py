
import yfinance as yf
import backtrader as bt

from database_helper import get_ticker_data


class MyStrategy(bt.Strategy):
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30  # period for the slow moving average
    )

    def __init__(self):
        self.fast_sma = {}
        self.slow_sma = {}
        self.crossover = {}
        self.rsi = {}

        for d in self.datas:
            self.fast_sma[d] = bt.indicators.SMA(d.close, period=self.params.pfast)
            self.slow_sma[d] = bt.indicators.SMA(d.close, period=self.params.pslow)
            self.crossover[d] = bt.indicators.CrossOver(self.fast_sma[d], self.slow_sma[d])
            self.rsi[d] = bt.indicators.RSI(d.close, period=21)

    def next(self):
        for d in self.datas:
            if not self.getposition(data=d):
                if self.crossover[d][0] > 0 or self.rsi[d][0] > 50:
                    self.buy(data=d, size=60)
                    print('BUY, Symbol:', d._name, 'Close:', d.close[0])
            elif self.crossover[d][0] < 0 and self.rsi[d][0] < 50:
                self.close(data=d)
                print('SELL, Symbol:', d._name, 'Close:', d.close[0])



if __name__ == '__main__':
    #tkr = yf.Ticker("NVDA")

    hist = get_ticker_data("NVDA", start_date="2020-01-01", end_date="2025-05-06")
    data = bt.feeds.PandasData(dataname=hist, name="NVDA")

    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    cerebro.plot()
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print()