
"""
    This script will analyze the daily trends to see if there is any BUY/SELL signal
    for today (and yesterday).
"""
from datetime import datetime, timedelta
import yfinance as yf
import backtrader as bt

from MCerebro import MCerebro
from sma_cross import MySmaCrossStrategy, save_backtrader_plot

default_symbols = ['NVDA', 'AAPL', 'AMZN', 'FB', 'GOOGL', 'NFLX', 'TSLA', 'MSFT', 'JPM', 'V', 'MA',
           'JNJ', 'UNH', 'PG', 'HD', 'DIS', 'BAC', 'KO', 'PEP', 'VZ',
           'T', 'INTC', 'CSCO', 'WMT', 'MCD', 'COST', 'XOM', 'CVX', 'BA', 'MMM',
           'GE', 'CAT', 'IBM', 'GS', 'MS', 'AXP', 'WFC', 'JPM', 'AMGN', 'MRK',
           'PFE', 'NKE', 'WBA', 'UNP', 'UPS', 'FDX', 'LMT', 'RTX', 'TMO', 'ABBV']
# default_symbols = ['AMZN']

ndays = 50
today = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now().replace(day=1) - timedelta(days=ndays)).strftime('%Y-%m-%d')

if __name__ == '__main__':
    for symbol in default_symbols:
        # Check data from the database
        print(f"Analyzing {symbol} from {start_date} to {today}")

        symbol = symbol.upper()
        hist = yf.download(
            symbol,
            start=start_date,
            end=today
        )
        hist.columns = hist.columns.get_level_values(0)
        data = bt.feeds.PandasData(dataname=hist)
        if len(hist) < 35:
            print(f"Not enough data for {symbol}, skipping...")
            continue

        # Configuring and running cerebro
        cerebro = MCerebro()
        cerebro.addstrategy(MySmaCrossStrategy)
        data_feed = cerebro.adddata(data)

        results = cerebro.run()
        save_backtrader_plot(cerebro, filename=f"plots/backtest_plot_{symbol}_{today}.png", dpi=300, style="candlestick")

        strategy = results[0]
        signals = strategy.signals
        signals.sort(key=lambda x: x[1])

        # check if there is signals N last days
        N = 5
        cutoff_date_str = (datetime.now() - timedelta(days=N)).strftime('%Y-%m-%d')
        recent_signals = [s for s in signals if str(s[1]) >= cutoff_date_str]

        if recent_signals:
            print(f"Recent signals for {symbol}:")
            for signal in recent_signals:
                print(f"{signal[0]} on {signal[1]}")
            # send mail
            from mail_notification import send_email
            last_action = recent_signals[-1][0]
            send_email(
                to_email="ryanrasoarahona@gmail.com",
                subject=f"{symbol} is ready to {last_action}",
                message=f"{symbol} is ready to {last_action} on {recent_signals[-1][1]}. Please check the attached plot.",
                image_path=f"plots/backtest_plot_{symbol}_{today}.png"
            )


