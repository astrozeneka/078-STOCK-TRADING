from datetime import datetime

import yfinance as yf
import pandas as pd
import argparse

from database_helper import connect_to_db, get_ticker_id, insert_daily_prices

parser = argparse.ArgumentParser(description="Download and store asset data from Yahoo Finance")
parser.add_argument(
    '--symbol',
    type=str,
    help='The stock symbol to download data for (e.g., AAPL, TSLA)'
)
parser.add_argument(
    '--start',
    type=str,
    default='2000-01-01',
    help='Start date for downloading data (default: 2000-01-01)'
)
parser.add_argument(
    '--end',
    type=str,
    default=datetime.now().strftime('%Y-%m-%d'),
    help='End date for downloading data (default: 2022-12-31)'
)
args = parser.parse_args()





if __name__ == '__main__':
    conn = connect_to_db()

    ticker_id = get_ticker_id(args.symbol)

    symbol = args.symbol.upper()
    data = yf.download(
        symbol,
        start=args.start,
        end=args.end
    )

    data.columns = data.columns.get_level_values(0)

    records_inserted = 0
    for date, row in data.iterrows():
        success = insert_daily_prices(
            ticker_id=ticker_id,
            trade_date=date.strftime('%Y-%m-%d'),
            open_price=float(row['Open']),
            high_price=float(row['High']),
            low_price=float(row['Low']),
            close_price=float(row['Close']),
            volume=int(row['Volume'])
        )

        if success:
            records_inserted += 1

    print(f"Successfully processed {records_inserted} records for {symbol}")
    print()