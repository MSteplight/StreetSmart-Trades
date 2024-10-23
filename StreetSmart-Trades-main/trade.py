''' THIS WILL BE USED WITH EACH STOCK'S OWN BUY AND SELL METHODS'''

import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np


import requests, json
from config import * # config file
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import time

# import alpaca_trade_api as tradeapi

'''
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
'''


BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = '{}/v2/account'.format(BASE_URL)
ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
ALL_ORDERS = '{}?status=all'.format(ORDERS_URL)
CLOSED_ORDERS = '{}?status=closed'.format(ORDERS_URL)
NEW_ORDERS = '{}?status=filled'.format(ORDERS_URL)

POSITIONS_URL = '{}/v2/positions'.format(BASE_URL)

CLOSEPOSAAPL_URL = '{}/v2/positions/AAPL'.format(BASE_URL)
CLOSEPOSTSLA_URL = '{}/v2/positions/TSLA'.format(BASE_URL)
CLOSEPOSAMZN_URL = '{}/v2/positions/AMZN'.format(BASE_URL)
CLOSEPOSMSFT_URL = '{}/v2/positions/MSFT'.format(BASE_URL)
CLOSEPOSMETA_URL = '{}/v2/positions/META'.format(BASE_URL)
CLOSEPOSGOOG_URL = '{}/v2/positions/GOOG'.format(BASE_URL)

AAPLTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AAPL/trades/latest?feed=iex'
TSLATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/TSLA/trades/latest?feed=iex'
AMZNTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/AMZN/trades/latest?feed=iex'
MSFTTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/MSFT/trades/latest?feed=iex'
METATRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/META/trades/latest?feed=iex'
GOOGTRADE_PRICE = 'https://data.alpaca.markets/v2/stocks/GOOG/trades/latest?feed=iex'
HEADERS = {'APCA-API-KEY-ID': API_KEY,'APCA-API-SECRET-KEY': SECRET_KEY}

TK_SILENCE_DEPRECATION=1

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def get_account():
     r = requests.get(ACCOUNT_URL,headers=HEADERS)
     return json.loads(r.content)

def get_cash():

     r = requests.get(ACCOUNT_URL, headers=HEADERS)
     response = json.loads(r.content)
     cash = response['cash']
     #print(f'Your cash amount is: ${cash}')
     return cash


def get_alpaca_data(ticker, timeframe='1D', start_date=None, end_date=None, limit=100): # New method to access real time data
    barset = api.get_bars(ticker, timeframe, start=start_date, end=end_date, limit=limit).df
    return barset


def bollinger_bands(df, window=20, no_of_std=2):
    df['SMA'] = df['close'].rolling(window=window).mean() # finding the Simple Moving Average
    df['STD'] = df['close'].rolling(window=window).std() # Calculating Standard deviation
    df['Upper Band'] = df['SMA'] + (no_of_std * df['STD'])  # Applying SD to upper band to get sell value
    df['Lower Band'] = df['SMA'] - (no_of_std * df['STD'])  # Applyinng SD to lower band to get buy value
    return df


def bollinger_strategy(df): # Our Trend Trading Strategy 
    buy_signal = []
    sell_signal = []

    for i in range(len(df)):
        '''
        if df['close'].iloc[i] < df['Lower Band'].iloc[i]:  # Buy condition
            buy_signal.append(df['close'].iloc[i])
            sell_signal.append(np.nan)
        elif df['close'].iloc[i] > df['Upper Band'].iloc[i]:  # Sell condition
            sell_signal.append(df['close'].iloc[i])
            buy_signal.append(np.nan)
        '''
        if df['close'][i] < df['Lower Band'][i]:  # Buy condition
            buy_signal.append(df['close'][i])
            sell_signal.append(np.nan)
        elif df['close'][i] > df['Upper Band'][i]:  # Sell condition
            sell_signal.append(df['close'][i])
            buy_signal.append(np.nan)
        else:
            buy_signal.append(np.nan)
            sell_signal.append(np.nan)

    df['Buy Signal'] = buy_signal
    df['Sell Signal'] = sell_signal
    return df


# Example usage
ticker = 'AAPL'
start_date = '2022-01-01'
end_date = '2023-01-01'
timeframe = '1Day'  # You can adjust the timeframe

# Fetch data from Alpaca
df = get_alpaca_data(ticker, timeframe=timeframe, start_date=start_date, end_date=end_date)

# Calculate Bollinger Bands
df = bollinger_bands(df)

# Apply the strategy
df = bollinger_strategy(df)


def get_tradePrice(stock):
     r = requests.get(stock, headers=HEADERS)
     response = json.loads(r.content)
     price = response['trade']['p']

     return price


# Function to create an order
def create_order(symbol, qty, side, type, time_in_force):
    data = {
        'symbol': symbol,
        'qty': qty,
        'side': side,
        'type': type,
        'time_in_force': time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    response = json.loads(r.content)
    print(response)


def get_orders():
     r = requests.get(ALL_ORDERS, headers=HEADERS)
     return json.loads(r.content)

# Function to check if the current time is within trading hours
def is_trading_hours():
    current_time = time.localtime()
    if current_time.tm_hour >= 9 and current_time.tm_hour < 16:
        return True
    else:
        return False

# Function to activate the bot at market opening
def activate_bot():
    if is_trading_hours():
         # Make purchases of specified stocks
        # buy_stocks()
         monitor_stock_pl()
         #schedule_sell_before_market_close()
    else:
         print("Market is closed. Cannot activate bot.")

# Function to deactivate the bot at market closing
def deactivate_bot():
    if is_trading_hours():
        # Sell all stocks before market closes
        sell_all_stocks()
    else:
        print("Market is closed. Bot is already deactivated.")



'''
# Function to buy specified stocks
def buy_stocks():
    stocks_to_buy = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    for stock in stocks_to_buy:
        #last_trade = api.get_last_trade(stock)
        create_order(symbol=stock, qty=1, side='buy', type='market', time_in_force='day') 

def sell_stocks_if_price_change():
    orders = get_orders()
    current_time = time.localtime()
    for order in orders:
        symbol = order['symbol']
        # Retrieve current price of the stock
        current_price = get_current_price(symbol)
        # Calculate percentage change
        purchase_price = get_purchase_price(symbol)
        percentage_change = ((current_price - purchase_price) / purchase_price) * 100
        if abs(percentage_change) >= 0.5:  # If price change is >= 0.5% in either direction
            create_order(symbol=symbol, qty=order['qty'], side='sell', type='market', time_in_force='day')
        elif current_time.tm_hour == 10 and current_time.tm_min == 1:
            create_order(symbol=symbol, qty=order['qty'], side='sell', type='market', time_in_force='day')
        deactivate_bot()
'''

# Function to get the current price of a stock
def get_current_price(symbol):
    BASE_URL = 'https://data.alpaca.markets/v2/stocks/{}/quote'.format(symbol)
    HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
    r = requests.get(BASE_URL, headers=HEADERS)
    response = json.loads(r.content)
    current_price = response['last']['price']
    print(f'Current price is: {current_price}')
    return current_price

# Function to get the purchase price of a stock
def get_purchase_price(symbol):
    BASE_URL = 'https://paper-api.alpaca.markets/v2/orders'
    HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}
    r = requests.get(BASE_URL, headers=HEADERS)
    orders = json.loads(r.content)
    for order in orders:
        if order['symbol'] == symbol and order['side'] == 'buy':
            return order['filled_avg_price']
    return None  # If no buy order found for the symbol

# Function to schedule selling of stocks 15 minutes before market close
'''
# def schedule_sell_before_market_close():
    while True:
        Check if it is 15 minutes before market close
        print('Checking Time')
        current_time = time.localtime()
        # 14 52
        if current_time.tm_hour == 14 and current_time.tm_min == 52:
            sell_all_stocks()
            break
        else:
            time.sleep(60)  
'''
# Function to sell all stocks
def sell_all_stocks():
    stocks_to_sell = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    for stock in stocks_to_sell:
        create_order(symbol=stock, qty=1, side='sell', type='market', time_in_force='day')
    # orders = get_orders()
    # for order in orders:
    #   create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')


def profitLoss():
    r = requests.get(POSITIONS_URL, headers=HEADERS)
    response = json.loads(r.content)
    stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
    floatsList = []
    # unrealized_plpc
    for stock in stocks:
        for item in response:
            if item['symbol'] == stock:
                print(item['unrealized_plpc'])
                #return response['unrealized_plpc']
    for stock in stocks:
        pl = [item['symbol'] and item['unrealized_plpc'] for item in response if item['symbol'] == stock]
        for ploss in pl:
            floatsList.append(float(ploss)*100)
            print(f'Ploss: {ploss}')
            print(f'{stock}: {ploss}')
        #return float(ploss)
    return floatsList


    
# Function to monitor stock prices and adjust strategies
def monitor_stock_pl():
    if is_trading_hours():
        print('Monitoring Profit/Loss')
        print('Waiting 10 seconds to prevent a wash...')
        time.sleep(10) 

        # P/L: Sell if 1% profit and 1% loss
        stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
        pl_list = profitLoss() 
        for stock, pl in zip(stocks, pl_list):
            if pl >= 1:
                print(f'The profit/loss value is {pl} for {stock} is greater than 1. The percentage is: {pl:.2f}%')
                print(f'Selling shares based on profit for {stock}')
                sell_all_shares(stock)
            
            elif pl <= -1:
                print(f'The profit/loss value is {pl} for {stock} is greater than -1. The percentage is: {pl:.2f}%')
                print(f'Selling shares based on loss for {stock}')
                sell_all_shares(stock)
            else:
               print(f'{stock} does not have a profit/loss of 1%, it has a profit/loss of: {pl:.2f}')

    else:
        pass
    

def sell_all_shares(stock):
     if stock == 'AAPL':
        URL = CLOSEPOSAAPL_URL
     if stock == 'TSLA':
          URL = CLOSEPOSTSLA_URL
     if stock == 'AMZN':
          URL = CLOSEPOSAMZN_URL
     if stock == 'GOOG':
          URL = CLOSEPOSGOOG_URL
     if stock == 'META':
          URL = CLOSEPOSMETA_URL
     if stock == 'MSFT':
          URL = CLOSEPOSMSFT_URL

     r = requests.delete(URL, headers=HEADERS)
     print(r.text)



    
    
def monitor_stock_price():
    if is_trading_hours():
        print('It is within trading hours, monitoring stock prices...')
        stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOG', 'META', 'MSFT']
        for stock in stocks:
            pass



def get_closedorders():
     r = requests.get(CLOSED_ORDERS, headers=HEADERS)
     return json.loads(r.content)

def get_neworders():
    r = requests.get(NEW_ORDERS, headers=HEADERS)
    return json.loads(r.content)


def mainWindow():
     welcome.destroy()
     orderingGUI()
     #orderingGUI()
     get_cash()

def range_trading():
    # Logic for Range Trading mode
    print("Range Trading button clicked")
    # Add more logic here as needed

def original_trading():
    # Logic for Original mode
    print("Original button clicked")
    # Add more logic here as needed
     
def orderingGUI():
    global root
    root = tk.Tk()
     #root.state('zoomed')
     #root.attributes('-fullscreen', True)
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Code Craft - Ordering Stocks')
    #root.state('zoomed')
    global entry1, spin, v, j, k

    # Empty spaces for formatting
    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=1, row=0)
    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=2, row=0)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=3, row=5)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=4, row=0)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=5, row=0)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=0)

    # Display the user's cash amount
    cash = get_cash()
    cashAmount = tk.Label(root, text=f'You currently have: ${cash}', font=('TkDefaultFont', 18, 'bold'))
    cashAmount.grid(column=6, row=3)

    genmess = tk.Label(root, text='Currently buying one share at market price using: day time in force ', font=('TkDefaultFont', 18, 'bold'))
    genmess.grid(column=6, row=4)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=5)


    # Column headers for stock symbol and current stock price
    headers = tk.Label(root, text='Stock Symbol | Current Stock Price', font=('TkDefaultFont', 18, 'bold'))
    headers.grid(column=6, row=7)

    # AAPL
    AAPLprice = get_tradePrice(AAPLTRADE_PRICE)
    aaplLabel = tk.Label(root, text=f'AAPL | ${AAPLprice}', font=('TkDefaultFont', 18, 'bold'))
    aaplLabel.grid(column=6, row=8)
    print(f"AAPL price: {AAPLprice}") 

    # MSFT
    MSFTprice = get_tradePrice(MSFTTRADE_PRICE)
    msftLabel = tk.Label(root, text=f'MSFT | ${MSFTprice}', font=('TkDefaultFont', 18, 'bold'))
    msftLabel.grid(column=6, row=9)
    
    # META
    METAprice = get_tradePrice(METATRADE_PRICE)
    metaLabel = tk.Label(root, text=f'META | ${METAprice}', font=('TkDefaultFont', 18, 'bold'))
    metaLabel.grid(column=6, row=10)

    # TSLA
    TSLAprice = get_tradePrice(TSLATRADE_PRICE)
    tslaLabel = tk.Label(root, text=f'TSLA | ${TSLAprice}', font=('TkDefaultFont', 18, 'bold'))
    tslaLabel.grid(column=6, row=11)

    # AMZN
    AMZNprice = get_tradePrice(AMZNTRADE_PRICE)
    amznLabel = tk.Label(root, text=f'AMZN | ${AMZNprice}', font=('TkDefaultFont', 18, 'bold'))
    amznLabel.grid(column=6, row=12)

    # GOOG
    GOOGprice = get_tradePrice(GOOGTRADE_PRICE)
    googLabel = tk.Label(root, text=f'GOOG | ${GOOGprice}', font=('TkDefaultFont', 18, 'bold'))
    googLabel.grid(column=6, row=13)

    # Automatic update to another screen
    root.after(10000, congratScreen)
     

def congratScreen():
    global congrat, selection, today
    congrat = tk.Tk()
    congrat.title('Congratulations')
    congrat.geometry('{}x{}'.format(congrat.winfo_screenwidth(), congrat.winfo_screenheight()))

    # Creating the two frames: top and bottom
    topframe = Frame(congrat)
    topframe.pack(side=TOP, fill='none')
    bottomframe = Frame(congrat)
    bottomframe.pack(side=BOTTOM, fill='none', expand=True)
    
    message = tk.Label(topframe, text='Would you like to make another order?',font=('TkDefaultFont', 18))
    message.pack()
    
    yesbtn = Button(congrat, text='Yes', bd=5, command=lambda: [congrat.destroy(), welcomeScr()], font=('TkDefaultFont', 18))
    nobtn = Button(congrat, text='No', bd=5,command=lambda: [congrat.destroy()], font=('TkDefaultFont', 18))
    yesbtn.pack()
    nobtn.pack()

    message2 = tk.Label(bottomframe, text='OPEN ORDERS',font=('TkDefaultFont', 18))
    message2.pack()


    
    response = get_neworders()

    #table = ttk.Treeview(lframe)
    columns = ('Symbol', 'Quantity', 'Side', 'Status')
    table = ttk.Treeview(bottomframe, columns=columns, show='headings')
    #table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
    table.heading('Symbol', text='Symbol')
    table.heading('Quantity', text='Quantity')
    table.heading('Side', text='Side')
    table.heading('Status', text='Status')


    # symbol, qty, side, status
    for order in response:
        symbol = order['symbol']
        qty = order['qty']
        side = order['side']
        status = order['status']
        table.insert('', 'end', values=(symbol, qty, side, status))

    table.pack()
    root.destroy()

    #select.destroy()

def welcomeScr():
    welcome = tk.Tk()
    welcome.title('Code Craft - Alpaca Trading API')
    welcome.state('zoomed')
    image = Image.open('CodeCraftLogo.png')
    image = ImageTk.PhotoImage(image)

    top = Frame(welcome)
    top.pack(side=TOP)
    left = Frame(welcome)
    left.pack(side=LEFT)
    right = Frame(welcome)
    right.pack(side=RIGHT)

    image_label = tk.Label(top, image=image)
    image_label.pack()

    # activate_bot, orderingGui, welcome.destroy
    buyBtn = Button(left, text='BUY Stocks', bd='5', command=lambda:[orderingGUI(), welcome.destroy(), activate_bot()],font=('TkDefaultFont', 18))
    buyBtn.pack(pady=40)

    btn_deactivate = Button(left, text='SELL Stocks', bd='5', command=lambda:[deactivate_bot(), congratScreen()], font=('TkDefaultFont', 18))
    btn_deactivate.pack(pady=40)


    welcome.title('Code Craft - Order Table')
    welcome.geometry('{}x{}'.format(welcome.winfo_screenwidth(), welcome.winfo_screenheight()))

    # Table to list orders
    response = get_closedorders()

    #table = ttk.Treeview(lframe)
    columns = ('Symbol', 'Quantity', 'Side', 'Status')
    table = ttk.Treeview(welcome, columns=columns, show='headings')
    #table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
    table.heading('Symbol', text='Symbol')
    table.heading('Quantity', text='Quantity')
    table.heading('Side', text='Side')
    table.heading('Status', text='Status')


    # symbol, qty, side, status
    for order in response:
        symbol = order['symbol']
        qty = order['qty']
        side = order['side']
        status = order['status']
        table.insert('', 'end', values=(symbol, qty, side, status))

    table.pack()


# Welcome screen
welcome = tk.Tk()
welcome.title('Code Craft - Alpaca Trading API')
welcome.state('zoomed')
image = Image.open('CodeCraftLogo.png')
image = ImageTk.PhotoImage(image)
# Create and place the Range Trading button
range_button = tk.Button(welcome, text="Range Trading", command=range_trading, font=("Helvetica", 12), width=15)
range_button.pack(pady=10)

# Create and place the Original Trading button
original_button = tk.Button(welcome, text="Original", command=original_trading, font=("Helvetica", 12), width=15)
original_button.pack(pady=10)

top = Frame(welcome)
top.pack(side=TOP)
left = Frame(welcome)
left.pack(side=LEFT)
right = Frame(welcome)
right.pack(side=RIGHT)

image_label = tk.Label(top, image=image)
image_label.pack()


buyBtn = Button(left, text='BUY Stocks', bd='5', command=lambda:[orderingGUI(), welcome.destroy(), activate_bot()],font=('TkDefaultFont', 18))
buyBtn.pack(pady=40)

btn_deactivate = Button(left, text='SELL Stocks', bd='5', command=lambda:[deactivate_bot(), congratScreen()], font=('TkDefaultFont', 18))
btn_deactivate.pack(pady=40)


welcome.title('Code Craft - Order Table')
welcome.geometry('{}x{}'.format(welcome.winfo_screenwidth(), welcome.winfo_screenheight()))

# Table to list orders
response = get_closedorders()

#table = ttk.Treeview(lframe)
columns = ('Symbol', 'Quantity', 'Side', 'Status')
table = ttk.Treeview(welcome, columns=columns, show='headings')
#table['columns'] = ('Symbol', 'Quantity', 'Side', 'Status')
table.heading('Symbol', text='Symbol')
table.heading('Quantity', text='Quantity')
table.heading('Side', text='Side')
table.heading('Status', text='Status')


# symbol, qty, side, status
for order in response:
     symbol = order['symbol']
     qty = order['qty']
     side = order['side']
     status = order['status']
     table.insert('', 'end', values=(symbol, qty, side, status))

table.pack()

# Calling the GUI
#mainWindow()
#orderingGUI()
profitLoss()

welcome.mainloop()
#root.mainloop()




'''
def price_increased(current_price, previous_price):
    return current_price > previous_price

def price_decreased(current_price, previous_price):
    return current_price < previous_price

previous_price = {}
'''

'''
# Function to sell all stocks
def sell_all_stocks():
    orders = get_orders()
    current_time = time.localtime()
    for order in orders:
        symbol = order['symbol']
        price = order['price']
        if symbol not in previous_price:
            previous_price[symbol] = price
            continue

        price_change = (price - previous_price[symbol]) / previous_price[symbol] * 100
        if price_change >= 1:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
            previous_price[symbol] = price
        elif price_change <= -1:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
            previous_price[symbol] = price
        elif current_time.tm_hour == 15  and current_time.tm_min == 55:
            create_order(symbol=order['symbol'], qty=order['qty'], side='sell', type='market', time_in_force='day')
        deactivate_bot()
'''
'''
def profitLoss():
    r = requests.get(POSITIONS_URL, headers=HEADERS)
    response = json.loads(r.content)
    stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'META', 'MSFT']
    # unrealized_plpc
    for stock in stocks:
        if response['symbol'] == stock:
            print(response['unrealized_plpc'])
            return response['unrealized_plpc']
'''




# DOESNT WORK YET
# Function to monitor stock prices and adjust strategies
'''def monitor_stock_pl():
    while True:
        if is_trading_hours():
            print('Monitor stock pl method')
            # Implement your monitoring and strategy adjustment logic here
            # put the price that it was bought at and check the price that it is at now
            # calculate the percentage
            stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'META', 'MSFT']
            for stock in stocks:
                if profitLoss() > 0:
                    print('Greater than 0')

                else:
                    print('Less than 0')


        else:
            break'''

'''def monitor_stock_prices():
    while True:
        if is_trading_hours():
            # Implement your monitoring and strategy adjustment logic here
            # put the price that it was bought at and check the price that it is at now
            # calculate the percentage
            stocks = ['AAPL', 'TSLA', 'AMZN', 'GOOGL', 'META', 'MSFT']
            for stock in stocks:
                # 159.75
                tradedPrice = get_tradePrice(stock)
                time.sleep(60)
                #159.74
                currentPrice = get_tradePrice(stock)

                priceChange = currentPrice - tradedPrice

                if profitLoss > 0:
                    print('Greater than 0')

                else:
                    print('Less than 0')


        else:
            break
        time.sleep(60)'''

