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

BASE_URL = 'https://paper-api.alpaca.markets/v2'
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



def get_tradePrice(stock):
     r = requests.get(stock, headers=HEADERS)
     response = json.loads(r.content)
     price = response['trade']['p']

     return price

def get_cash():

     r = requests.get(ACCOUNT_URL, headers=HEADERS)
     response = json.loads(r.content)
     cash = response['cash']
     #print(f'Your cash amount is: ${cash}')
     return cash

def is_trading_hours():
    current_time = time.localtime()
    if current_time.tm_hour >= 9 and current_time.tm_hour < 16:
        return True
    else:
        return False
    
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
    

def get_closedorders():
     r = requests.get(CLOSED_ORDERS, headers=HEADERS)
     return json.loads(r.content)

def get_neworders():
    r = requests.get(NEW_ORDERS, headers=HEADERS)
    return json.loads(r.content)

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



# UI

def mainWindow():
     welcome.destroy()
     orderingGUI()
     #orderingGUI()
     get_cash()
     
def orderingGUI():
    global root
    root = tk.Tk()
     #root.state('zoomed')
     #root.attributes('-fullscreen', True)
    root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.title('Code Craft - Ordering Stocks')
    #root.state('zoomed')
    global entry1, spin, v, j, k
    

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

    # Display the user's cash amount
    cash = get_cash()
    cashAmount = tk.Label(root, text=f'You currently have: ${cash}', font=('TkDefaultFont', 18, 'bold'))
    cashAmount.grid(column=6, row=3)

    
    genmess = tk.Label(root, text='Currently buying one share at market price using: day time in force ',font=('TkDefaultFont', 18, 'bold'))
    genmess.grid(column=6, row=4)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=5)

    empty = tk.Label(root, text=' \n   ', width=10)
    empty.grid(column=6, row=6)

    # AAPL
    AAPLprice = get_tradePrice(AAPLTRADE_PRICE)
    buymess = tk.Label(root, text=f'AAPL at ${(AAPLprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=7)

    # MSFT
    MSFTprice = get_tradePrice(MSFTTRADE_PRICE)
    buymess = tk.Label(root, text=f'MSFT at ${(MSFTprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=8)
    
    # META
    METAprice = get_tradePrice(METATRADE_PRICE)
    buymess = tk.Label(root, text=f'META at ${(METAprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=9)

    # TSLA
    TSLAprice = get_tradePrice(TSLATRADE_PRICE)
    buymess = tk.Label(root, text=f'TSLA at ${(TSLAprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=10)

    # AMZN
    AMZNprice = get_tradePrice(AMZNTRADE_PRICE)
    buymess = tk.Label(root, text=f'AMZN at ${(AMZNprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=11)

    # GOOG
    GOOGprice = get_tradePrice(GOOGTRADE_PRICE)
    buymess = tk.Label(root, text=f'GOOG at ${(GOOGprice)}',font=('TkDefaultFont', 18, 'bold'))
    buymess.grid(column=6, row=12)

     #root.pack(side=RIGHT, fill='none', expand=True)
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
