import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

def get_symbol():
    print('Enter the Ticker of the stock you would like to analyze: ')
    symbol = str(input()) #Change this to user input later
    return symbol

def get_ticker(symbol):
    symbol = symbol
    ticker = yf.Ticker(symbol)
    return ticker

def get_recos(ticker):
    df_base = ticker.recommendations.reset_index()
    df = df_base.copy()
    return df

def get_prices(symbol):
    symbol = symbol
    df = yf.download(symbol, interval = '1d', progress=False).reset_index()
    return df

def standardize_recos(df):
    #Change terms to buy
    df['To Grade'] = np.where((df['To Grade'].isin(['Outperform','Overweight','Positive','Market Outperform','Strong Buy'])),('Buy'),df['To Grade'])
    #Change terms to Hold
    df['To Grade'] = np.where((df['To Grade'].isin(['Neutral','Market Perform','Equal-Weight', 'Sector Perform','Perform','Equal-weight','In-Line','Peer Perform','Sector Weight'])),'Hold',df['To Grade'])
    #Change terms to Sell
    df['To Grade'] = np.where((df['To Grade'].isin(['Underperform','Underweight','Reduce','Negative'])),'Sell',df['To Grade'])
    return df

def remove_bad_recos(df):
    df_new = df.loc[(df['To Grade'] == 'Hold')|(df['To Grade']=='Buy')|(df['To Grade']=='Sell')].copy()
    return df

#This function combines all above functions to get the formatted dataframes for plotting
def get_frames():
    symbol = get_symbol()
    ticker = get_ticker(symbol)
    df_recos = get_recos(ticker)
    df_prices = get_prices(symbol)

    std_recos = standardize_recos(df_recos)
    std_recos = remove_bad_recos(std_recos)
    return std_recos, df_prices

def plot():
    std_recos, df_prices = get_frames()
    plt.plot(df_prices.Date, df_prices['Adj Close'])
    plt.show()


"""
Now we have the data frames, let's get to the plotting
"""
