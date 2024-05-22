import pdb

import pandas as pd
from backtesting import Strategy
from tqdm import tqdm


class SupportResistanceRSI(Strategy):  
  ## detect initial support fractal candle
  wick_threshold = 0.0005
  df = pd.DataFrame()

  ## detect initial support fractal candle
  def support(self, df1, l, n1, n2): #n1 n2 before and after candle l
      if (df1.Low[l - n1:l].min() < df1.Low[l] or
          df1.Low[l + 1:l + n2 + 1].min() < df1.Low[l]):
          return 0

      ## select candles showing a strong rejection movement
      ## a candle wick exceeding a certain threshold can be considered a strong rejection movement
      candle_body = abs(df1.Open[l] - df1.Close[l])
      lower_wick = min(df1.Open[l], df1.Close[l]) - df1.Low[l]
      if (lower_wick > candle_body) and (lower_wick > self.wick_threshold):
          return 1

      return 0
  ##detect resistance candles
  def resistance(self, df1, l, n1, n2): #n1 n2 before and after candle l
      if ( df1.High[l-n1:l].max() > df1.High[l] or
        df1.High[l+1:l+n2+1].max() > df1.High[l] ):
          return 0

      candle_body = abs(df1.Open[l]-df1.Close[l])
      upper_wick = df1.High[l]-max(df1.Open[l], df1.Close[l])
      if (upper_wick > candle_body) and (upper_wick > self.wick_threshold) :
          return 1

      return 0

  def closeResistance(self, l, levels, lim, df):

      if len(levels) == 0:
          return 0


      ## the highest wick should be within a threshold distance of the highest R level
      c1 = abs(df.High[l] - min(levels, key=lambda x:abs(x - df.High[l]))) <= lim

      ## body top (open or close)'s difference from the high of the R level should be within a limit
      ## alternatively body should be contained within the level
      c2 = abs( max(df.Open[l], df.Close[l]) - min(levels, key=lambda x:abs(x-df.High[l])) ) <= lim

      ##whichever one is lower (open or close) should be less than the (min) high of the R candles
      c3 = min(df.Open[l], df.Close[l]) < min(levels, key=lambda x:abs(x-df.High[l]))

      ## low of the candle should be lower than the (min) high of the R candles
      c4 = df.Low[l] < min(levels, key=lambda x:abs(x - df.High[l]))

      ### either one of the two c1 or c2 should meet the criteria
      if( (c1 or c2) and c3 and c4):
          return min(levels, key=lambda x:abs(x - df.High[l]))
      else:
          return 0

  def closeSupport(self, l,levels,lim, df):

      if len(levels) == 0:
          return 0

      ## candle's low should be within a threshold distance of the candle with lowest closest to the current candle
      c1 = abs(df.Low[l] - min(levels, key=lambda x:abs(x - df.Low[l]))) <= lim

      ## candle's minimum (either open or close) should be within a threshold distance of the min level support candle
      c2 = abs(min(df.Open[l],df.Close[l]) - min(levels, key=lambda x:abs(x - df.Low[l]))) <= lim

      ## the max of either open or close should be greater than the minimum of all support candles
      c3 = max(df.Open[l], df.Close[l]) > min(levels, key=lambda x:abs(x - df.Low[l]))

      ## the high of the candle should be greater than the min of all S candles
      c4 = df.High[l] > min(levels, key=lambda x:abs(x-df.Low[l]))

      if( (c1 or c2) and c3 and c4 ):
          return min(levels, key=lambda x:abs(x-df.Low[l]))
      else:
          return 0
      

  def is_below_resistance(self, l, level_backCandles, level, df):
      return df.loc[l - level_backCandles:l - 1, 'High'].max() < level

  def is_above_support(self, l, level_backCandles, level, df):
      return df.loc[l - level_backCandles:l - 1, 'Low'].min() > level

  def check_candle_signal(self, l, n1, n2, backCandles, df):
      
      ss = [] # support levels
      rr = [] # resistance levels

      ## merge all levels that are close to each other


      for subrow in range(l - backCandles, l - n2):
          if self.support(df, subrow, n1, n2):
              ss.append(df.Low[subrow])
          if self.resistance(df, subrow, n1, n2):
              rr.append(df.High[subrow])

      ss.sort() #keep lowest support when popping a level
      for i in range(1, len(ss)):
          if(i >= len(ss)):
              break
          if abs(ss[i] - ss[i-1]) <= 0.0001: # merging close distance levels
              ss.pop(i)

      rr.sort(reverse=True) # keep highest resistance when popping one
      for i in range(1,len(rr)):
          if(i >= len(rr)):
              break
          if abs(rr[i]-rr[i-1])<=0.0001: # merging close distance levels
              rr.pop(i)

      #----------------------------------------------------------------------
      # joined levels
      # the same level can exist as support and resistance depending upon where the price is heading
      rrss = rr+ss
      rrss.sort()
      for i in range(1,len(rrss)):
          if(i>=len(rrss)):
              break
          if abs(rrss[i]-rrss[i-1])<=0.0001: # merging close distance levels
              rrss.pop(i)
      cR = self.closeResistance(l, rrss, 150e-5, df)
      cS = self.closeSupport(l, rrss, 150e-5, df)

      if (cR and self.is_below_resistance(l, 6, cR, df) and df.RSI[l-1:l].min() < 35): # and df.RSI[l]>65
          # 1 is a bearish signal, we are approaching resistance level from below, approaching downtrend
          return 1
      elif(cS and self.is_above_support(l, 6, cS, df) and df.RSI[l-1:l].max() > 65 ):#and df.RSI[l]<35
          # 2 is a bullish signal
          return 2
      else:
          return 0

  def SIGNAL(self):
      return self.df.signal
  
  def convert_to_dataframe(self):
      df = pd.DataFrame()
      for i in range(len(self.data)):
        temp = pd.DataFrame({
            'Open': self.data.Open[i],
            'High': self.data.High[i],
            'Low': self.data.Low[i],
            'Close': self.data.Close[i],
            'Volume': self.data.Volume[i],
            'RSI': self.data.RSI[i]
          }, index=[1])

        df = pd.concat([df, temp])
      
      df.reset_index(inplace=True)
        
      return df
          


  def init(self):
    super().init()
    self.df = self.convert_to_dataframe()

    n1 = 8 # left preceding candles
    n2 = 6 # forward preceding candles

    backCandles = 140

    signal = [0 for i in range(len(self.df))]

    for row in tqdm(range(backCandles + n1, len(self.df) - n2)):
      # pdb.set_trace()
      signal[row] = self.check_candle_signal(row, n1, n2, backCandles, self.df)
    

    self.df["signal"] = signal
    self.df = self.df.drop('index', axis=1)
  
    # self.df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'signal']

    self.signal1 = self.I(self.SIGNAL)

  def next(self):
    super().next() 
    if self.signal1 == 2:
      self.buy()
    elif self.signal1 == 1:
      self.position.close()
