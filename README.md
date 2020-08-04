## The purpose of this project is to evaluate the historical buy/sell/hold recommendations of analysts on any given security on the NYSE
The yfinance library gives us price data for any security listed on the New York Stock Exchange. Unfortunately, the method to pull historic analyst recommendations is slightly more limited as not all NYSE stocks have reco data available. However, most large cap stocks (especially tech stock) do have this data available and are therefore great candidates for this program. 

### How to use:
Use the 'Stock Reco Analyser' file and input any ticker for a stock trading on the NYSE into the designated ticker variable.
The program will then plot all of the buy and sell recommendations available against the historic daily close prices. This gives us a nice visualization on analyst sentiment towards the stock at different times, and how the stock performed after these predictions. 

Boxplots are also created to show the distribution of returns after a buy/hold/sell reco are made. These boxplots cover both short and longterm periods of return so that we can have a full picture of performance. Here we would like to see that the performance after a buy reco is higher than that of sell or hold recos. 

### Additional files:

I have also included a deeper dive into Tesla stock recommendations, where we look at recommendations before/during the recent price surge as well as evaluating different firms based on their recommendation performace. 

Tesla was chosen as it is a highly volatile stock that has had unpredictable fluctuations in price making many firm/analyst recommendations look ridiculous. The analysis shows that this is the case as the sell recos had higher returns on average than the buy recos. 
