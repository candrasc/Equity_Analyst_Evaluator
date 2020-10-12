## The purpose of this project is to evaluate the historical buy/sell/hold recommendations of analysts on any large cap publicly traded company in the US
The yfinance library gives us price data for any security listed in the USA. Unfortunately, the method to pull historic analyst recommendations is slightly more limited as not all stocks have reco data available. However, most large cap stocks (especially tech stock) do have this data available and are therefore great candidates for this program. 

### How to use:
I have created a Flask application and deployed it using AWS Elastic Beanstock, so that you can access the application directly from your browser. Please visit http://stockrecoevaluator-env.eba-xpfs3xmu.us-east-2.elasticbeanstalk.com/ to try it out!

Once you are on the webpage, input any ticker for a large cap stock trading in the USA into the designated ticker box.
The program will then plot all of the buy and sell recommendations available against the historic daily close prices. This gives us a nice visualization on analyst sentiment towards the stock at different times, and how the stock performed after these predictions. 

Boxplots are also created to show the distribution of returns after buy/hold/sell recos are made. These boxplots cover both short and longterm periods of return so that we can have a full picture of performance. Here we would like to see that the performance after a buy reco is higher than that of sell or hold recos. 

