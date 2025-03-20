import yfinance as yf
from datetime import datetime
import pandas as pd
import time
from yfinance import exceptions as e

def candlestick_data(ticker, max_retries=3, initial_delay=1):
    """
    Fetch candlestick data for a given ticker with rate limit handling
    
    Args:
        ticker (str): Stock ticker symbol
        max_retries (int): Maximum number of retry attempts
        initial_delay (int): Initial delay between retries in seconds
        
    Returns:
        list: List of dictionaries containing candlestick data
              Returns empty list if all retries fail
    """
    retries = 0
    delay = initial_delay
    
    while retries < max_retries:
        try:
            # Initialize yfinance Ticker object
            stock = yf.Ticker(ticker)
            now = datetime.now().date().strftime('%Y-%m-%d')
            
            # Fetch historical data
            history = stock.history(start="2001-05-21", end=now)
            history = history.reset_index()
            
            # Convert relevant columns to float64
            for col in ['Open', 'High', 'Close', 'Low']:
                history[col] = history[col].astype('float64')
                
            # Prepare data for return
            cols = history.columns[:5].values
            data = []
            
            for _, row in history.iterrows():
                candle = {col: row[col] for col in cols}
                candle['Date'] = row['Date'].date().strftime("%d-%b-%Y")
                data.append(candle)
                
            return data
            
        except e.YFRateLimitError:
            retries += 1
            if retries < max_retries:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                # Return empty data after max retries
                return []
                
        except Exception as e:
            # Handle other potential errors
            print(f"Error fetching data for {ticker}: {e}")
            return []
    #print(old)
    # return data
    # final_data = {}
    # if(len(passover['Open']) > 0):
    #
    #     open_last = list(passover['Open'].keys())[-1]
    #     high_last = list(passover['High'].keys())[-1]
    #
    #     low_last = list(passover['Low'].keys())[-1]
    #
    #     close_last = list(passover['Close'].keys())[-1]
    #
    #     final_data = {
    #         "Open":passover['Open'][open_last],
    #         "High":passover['High'][high_last],
    #         "Low":passover['Low'][low_last],
    #         "Close":passover['Close'][close_last],
    #
    #     }
    #
    #
    #
    # return passover['Open'].keys()

#print(get_data("aapl"))

def get_data(ticker):
    #now  = datetime.now()
    aapl = yf.Ticker(ticker)
    data = aapl.info
    return data

def get_name(ticker):
    symbol = yf.Ticker(ticker)
    data = symbol.info
    print(data)
    return(data['shortName'])

def get_price(ticker):
    symbol = yf.Ticker(ticker)
    # df  =symbol.history(interval='5m')
    data = symbol.info
    price  =  symbol.history(interval='5m').iloc[-1].Close
    # print(df)
    return([price, data['currency']])



# for a in get_data("aapl"):
#     print(a.shortName)
