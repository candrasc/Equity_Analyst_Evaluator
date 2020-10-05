import stock_analyser

df_recos, df_prices = stock_analyser.get_frames('NVDA')

df_recos['Date'] = df_recos['Date'].values.astype('<M8[M]')

print(df_recos)
