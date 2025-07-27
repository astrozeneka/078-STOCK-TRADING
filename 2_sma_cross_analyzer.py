
import yfinance as yf
import backtrader as bt
import matplotlib.pyplot as plt

from MCerebro import MCerebro
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
        self.signals = []  # Store signals as (signal_type, date) tuples

        for d in self.datas:
            self.fast_sma[d] = bt.indicators.SMA(d.close, period=self.params.pfast)
            self.slow_sma[d] = bt.indicators.SMA(d.close, period=self.params.pslow)
            self.crossover[d] = bt.indicators.CrossOver(self.fast_sma[d], self.slow_sma[d])
            self.rsi[d] = bt.indicators.RSI(d.close, period=21)

    def next(self):
        for d in self.datas:
            current_date = d.datetime.date(0)
            if not self.getposition(data=d):
                if self.crossover[d][0] > 0 or self.rsi[d][0] > 50:
                    self.buy(data=d, size=60)
                    self.signals.append(('BUY', current_date))
                    print('BUY, Symbol:', d._name, 'Close:', d.close[0])
            elif self.crossover[d][0] < 0 and self.rsi[d][0] < 50:
                self.close(data=d)
                print('SELL, Symbol:', d._name, 'Close:', d.close[0])
                self.signals.append(('SELL', current_date))

def save_backtrader_plot(cerebro, filename='backtest_plot.png', dpi=300, **kwargs):
    """
    Custom function to save backtrader plots without blocking execution

    Args:
        cerebro: The cerebro instance after running
        filename: Output filename for the plot
        dpi: Resolution of the saved image
        **kwargs: Additional arguments passed to cerebro.plot()
    """
    if True:
        # Generate plots with non-interactive backend
        plots = cerebro.plot(width=32, height=9, dpi=dpi)

        if not plots:
            print("No plots were generated")
            return False

        # Handle multiple strategies if present
        saved_count = 0
        for i, strategy_plots in enumerate(plots):
            for j, fig in enumerate(strategy_plots):
                if len(plots) > 1 or len(strategy_plots) > 1:
                    # Multiple figures - add index to filename
                    base_name = filename.rsplit('.', 1)[0]
                    ext = filename.rsplit('.', 1)[1] if '.' in filename else 'png'
                    save_filename = f"{base_name}_strategy{i}_fig{j}.{ext}"
                else:
                    # Single figure - use original filename
                    save_filename = filename

                fig.savefig(save_filename, dpi=dpi, bbox_inches='tight')
                plt.close(fig)  # Free memory
                saved_count += 1
                print(f"Saved plot: {save_filename}")

        return saved_count > 0

if __name__ == '__main__':
    #tkr = yf.Ticker("NVDA")

    hist = get_ticker_data("NVDA", start_date="2025-01-01")
    data = bt.feeds.PandasData(dataname=hist, name="NVDA")

    cerebro = MCerebro()
    cerebro.addstrategy(MyStrategy)
    cerebro.adddata(data)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    save_backtrader_plot(cerebro, filename='backtrader_plot.png', dpi=300, style='candlestick')

    strategy = results[0]
    signals = strategy.signals
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print()
