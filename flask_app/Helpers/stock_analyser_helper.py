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

class DoesItAll:
    """
    Pull data from yfinance and format it for further use
    """
    def __init__(self, symbol, date_min = None, date_max = None, return_windows = [30,60,180,360]):
        self.symbol = symbol
        self.ticker = yf.Ticker(self.symbol)
        self.date_min = date_min
        self.date_max = date_max
        self.return_windows = return_windows
        self.prices = self._get_prices()
        self.recos = self._get_recos()

    def _get_prices(self):
        """
        set prices class attribute with price data of given ticker
        """
        df = yf.download(self.symbol, interval = '1d', start=self.date_min, end=self.date_max, progress=False).reset_index()
        return df

    def _get_recos(self):
        """
        Get reco data and rename similar reco types to either buy, sell or hold
        Set reco class attribute
        """
        df = self.ticker.recommendations.reset_index()

        #Get Date in same dt format as prices df
        df['Date'] = df['Date'].astype('str')
        df['Date'] = df['Date'].apply(lambda x: x[:-9])
        df['Date'] = pd.to_datetime(df['Date'])
        #filter recos by prices dates incase we filtered the prices df
        df = df.loc[df['Date'].isin(self.prices.Date)]

        df['To Grade'] = np.where((df['To Grade'].isin(['Outperform','Overweight','Positive','Market Outperform','Strong Buy'])),
                                                        ('Buy'),df['To Grade'])
        #Change terms to Hold
        df['To Grade'] = np.where((df['To Grade'].isin(['Neutral','Market Perform','Equal-Weight', 'Sector Perform','Perform','Equal-weight','In-Line','Peer Perform','Sector Weight'])),
                                                        'Hold',df['To Grade'])
        #Change terms to Sell
        df['To Grade'] = np.where((df['To Grade'].isin(['Underperform','Underweight','Reduce','Negative'])),
                                                        'Sell',df['To Grade'])
        #Fix date time to not include seconds
        df['Date'] = df['Date'].values.astype('<M8[M]')

        #Remove bad recos
        df = df.loc[(df['To Grade'] == 'Hold')|(df['To Grade']=='Buy')|(df['To Grade']=='Sell')]

        bad_dates = df.loc[df.Date.isin(self.prices.Date)==False].Date.reset_index()
        bad_dates = bad_dates.drop(columns = 'index')
        df.Date = np.where(df.Date.isin(bad_dates.Date), df.Date - timedelta(days=2), df.Date)

        return df

    def _prep_for_lineplot(self):
        recos = self.recos
        prices = self.prices


        df_buy = recos.loc[recos['To Grade']=='Buy']
        df_sell = recos.loc[recos['To Grade']=='Sell']

        plot_buy = prices.merge(df_buy,on='Date', how = 'left')
        plot_sell = prices.merge(df_sell,on='Date', how = 'left')

        plot_buy = plot_buy.loc[plot_buy['To Grade']=='Buy']
        plot_sell = plot_sell.loc[plot_sell['To Grade']=='Sell']
        return prices, plot_buy, plot_sell

    def _prep_for_boxplot(self):
        """
        Merging the price and reco dfs and then calculating returns after recos
        Then melting the dfs so that we can boxplot them
        """
        recos = self.recos
        prices = self.prices

        df = prices.merge(recos, on='Date',how='left')
        df.drop(columns = ['Open','High','Low','Close','Volume','From Grade'],inplace= True)

        dt_adj = 261/365 #use to adjust our desired windows as US has 261 working days a year
        return_windows = self.return_windows

        #calculate percent return
        for period in return_windows:
            df['{} day return'.format(period)] = df.loc[:,'Adj Close'].pct_change(periods = int(dt_adj*period))

        #shift df back so percent return for a given period appears the day the reco was made
        for period in return_windows:
            df['{} day return'.format(period)] = df['{} day return'.format(period)].shift(-int(dt_adj*30))

        #Need to format df so that it can be used in a boxplot
        return_gp = df.groupby(['To Grade','Firm']).mean().reset_index()
        return_gp.drop(columns = 'Adj Close',inplace=True)

        df_melt = return_gp.melt(id_vars=['To Grade','Firm'])

        return df_melt

    """
    The below functions are dedicated to plotting
    """

    def prices_lineplot(self, ax= None):

        symbol = self.symbol
        prices, plot_buy, plot_sell = self._prep_for_lineplot()

        ax = ax or plt.gca()

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
        plt.xlabel('Year')
        plt.ylabel('Price')
        plt.legend(loc=2)

        datemin = plot_buy.Date.min() - timedelta(days=30)
        datemax = prices.Date.max() + timedelta(days=30)
        ax.set_xlim(datemin, datemax)
        return ax

    def pct_return_boxplot(self, ax = None):

        symbol = self.symbol
        df = self._prep_for_boxplot()

        ax = ax or plt.gca()

        sns.boxplot(x='variable',y = 'value', hue = 'To Grade',data = df)
        plt.title('{} Percent Return After Reco'.format(symbol))
        plt.ylabel('Percent Return')
        plt.xlabel('Return Window')
        plt.legend(loc = 2)

        #Format y ticks to percentage
        y_vals = ax.get_yticks()
        ax.set_yticklabels(['{:3.0f}%'.format(x * 100) for x in y_vals])

        return ax

    def all_plots(self):
        symbol = self.symbol

        fig, ax = plt.subplots(2,1,figsize=(15,15))
        plt.subplots_adjust(hspace = 0.4)

        plt.subplot(2, 1, 1)
        self.prices_lineplot()

        plt.subplot(2,1,2)
        self.pct_return_boxplot()

        fig.suptitle('{} Evaluation of Analyst Recommendations'.format(symbol), fontsize=20)


        full_path = 'static/images/new_plot.png'


        if os.path.isfile(full_path):
            os.remove(full_path)
        plt.savefig(full_path)
