import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import seaborn as sns
import datetime as dt
from datetime import datetime, timedelta
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

def create_melted_dfs(df_prices, df_recos):
    """
    Merging the price and reco dfs and then calculating returns after df_recos
    Then melting the dfs so that we can boxplot them
    """
    prices = df_prices
    df = df_recos

    df = prices.merge(df, on='Date',how='left')
    df.drop(columns = ['Open','High','Low','Close','Volume','From Grade'],inplace= True)

    dt_adj = 261/365 #use to adjust our desired windows as US has 261 working days a year
    time_periods = [30,60,180,360,360*2,360*3,360*5]

    for period in time_periods:
        df['{} day return'.format(period)] = df.loc[:,'Adj Close'].pct_change(periods = int(dt_adj*period))

    for period in time_periods:
        df['{} day return'.format(period)] = df['{} day return'.format(period)].shift(-int(dt_adj*30))

    df.rename(columns = {'720 day return':'2 year return',\
                     '1080 day return':'3 year return',\
                     '1800 day return':'5 year return'}, inplace = True)

    #Need to format df so that it can be used in a boxplot
    return_gp = df.groupby(['To Grade','Firm']).mean().reset_index()
    return_gp.drop(columns = 'Adj Close',inplace=True)

    return_melt = return_gp.melt(id_vars=['To Grade','Firm'])

    return_melt_short = return_melt.loc[(return_melt['variable']=='30 day return')|
                                        (return_melt['variable']=='90 day return')|
                                        (return_melt['variable']=='180 day return')|
                                        (return_melt['variable']=='360 day return')]

    return_melt_long = return_melt.loc[(return_melt['variable']=='2 year return')|
                                        (return_melt['variable']=='3 year return')|
                                       (return_melt['variable']=='5 year return')|
                                        (return_melt['variable']=='360 day return')]

    return return_melt_short, return_melt_long

#Current issue is that date axis is fucked up
def plot_prices(df_prices, plot_buy, plot_sell, symbol, ax= None):
    ax = ax or plt.gca()

    line_alpha = 0.6
    marker_alpha = 1
    line_color = 'b'
    buy_color = 'g'
    sell_color = 'r'
    marker_s = 70

    plt.plot(df_prices.Date, df_prices['Adj Close'], color =line_color, alpha=line_alpha)
    plt.scatter(x = plot_buy.Date, y = plot_buy['Adj Close'], color = buy_color, marker = '^', label = 'Buy Reco',s=marker_s, alpha = marker_alpha)
    plt.scatter(x = plot_sell.Date, y = plot_sell['Adj Close'], color = sell_color, marker = 'v', label = 'Sell Reco',s=marker_s, alpha=marker_alpha)
    plt.title('{} Buy and Sell Recommendations'.format(symbol))
    plt.xlabel('Year')
    plt.ylabel('Price')
    plt.legend(loc=2)

    datemin = plot_buy.Date.min() - timedelta(days=180)
    datemax = df_prices.Date.max() + timedelta(days=30)
    ax.set_xlim(datemin, datemax)
    return ax

def short_return_plot(return_melt_short, symbol, ax = None):
    ax = ax or plt.gca()

    sns.boxplot(x='variable',y = 'value', hue = 'To Grade',data = return_melt_short)
    plt.title('{} Short Run Percent Return After Reco'.format(symbol))
    plt.ylabel('Percent Return')
    plt.xlabel('Return Window')
    plt.legend(loc = 2)

    #Format y ticks to percentage
    y_vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in y_vals])

    return ax

def long_return_plot(return_melt_long, symbol, ax = None):
    ax = ax or plt.gca()

    sns.boxplot(x='variable',y = 'value', hue = 'To Grade',data = return_melt_long)
    plt.title('{} Long Run Percent Return After Reco'.format(symbol))
    plt.ylabel('Percent Return')
    plt.xlabel('Return Window')
    plt.legend(loc = 2)

    #Format y ticks to percentage
    y_vals = ax.get_yticks()
    ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in y_vals])

    return ax



def all_plots(df_prices, plot_buy, plot_sell, return_melt_short, return_melt_long, symbol):
    fig, ax = plt.subplots(3,1,figsize=(10,15))
    plt.subplots_adjust(hspace = 0.4)

    plt.subplot(3, 1, 1)
    plot_prices(df_prices,plot_buy, plot_sell, symbol)

    plt.subplot(3,1,2)
    short_return_plot(return_melt_short, symbol)

    plt.subplot(3,1,3)
    long_return_plot(return_melt_long, symbol)

    fig.suptitle('{} Analysis of Analyst Recommendations'.format(symbol), fontsize=20)

    strFile = 'static/images/new_plot.png'
    #Keep getting the GM picture...
    if os.path.isfile(strFile):
        os.remove(strFile)
    plt.savefig(strFile)


def flask_get_plots(symbol):
    """
    Call this in Main.py to do all transformations, save plot, and then retrieve plot in plots template
    """
    #https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask
    try:
        df_recos, df_prices = get_frames(symbol)
        plot_buy, plot_sell = format_dfs(df_recos,df_prices)
        return_melt_short, return_melt_long = create_melted_dfs(df_prices, df_recos)
        all_plots(df_prices, plot_buy, plot_sell, return_melt_short, return_melt_long, symbol)
        image = [i for i in os.listdir('static/images') if i.endswith('.png')][0]
        return render_template('plots.html', name = 'new_plot', user_image = image)
    except:
        return render_template('error.html',name = 'error')
