 """
  basic argeparse arguments: 
    --- start date
    --- end date 
    --- ticker name --> comma separated list of tickers 
    --- strategy name
    --- output --> a row with stock name, parameter values including profit 
    -------------> if multiple stocks (if comma separated ticker name) then run the strategy on multiple stocks, and produce a table with metrics, each row a new stock + strategy
    -------------> if multiple stocks and multiple strategies, just have it enumerated
    -------------> columns --> strategy, other metrics for columns
    -------------> row is each stock, store this in a dateframe to make sure it gets printed easily
    --- plot for a single 
    At the end of it, I should be able to give in a ticker and start_end dates, and strategy and get a plot
    I
    the point of this is to 

    Step 1: create an argeparse component with ticker_name, end_date, start_date, strategy_name 
    Step 2: pretty print this output 
    Step 3: create a plot inside an html folder for a single 
  """
1. Make RSI Oscillator work 
2. Make other strategies work
3. Make sure they output a prettyprint table 


#TODO 
-- Add multiple strategies
-- multiple stocks, multiple strategies 
-- 

## ATR 

An expanding ATR indicates increased volatility in the market, with the range of each bar getting larger. A reversal in price with an increase in ATR would indicate strength behind that move. ATR is not directional so an expanding ATR can indicate selling pressure or buying pressure. High ATR values usually result from a sharp advance or decline and are unlikely to be sustained for extended periods.
A low ATR value indicates a series of periods with small ranges (quiet days). These low ATR values are found during extended sideways price action, thus the lower volatility. A prolonged period of low ATR values may indicate a consolidation area and the possibility of a continuation move or reversal.
ATR is very useful for stops or entry triggers, signaling changes in volatility. Whereas fixed dollar- point or percentage stops will not allow for volatility, the ATR stop will adapt to sharp price moves or consolidation areas, which can trigger an abnormal price movement in either direction. Use a multiple of ATR, such as 1.5 x ATR, to catch these abnormal price moves

# data['Slope_Area'] = np.abs(data[key_slope_small] - data[key_slope_large])

    # small_slope_threshold = 0.05

    # data['Signals'][int(small_win):] = np.where(
    #     (data[key_small][int(small_win):] > data[key_large][int(small_win):]) & 
    #     (data[key_slope_small][int(small_win):] >= small_slope_threshold), 1, 0
    # )

    # data['Signals'][int(small_win):] = np.where(
    #     (data[short_window][int(small_win):] > data[long_window][int(small_win):]) & 
    #     (data['Slope_Area'][int(small_win):] > area_threshold), 1, 0
    # )

    # data['Signals'][int(small_win):] = np.where(
    #     (data[short_window][int(small_win):] > data[long_window][int(small_win):]) & 
    #     (data[key_slope_small][int(small_win):] > slope_threshold) & 
    #     (data[key_slope_large][int(small_win):] > slope_threshold), 1, 0

    ##########


#   plt.plot(df.index, df['close'], label='Close Price')
#   plt.plot(df[key_small], label=label1)
#   plt.plot(df[key_large], label=label2)

#   plt.plot(df.loc[df['Signal'] == 1.0].index, 
#           df[key_small][df['Signal'] == 1.0], 
#           '^', markersize=10, color='g', label='Buy Signal')
  
#   for i in df.loc[df['Signal'] == 1.0].index:
#     plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='g', va='bottom')

#   plt.plot(df.loc[df['Signal'] == -1.0].index, 
#           df[key_small][df['Signal'] == -1.0], 
#           'v', markersize=10, color='r', label='Sell Signal')
  
#   for i in df.loc[df['Signal'] == -1.0].index:
#     plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='r', va='bottom')

#   plt.title('Stock Price with Buy and Sell Signals')
#   plt.xlabel('Date')
#   plt.ylabel('Price')
#   plt.legend()
#   plt.grid(True)

  ########

#   plt.tight_layout()
#   plt.show()