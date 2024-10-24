import threading
import alpaca_trade_api as tradeapi
import pandas as pd
import time
import tkinter as tk
from tkinter import PhotoImage
from tkinter import messagebox

# Alpaca API credentials
API_KEY = 'PKYW2KU4ERSLVK37S28O'
API_SECRET = 'hQSNiGEWEnCIiBdzS8LUqM6qwYSuFN2xSMq6Opvo'
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Define stock symbols, timeframe, and other parameters
symbols = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']  
timeframe = tradeapi.rest.TimeFrame.Minute  
limit = 100  
position_size = 1  
trading = False

# GUI setup
window = tk.Tk()
window.title("Range Trading Bot")

# Add logo at the top
logo_img = PhotoImage(file='CodeCraftLogo.png')
logo_label = tk.Label(window, image=logo_img)
logo_label.pack(pady=10)

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

# Function to generate buy/sell signals based on Bollinger Bands and print current bands
def bollinger_signal(data, symbol):
    latest = data.iloc[-1]
    upper_band = latest['Upper']
    lower_band = latest['Lower']
    current_price = latest['close']
    
    # Print the current Bollinger Bands and price
    print(f"Symbol: {symbol} | Upper Band: {upper_band:.3f}, Lower Band: {lower_band:.3f}, Current Price: {current_price:.3f}")
    
    # Determine buy, sell, or hold signal
    if current_price < lower_band:  # Buy signal (price crosses below lower band)
        return 'buy'
    elif current_price > upper_band:  # Sell signal (price crosses above upper band)
        return 'sell'
    else:
        return 'hold'

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
        return False 

# Function to show popup notifications
'''def show_popup(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Trading Bot Notification", message)
    root.destroy()'''

# Main trading function to be run in a separate thread
def start_trading():
    global trading
    trading = True
    print("Trading started.")
    
    while trading:
        try:
            for sym in symbols:
                data = get_bollinger_bands(sym, limit=limit)
                signal = bollinger_signal(data, sym)
                print(f"Symbol: {sym}, Signal: {signal}")
                
                # Check if there's an open position
                has_position = has_open_position(sym)
                
                # Execute trade based on signal
                if signal == 'buy' and not has_position:
                    execute_trade('buy', sym, position_size)
                elif signal == 'sell' and has_position:
                    execute_trade('sell', sym, position_size)
            
            time.sleep(60)  # Sleep for a minute before checking again
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait before retrying

# Function to start trading in a new thread
def start_trading_thread():
    trading_thread = threading.Thread(target=start_trading)
    trading_thread.daemon = True  # exits when the main program exits
    trading_thread.start()

# Function to stop trading
def stop_trading():
    global trading
    trading = False
    print("Trading stopped.")

# Start button
start_button = tk.Button(window, text="Start Trading", command=start_trading_thread, width=20, height=2)
start_button.pack(pady=10)

# Stop button
stop_button = tk.Button(window, text="Stop Trading", command=stop_trading, width=20, height=2)
stop_button.pack(pady=10)

# Start the GUI loop
window.mainloop()
