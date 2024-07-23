import talib
from backtesting import Strategy
from backtesting.lib import crossover


class RsiOscillator(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14
    
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_window)
        
    def next(self):
        if crossover(self.rsi, self.upper_bound):
            #TODO: check why not self.sell()
            self.position.close() # sell 
        elif crossover(self.lower_bound, self.rsi):
            self.buy() # buy