import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np
import time

AAPLTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AAPL/trades/latest?feed=iex'
TSLATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/TSLA/trades/latest?feed=iex'
AMZNTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AMZN/trades/latest?feed=iex'
MSFTTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/MSFT/trades/latest?feed=iex'
METATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/META/trades/latest?feed=iex'
GOOGTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/GOOG/trades/latest?feed=iex'

# Alpaca API credentials (replace with your keys)
API_KEY = 'PKANC9WRD0CHUHCWE7SG'
API_SECRET = 'TOUV6DNtDkFoRBtkCti9YmCxDSAhNsnasA0IgxsY'
BASE_URL = 'https://paper-api.alpaca.markets/v2'  # Paper trading URL

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Define stock symbols, timeframe, and other parameters
symbol = ['AAPL', 'MSFT', 'GOOGL', '']  # List of symbols to trade
timeframe = tradeapi.rest.TimeFrame.Minute  # 1-minute intervals
limit = 100  # Number of historical bars to retrieve
position_size = 1  # Number of shares to trade

# Function to fetch historical data and calculate Bollinger Bands
def get_bollinger_bands(symbol, limit=100):
    # Fetch the latest bar data from Alpaca
    bars = api.get_bars(symbol, timeframe, limit=limit).df
    
    # Calculate 20-period moving average
    bars['MA20'] = bars['close'].rolling(window=20).mean()
    
    # Calculate the rolling standard deviation
    bars['STD'] = bars['close'].rolling(window=20).std()
    
    # Calculate Bollinger Bands
    bars['Upper'] = bars['MA20'] + (bars['STD'] * 2)
    bars['Lower'] = bars['MA20'] - (bars['STD'] * 2)
    
    return bars

# Function to generate buy/sell signals based on Bollinger Bands
def bollinger_signal(data):
    latest = data.iloc[-1]  # Get the latest row of data
    if latest['close'] < latest['Lower']:  # Buy signal (price crosses below lower band)
        return 'buy'
    elif latest['close'] > latest['Upper']:  # Sell signal (price crosses above upper band)
        return 'sell'
    else:
        return 'hold. The prices havent reached the lower limit yet'

# Function to place buy/sell orders
def execute_trade(signal, symbol, qty):
    if signal == 'buy':
        try:
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"Bought {qty} shares of {symbol}")
        except Exception as e:
            print(f"Error placing buy order: {e}")
    
    elif signal == 'sell':
        try:
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            print(f"Sold {qty} shares of {symbol}")
        except Exception as e:
            print(f"Error placing sell order: {e}")

# Function to check for an open position
def has_open_position(symbol):
    try:
        position = api.get_position(symbol)
        return int(position.qty) > 0
    except tradeapi.rest.APIError as e:
        return False  # No open position

# Main loop to continuously check for signals and trade
while True:
    try:
        # Fetch the latest data and calculate Bollinger Bands
        data = get_bollinger_bands(symbol, limit=limit)
        
        # Generate trading signal
        signal = bollinger_signal(data)
        print(f"Current signal: {signal}")
        
        # Check if there's an open position
        has_position = has_open_position(symbol)
        
        # Execute trade based on signal
        if signal == 'buy' and not has_position:
            execute_trade('buy', symbol, position_size)
        elif signal == 'sell' and has_position:
            execute_trade('sell', symbol, position_size)
        
        # Sleep for a minute before checking again
        time.sleep(60)
    
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)  # Wait before retrying
