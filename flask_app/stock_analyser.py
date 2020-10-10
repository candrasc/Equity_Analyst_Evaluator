import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from flask import render_template
import os

def get_ticker(symbol):
    symbol = symbol
    ticker = yf.Ticker(symbol)
    return ticker

def get_recos(ticker):
    df_base = ticker.recommendations.reset_index()
    return df_base

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
    #Fix date time to not include seconds
    df['Date'] = df['Date'].values.astype('<M8[M]')
    return df

def remove_bad_recos(df):
    df = df.loc[(df['To Grade'] == 'Hold')|(df['To Grade']=='Buy')|(df['To Grade']=='Sell')]
    return df

#This function combines all above functions to get the formatted dataframes for plotting
def get_frames(symbol):
    ticker = get_ticker(symbol)
    df_recos = get_recos(ticker)
    df_prices = get_prices(symbol)

    df_recos = standardize_recos(df_recos)
    df_recos= remove_bad_recos(df_recos)
    return df_recos, df_prices
"""
We have all the required functions to retrieve the required data.

The below functions will be focused on formatting and plotting
starting with the line plot that has buy sell recos on it
"""

#Merges the recos and prices dfs for plotting and analysis
def format_dfs(df_recos, df_prices):

    df_buy = df_recos.loc[df_recos['To Grade']=='Buy']
    df_sell = df_recos.loc[df_recos['To Grade']=='Sell']

    plot_buy = df_prices.merge(df_buy,on='Date', how = 'left')
    plot_sell = df_prices.merge(df_sell,on='Date', how = 'left')

    plot_buy = plot_buy.loc[plot_buy['To Grade']=='Buy']
    plot_sell = plot_sell.loc[plot_sell['To Grade']=='Sell']
    return plot_buy, plot_sell

#Current issue is that date axis is fucked up
def line_plot(prices, plot_buy, plot_sell, symbol):
    fig = plt.figure(figsize = (15,8))
    ax = fig.add_subplot(1, 1, 1)
    plt.style.use('ggplot')

    #variables for plot to make tweaking easier
    line_alpha = 0.6
    marker_alpha = 1
    line_color = 'b'
    buy_color = 'g'
    sell_color = 'r'
    marker_s = 70

    plt.plot(prices.Date, prices['Adj Close'], color =line_color, alpha=line_alpha)
    plt.scatter(x = plot_buy.Date, y = plot_buy['Adj Close'], color = buy_color, marker = '^', label = 'Buy Reco',s=marker_s, alpha = marker_alpha)
    plt.scatter(x = plot_sell.Date, y = plot_sell['Adj Close'], color = sell_color, marker = 'v', label = 'Sell Reco',s=marker_s, alpha=marker_alpha)
    plt.title('{} Buy and Sell Recommendations'.format(symbol))
    plt.legend(loc=2)

    #https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask
    strFile = 'static/images/new_plot.png'

    #Keep getting the GM picture...
    if os.path.isfile(strFile):
        os.remove(strFile)
    plt.savefig(strFile)
    image = [i for i in os.listdir('static/images') if i.endswith('.png')][0]
    return render_template('plots.html', name = 'new_plot', user_image = image)

def flask_line_plot(symbol):
    df_recos, df_prices = get_frames(symbol)
    plot_buy, plot_sell = format_dfs(df_recos,df_prices)
    return line_plot(df_prices,plot_buy,plot_sell,symbol)

"""
Next we will format the dfs for boxplots in order to compare
returns after a buy/hold/sell reco are made
"""
