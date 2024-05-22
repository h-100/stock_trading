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