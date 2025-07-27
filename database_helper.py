from datetime import datetime

import pandas as pd
import mysql.connector
import dotenv
import os
dotenv.load_dotenv()
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT", 3306))  # default to 3306 if not set
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None


def get_ticker_id(ticker_symbol):
    """
    Get ticker_id for a given ticker symbol.
    If it doesn't exist, insert it and return the new ID.
    """
    connection = connect_to_db()
    if not connection:
        return None

    try:
        cursor = connection.cursor()

        # Try to get existing ticker
        cursor.execute("SELECT ticker_id FROM ticker WHERE ticker_symbol = %s", (ticker_symbol,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Insert new ticker if not found
        cursor.execute(
            "INSERT INTO ticker (ticker_symbol, company_name) VALUES (%s, %s)",
            (ticker_symbol, ticker_symbol)
        )
        connection.commit()

        return cursor.lastrowid

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        connection.close()


def insert_daily_prices(ticker_id, trade_date, open_price, high_price, low_price, close_price, volume):
    """
    Insert daily price data for a ticker.
    Updates if the record already exists for the same ticker and date.
    """
    connection = connect_to_db()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO daily_prices (ticker_id, trade_date, open_price, high_price, low_price, close_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open_price = VALUES(open_price),
                high_price = VALUES(high_price),
                low_price = VALUES(low_price),
                close_price = VALUES(close_price),
                volume = VALUES(volume)
        """, (ticker_id, trade_date, open_price, high_price, low_price, close_price, volume))

        connection.commit()
        return True

    except Exception as e:
        print(f"Error inserting daily prices: {e}")
        return False
    finally:
        connection.close()


def get_ticker_data(ticker_symbol, start_date, end_date=datetime.now().strftime('%Y-%m-%d')):
    """
    Retrieve daily price data for a ticker between specified dates.
    Returns a pandas DataFrame compatible with bt.feeds.PandasData.
    """
    connection = connect_to_db()
    if not connection:
        return None

    try:
        cursor = connection.cursor()

        # Get ticker_id
        cursor.execute("SELECT ticker_id FROM ticker WHERE ticker_symbol = %s", (ticker_symbol,))
        result = cursor.fetchone()

        if not result:
            print(f"Ticker {ticker_symbol} not found in database")
            return None

        ticker_id = result[0]

        # Get price data
        cursor.execute("""
            SELECT trade_date, open_price, high_price, low_price, close_price, volume
            FROM daily_prices 
            WHERE ticker_id = %s AND trade_date BETWEEN %s AND %s
            ORDER BY trade_date
        """, (ticker_id, start_date, end_date))

        rows = cursor.fetchall()

        if not rows:
            print(f"No data found for {ticker_symbol} between {start_date} and {end_date}")
            return None

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        return df

    except Exception as e:
        print(f"Error retrieving ticker data: {e}")
        return None
    finally:
        connection.close()