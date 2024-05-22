import pdb

import pandas as pd
from backtesting import Strategy


class SR_Candles(Strategy):  

  df = pd.DataFrame()
  length, high, low, close, open, bodydiff, highdiff, lowdiff, ratio1, ratio2 = None, None, None, None, None, None, None, None, None, None
  

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
          }, index=[1])

        df = pd.concat([df, temp])
      
      df.reset_index(inplace=True)
        
      return df

  def support(self, df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.Low[i]>df1.Low[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.Low[i]<df1.Low[i-1]):
            return 0
    return 1

  def resistance(self, df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.High[i]<df1.High[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.High[i]>df1.High[i-1]):
            return 0
    return 1
  

  def isEngulfing(self, l):
  
    row=l
    self.bodydiff[row] = abs(self.open[row]-self.close[row])
    if self.bodydiff[row]<0.000001:
        self.bodydiff[row]=0.000001      

    bodydiffmin = 0.002
    if (self.bodydiff[row]>bodydiffmin and self.bodydiff[row-1]>bodydiffmin and
        self.open[row-1]<self.close[row-1] and
        self.open[row]>self.close[row] and 
        (self.open[row]-self.close[row-1])>=-0e-5 and self.close[row]<self.open[row-1]): #+0e-5 -5e-5
        return 1

    elif(self.bodydiff[row]>bodydiffmin and self.bodydiff[row-1]>bodydiffmin and
        self.open[row-1]>self.close[row-1] and
        self.open[row]<self.close[row] and 
        (self.open[row]-self.close[row-1])<=+0e-5 and self.close[row]>self.open[row-1]):#-0e-5 +5e-5
        return 2
    else:
        return 0
       
  def isStar(self, l):
    bodydiffmin = 0.0020
    row=l
    self.highdiff[row] = self.high[row]-max(self.open[row],self.close[row])
    self.lowdiff[row] = min(self.open[row],self.close[row])-self.low[row]
    self.bodydiff[row] = abs(self.open[row]-self.close[row])
    if self.bodydiff[row]<0.000001:
        self.bodydiff[row]=0.000001
    self.ratio2[row] = self.lowdiff[row]/self.bodydiff[row]
    self.ratio1[row] = self.highdiff[row]/self.bodydiff[row]
    self.ratio2[row] = self.lowdiff[row]/self.bodydiff[row]

    if (self.ratio1[row]>1 and self.lowdiff[row]<0.2*self.highdiff[row] and self.bodydiff[row]>bodydiffmin):# and open[row]>close[row]):
        return 1
    elif (self.ratio2[row]>1 and self.highdiff[row]<0.2*self.lowdiff[row] and self.bodydiff[row]>bodydiffmin):# and open[row]<close[row]):
        return 2
    else:
        return 0
    
  def closeResistance(self, l,levels,lim):
    if len(levels)==0:
        return 0
    c1 = abs(self.df.High[l]-min(levels, key=lambda x:abs(x-self.df.High[l])))<=lim
    c2 = abs(max(self.df.Open[l],self.df.Close[l])-min(levels, key=lambda x:abs(x-self.df.High[l])))<=lim
    c3 = min(self.df.Open[l],self.df.Close[l])<min(levels, key=lambda x:abs(x-self.df.High[l]))
    c4 = self.df.Low[l]<min(levels, key=lambda x:abs(x-self.df.High[l]))
    if( (c1 or c2) and c3 and c4 ):
        return 1
    else:
        return 0
    
  def closeSupport(self, l,levels,lim):
    if len(levels)==0:
        return 0
    c1 = abs(self.df.Low[l]-min(levels, key=lambda x:abs(x-self.df.Low[l])))<=lim
    c2 = abs(min(self.df.Open[l],self.df.Close[l])-min(levels, key=lambda x:abs(x-self.df.Low[l])))<=lim
    c3 = max(self.df.Open[l],self.df.Close[l])>min(levels, key=lambda x:abs(x-self.df.Low[l]))
    c4 = self.df.High[l]>min(levels, key=lambda x:abs(x-self.df.Low[l]))
    if( (c1 or c2) and c3 and c4 ):
        return 1
    else:
        return 0
    

  def init(self):
    super().init()
    self.df = self.convert_to_dataframe()

    length = len(self.df)
    self.high = list(self.df['High'])
    self.low = list(self.df['Low'])
    self.close = list(self.df['Close'])
    self.open = list(self.df['Open'])
    self.bodydiff = [0] * length

    self.highdiff = [0] * length
    self.lowdiff = [0] * length
    self.ratio1 = [0] * length
    self.ratio2 = [0] * length

    n1=2

    n2=2
    backCandles=30
    signal = [0] * length

    for row in range(backCandles, len(self.df)-n2):
      ss = []
      rr = []
      for subrow in range(row-backCandles+n1, row+1):
        if self.support(self.df, subrow, n1, n2):
            ss.append(self.df.Low[subrow])
        if self.resistance(self.df, subrow, n1, n2):
            rr.append(self.df.High[subrow])

      if ((self.isEngulfing(row)==1 or self.isStar(row)==1) and self.closeResistance(row, rr, 150e-5) ):#and df.RSI[row]<30
        signal[row] = 1
      elif((self.isEngulfing(row)==2 or self.isStar(row)==2) and self.closeSupport(row, ss, 150e-5)):#and df.RSI[row]>70
        signal[row] = 2
      else:
        signal[row] = 0


    self.df["signal"] = signal
    self.df = self.df.drop('index', axis=1)
  
    # self.df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'signal']

    self.signal1 = self.I(self.SIGNAL)

  def next(self):
    super().next() 
    if self.signal1 == 2:
      self.buy()
      #TODO: use StopLoss and TakeProfit later
    elif self.signal1 == 1:
      self.position.close()