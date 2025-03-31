from MH_libraries import numpy, pandas, talib


class Indicators():
    
    def __init__(self, group):
        
        self.group = group
        self.period:int = 11
        self.Close = group['close']
        self.Open = group['open']
        self.High = group['max']
        self.Low = group['min']
        self.Vol = group['volume']
        self.To = group['to']
        self.Gator_JAW = talib.WMA(self.Close, timeperiod=11).shift(6)
        self.Gator_TEETH = talib.WMA(self.Close, timeperiod=6).shift(3)
        self.Gator_LIPS = talib.WMA(self.Close, timeperiod=3).shift(1)
        self.Gator_UPPER = abs(self.Gator_JAW - self.Gator_TEETH )
        self.Gator_LOWER = abs(self.Gator_TEETH - self.Gator_LIPS )
        self.Gator_UPPER_color = numpy.select([(self.Gator_UPPER > self.Gator_UPPER.shift(periods=1)), (self.Gator_UPPER < self.Gator_UPPER.shift(periods=1)), (self.Gator_UPPER == self.Gator_UPPER.shift(periods=1))], ['g', 'r', 'nut'], 0)
        self.Gator_LOWER_color = numpy.select([(self.Gator_LOWER > self.Gator_LOWER.shift(periods=1)), (self.Gator_LOWER < self.Gator_LOWER.shift(periods=1)), (self.Gator_LOWER == self.Gator_LOWER.shift(periods=1))], ['g', 'r', 'nut'], 0)
        self.OBV = talib.OBV(self.Close, self.Vol)
        self.VOL_CH = self.Vol.pct_change()
        self.VOL_MA = talib.SMA(self.Vol, timeperiod=self.period)
        self.SMA50 = talib.SMA(self.Close, timeperiod=self.period)
        self.SMA200 = talib.SMA(self.Close, timeperiod=self.period*3)
        self.EMA50 = talib.EMA(self.Close, timeperiod=self.period)
        self.EMA200 = talib.EMA(self.Close, timeperiod=self.period*2)
        Median = (self.High + self.Low) / 2
        self.AWO = talib.SMA(Median, timeperiod=self.period/3) - talib.SMA(Median, timeperiod=self.period)
        self.VWAP = (self.Vol * (self.High + self.Low + self.Close) / 3).cumsum() / self.Vol.cumsum()
        self.bop = talib.BOP(self.Open, self.High, self.Low, self.Close) * 100
        self.RSI = talib.RSI(self.Close, timeperiod=self.period)
        self.SAR = talib.SAR(self.High, self.Low, acceleration=0.02, maximum=0.2)
        self.ATR = talib.ATR(self.High, self.Low, self.Close, timeperiod=self.period)
        self.ADX = talib.ADX(self.High, self.Low, self.Close, timeperiod=self.period)
        self.Upper_BBand, self.Middle_BBand, self.Lower_BBand = talib.BBANDS(self.Close, timeperiod=self.period)
        self.MACD, self.MACD_signal, self.MACD_highest = talib.MACD(self.Close, fastperiod=self.period, slowperiod=self.period*2, signalperiod=9)
        self.STOCHk, self.STOCHd = talib.STOCH(self.High, self.Low, self.Close, fastk_period=self.period, slowk_period=self.period/3, slowk_matype=0, slowd_period=self.period/3, slowd_matype=0)
        self.wup = numpy.where(self.bop < 0, (talib.BOP(self.Open, self.High, self.Low, self.High) * 100), (talib.BOP(self.Close, self.High, self.Low, self.High) * 100))
        self.wlo = numpy.where(self.bop < 0, (talib.BOP(self.Low, self.High, self.Low, self.Close) * 100), (talib.BOP(self.Low, self.High, self.Low, self.Open) * 100))
        # Calculate MAD
        self.MAD = self.Close - self.SMA50
        self.MAD_color = numpy.select([(self.MAD > self.MAD.shift(periods=1)), (self.MAD < self.MAD.shift(periods=1)), (self.MAD == self.MAD.shift(periods=1))], ['g', 'r', 'nut'], 0)
        # Rainbow Oscillator Calculations
        hl2 = (self.High + self.Low) / 2
        ma_list = [talib.SMA(hl2, timeperiod=self.period)]
        for i in range(1, 10):  # 10 SMAs in total
            ma_list.append(talib.SMA(ma_list[i - 1], timeperiod=self.period))
        ma_stack = numpy.array(ma_list)  # Shape: (10, len(df))
        hh, ll = talib.MAX(hl2, 10), talib.MIN(hl2, 10)
        self.rb = 100 * (numpy.maximum.reduce(ma_stack, axis=0) - numpy.minimum.reduce(ma_stack, axis=0)) / (hh - ll)  # Highlighted Area
        self.rbo = 100 * (hl2 - numpy.mean(ma_stack, axis=0)) / (hh - ll)  # Bar (Histogram/Rect)
        
        del Median, hl2, ma_list, ma_stack, hh, ll
    
    def _single_column_color(self, values, default_color:str= 'nut'):
        
        return numpy.select([(values > values.shift(periods=1)), (values < values.shift(periods=1)), (values == values.shift(periods=1))], ['g', 'r', default_color], default_color)
    
    def _single_percentage(self, values):
        
        return numpy.clip(talib.ROC(values, timeperiod=1), -100, 100)
    
    def _douple_column_color(self, values1, values2, default_color:str= 'nut'):
        
        return numpy.select([(values1 > values2), (values1 < values2), (values1 == values2)], ['g', 'r', default_color], default_color)
    
    def _douple_percentage(self, values1, values2):
        
        return numpy.clip((((values1 - values2) / (values1 + values2)) * 100).round(1), -100, 100)
    
    def _triple_percentage(self, high_arr, middle_arr, low_arr):
        
        return (middle_arr - low_arr) / (high_arr - low_arr) * 100
    # bop - Balance of Power
    # ----------------------------------------------------
    def Balance_of_Power(self):
        """
        Calculates the Balance of Power (bop) indicator and adds it to the DataFrame.
        """        
        bop = (self.bop).round(1)
        bop_color = self._single_column_color((self.bop / 100))
        
        return {
            'bop': bop,
            'bop_color': bop_color
            }
    
    # self.RSI - Relative Strength Index
    # ----------------------------------------------------
    def Relative_Strength_Index(self):
        
        EMA_RSI = talib.EMA(self.RSI, timeperiod=self.period)
        
        rsi = self.RSI.round(1)
        rsi_color = self._single_column_color(self.RSI)
        rsi_dir = numpy.select(
            [
                (self.RSI > self.RSI.shift(1)),  # RSI breaks above the trend (simplified)
                (self.RSI < 30) & (self.RSI > EMA_RSI),  # RSI oversold and above EMA_RSI
                (self.RSI > 30) & (self.RSI.shift(1) <= 30),  # RSI moving out of oversold
                (self.RSI < 70) & (self.RSI.shift(1) >= 70),  # RSI moving out of overbought
                (self.RSI < 30) & (self.Vol > self.Vol.shift(1)),  # Volume increasing in oversold zone
                (self.RSI > 70) & (self.Vol > self.Vol.shift(1)),  # Volume increasing in overbought zone
                (self.Close < self.Close.shift(1)) & (self.RSI > self.RSI.shift(1)),  # Bullish divergence
                (self.Close > self.Close.shift(1)) & (self.RSI < self.RSI.shift(1)),  # Bearish divergence
                (self.RSI > 40) & (self.RSI < 60) & (self.RSI > self.RSI.shift(1)),  # RSI moving up in neutral zone
                (self.RSI > 40) & (self.RSI < 60) & (self.RSI < self.RSI.shift(1)),  # RSI moving down in neutral zone
                (self.RSI > 50) & (self.RSI > self.RSI.shift(1)),  # RSI confirms uptrend
                (self.RSI < 50) & (self.RSI < self.RSI.shift(1)),  # RSI confirms downtrend
                (self.RSI == 30) & (self.RSI > self.RSI.shift(1)),  # RSI bouncing from 30
                (self.RSI == 70) & (self.RSI < self.RSI.shift(1)),  # RSI reversing from 70
                (self.RSI < 30) & (self.MACD > self.MACD_signal),  # MACD crossover and RSI in oversold
                (self.RSI < 30) & (self.SAR < self.Close),  # RSI below 30 and SAR below price
                (self.RSI > 70) & (self.SAR > self.Close)  # RSI above 70 and SAR above price
            ],
            ['call', 'call', 'call', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'call', 'put'],
            default='nut'
        )
        
        del EMA_RSI
        
        return {
            'rsi': rsi, 
            'rsi_color': rsi_color,
            'rsi_dir': rsi_dir
            }
    
    # MACD - Moving Average Convergence/Divergence
    # ----------------------------------------------------
    def Moving_Average_Convergence_Divergence(self):
        
        macd = self._single_percentage(self.MACD)
        macd_signal = self._single_percentage(self.MACD_signal)
        macd_highest = self._single_percentage(self.MACD_highest)
        macd_color = self._single_column_color(self.MACD)
        macd_dir = numpy.select(
            [
                (self.MACD > self.MACD_signal) & (self.MACD.shift(1) <= self.MACD_signal.shift(1)),  # Bullish Crossover
                (self.MACD < self.MACD_signal) & (self.MACD.shift(1) >= self.MACD_signal.shift(1)),  # Bearish Crossover
                (self.MACD > 0) & (self.MACD.shift(1) <= 0),  # Bullish Zero-line Crossover
                (self.MACD < 0) & (self.MACD.shift(1) >= 0),  # Bearish Zero-line Crossover
                (self.MACD > self.MACD.shift(1)) & (self.MACD_signal > self.MACD_signal.shift(1)),  # Uptrend Confirmation
                (self.MACD < self.MACD.shift(1)) & (self.MACD_signal < self.MACD_signal.shift(1)),  # Downtrend Confirmation
                (self.MACD_highest > self.MACD_highest.shift(1)) & (self.MACD_highest > 0),  # Expanding Bullish Histogram
                (self.MACD_highest < self.MACD_highest.shift(1)) & (self.MACD_highest < 0),  # Expanding Bearish Histogram
                (self.MACD > self.MACD_signal) & (self.RSI > 50),  # self.RSI & self.MACD Bullish Confirmation
                (self.MACD < self.MACD_signal) & (self.RSI < 50),  # self.RSI & self.MACD Bearish Confirmation
                (self.MACD > self.MACD_signal) & (self.Close > self.EMA50),  # Price Above EMA & Bullish Crossover
                (self.MACD < self.MACD_signal) & (self.Close < self.EMA50),  # Price Below EMA & Bearish Crossover
                (self.MACD > self.MACD_signal) & (self.STOCHk > self.STOCHd),  # self.MACD Bullish + Stoch Bullish
                (self.MACD < self.MACD_signal) & (self.STOCHk < self.STOCHd),  # self.MACD Bearish + Stoch Bearish
                (self.MACD > self.MACD_signal) & (self.MACD > self.MACD.shift(1)),  # self.MACD Continuation Up
                (self.MACD < self.MACD_signal) & (self.MACD < self.MACD.shift(1)),  # self.MACD Continuation Down
                
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        return {
            'macd': macd.round(1), 
            'macd_signal': macd_signal.round(1), 
            'macd_highest': macd_highest.round(1), 
            'macd_color':macd_color, 
            'macd_dir':macd_dir
            }
    
    # Wicks - Upper or Lower Wicks
    # ----------------------------------------------------
    def Wicks(self):
        """
        Calculates the upper or lower wicks using the Balance of Power (bop) indicator.
        """
        wup = self.wup.round(1)
        wlo = self.wlo.round(1)
        wicks_dir = numpy.select(
            [
                (self.bop > 0) & (self.wup < 10) & (self.RSI < 30) & (self.EMA50 > self.EMA200) & (self.Vol > self.VOL_MA) & (self.bop > 0),  # Bullish Call (Long entry)
                (self.bop > 50) & (self.wup < 10),  # Strong Bullish Call (Strong trend)
                (self.bop < 0) & (self.wlo < 10) & (self.RSI > 70) & (self.EMA50 < self.EMA200) & (self.Vol > self.VOL_MA) & (self.bop > 0),  # Bearish Put (Short entry)
                (self.bop < -50) & (self.wlo < 10),  # Strong Bearish Put (Strong trend)
                (self.bop.shift(1) > 0) & (self.bop < 0) & (self.wup > 10),  # Bearish Reversal (from Call to Put)
                (self.bop.shift(1) < 0) & (self.bop > 0) & (self.wlo > 10),  # Bullish Reversal (from Put to Call)
                (self.bop > 0) & (self.Close > self.High.iloc[:-1].max()),  # Breakout Call (Breakout above resistance)
                (self.bop < 0) & (self.Close < self.Low.iloc[:-1].max()),  # Breakout Put (Breakout below support)
                (abs(self.bop) < 10) & (self.wup > 10) & (self.wlo > 10)  # Market is consolidating, no clear direction
            ],
            ['call', 'call', 'put', 'put', 'put', 'call', 'call', 'put', 'nut'],
            default='nut'
        )
        
        return {
            'wup': wup, 
            'wlo': wlo, 
            'wicks_dir': wicks_dir
            }
    
    # BBANDS - Bollinger Bands
    # ----------------------------------------------------
    def Bollinger_Bands(self):
        
        bband_2sd = talib.BBANDS(self.Close, timeperiod=self.period, nbdevup=1, nbdevdn=1, matype=0)
        bandwidth = bband_2sd[0] - bband_2sd[2]
        bandwidth_SMA = talib.SMA(bandwidth, timeperiod=self.period) * 0.5
        
        BB = self._triple_percentage(bband_2sd[0], bband_2sd[2], bband_2sd[2])
        
        # Bollinger Band Width
        bband = BB.round(1)
        bband_color = self._single_column_color(BB)
        bband_dir = numpy.select(
            [
                (self.Close <= bband_2sd[2]),  # Buy when price touches or crosses lower band (oversold)
                (self.Close >= bband_2sd[0]),  # Sell when price touches or crosses upper band (overbought)
                (self.Close > bband_2sd[0]) & (bandwidth < bandwidth_SMA),  # Breakout above upper band after squeeze
                (self.Close < bband_2sd[2]) & (bandwidth < bandwidth_SMA),  # Breakdown below lower band after squeeze
                (self.Close >= bband_2sd[0]),  # Buy when price is riding the upper band
                (self.Close <= bband_2sd[2]),  # Sell when price is riding the lower band
                (self.Close > self.Lower_BBand),  # Buy when price crosses above the lower band of the wider bands
                (self.Close < self.Upper_BBand),  # Sell when price crosses below the upper band of the wider bands
                (self.Close < bband_2sd[2]) & (self.RSI > self.RSI.shift(1)),  # Bullish Divergence (self.RSI higher low while price lower low)
                (self.Close > bband_2sd[0]) & (self.RSI < self.RSI.shift(1)),  # Bearish Divergence (self.RSI lower high while price higher high)
                (self.Close < bband_2sd[2]) & (self.MACD > self.MACD_signal),  # Buy when self.MACD crosses above signal line and price at lower band
                (self.Close > bband_2sd[0]) & (self.MACD < self.MACD_signal),  # Sell when self.MACD crosses below signal line and price at upper band
                (self.Close <= bband_2sd[2]) & (self.Vol > self.VOL_MA * 1.5),  # Buy when volume spikes at lower band
                (self.Close >= bband_2sd[0]) & (self.Vol > self.VOL_MA * 1.5),  # Sell when volume spikes at upper band
                (bandwidth > bandwidth_SMA),  # Buy when width increases (post-squeeze breakout)
                (bandwidth < bandwidth_SMA),  # Sell when width decreases (post-high volatility)
                (self.Close <= bband_2sd[2] * 0.618),  # Buy at 61.8% Fibonacci retracement near lower band
                (self.Close >= bband_2sd[0] * 0.382)  # Sell at 38.2% Fibonacci retracement near upper band
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del bband_2sd, bandwidth, bandwidth_SMA, BB
        
        return {
            'bband': bband, 
            'bband_color': bband_color,
            'bband_dir': bband_dir
            }
    
    # KELCHAN - Keltner Channels
    # ----------------------------------------------------
    def Keltner_Channels(self):
        
        """Calculate Keltner Channels using TA-Lib"""
        Upper_Keltner = self.EMA50 + (2 * self.ATR)
        Lower_Keltner = self.EMA50 - (2 * self.ATR)
        channel_width = (Upper_Keltner - Lower_Keltner) / self.EMA50
        
        KTCH = self._triple_percentage(Upper_Keltner, self.EMA50, Lower_Keltner)
        
        # Keltner Channels Width as a Percentage
        keltner = KTCH.round(1)
        keltner_color = self._single_column_color(KTCH)
        keltner_dir = numpy.select(
            [
                (self.Close >= Upper_Keltner),  # Bullish Trend (Call)
                (self.Close <= Lower_Keltner),  # Bearish Trend (Put)
                (self.Close < Lower_Keltner) & (self.RSI < 30),  # Bullish Reversal (Call)
                (self.Close > Upper_Keltner) & (self.RSI > 70),  # Bearish Reversal (Put)
                (self.Close > Upper_Keltner) & (self.MACD > self.MACD_signal),  # Breakout Buy (Call)
                (self.Close < Lower_Keltner) & (self.MACD < self.MACD_signal),  # Breakout Sell (Put)
                (channel_width < numpy.percentile(channel_width, 20)) & (self.Close > Upper_Keltner),  # Low Volatility Breakout Up (Call)
                (channel_width < numpy.percentile(channel_width, 20)) & (self.Close < Lower_Keltner),  # Low Volatility Breakout Down (Put)
                (self.Close < Lower_Keltner) & (self.RSI > numpy.roll(self.RSI, 1)),  # Bullish Divergence (Call)
                (self.Close > Upper_Keltner) & (self.RSI < numpy.roll(self.RSI, 1)),  # Bearish Divergence (Put)
                (self.Close < Lower_Keltner) & (self.MACD > self.MACD_signal),  # self.MACD Bullish Crossover (Call)
                (self.Close > Upper_Keltner) & (self.MACD < self.MACD_signal),  # self.MACD Bearish Crossover (Put)
                (self.Close < Lower_Keltner) & (self.Vol > self.VOL_MA),  # Volume Confirmed Buy (Call)
                (self.Close > Upper_Keltner) & (self.Vol > self.VOL_MA)  # Volume Confirmed Sell (Put)
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default='nut'
        )
        
        del Upper_Keltner, Lower_Keltner, channel_width, KTCH
        
        return {
            'keltner': keltner,
            'keltner_color': keltner_color,
            'keltner_dir': keltner_dir
            }
    
    # DONCHAN - Donchian Channels
    # ----------------------------------------------------
    def Donchian_Channels(self):
        
        # Donchian Channels Calculation
        upper_band = talib.MAX(self.High, timeperiod=self.period)
        lower_band = talib.MIN(self.Low, timeperiod=self.period)
        middle_band = (upper_band + lower_band) / 2
        channel_width = upper_band - lower_band
        
        DONCHAN = self._triple_percentage(upper_band, middle_band, lower_band)
        
        # Donchian Channels Width as a Percentage
        donchian = DONCHAN.round(1)
        donchian_color = self._single_column_color(DONCHAN)
        donchian_dir = numpy.select(
            [
                (self.Close > upper_band),  # Breakout Buy (Call)
                (self.Close < lower_band),  # Breakout Sell (Put)
                (self.Close >= upper_band) & (self.ADX > 25),  # Strong Uptrend (Call)
                (self.Close <= lower_band) & (self.ADX > 25),  # Strong Downtrend (Put)
                (self.Close < lower_band) & (self.RSI < 30),  # Oversold Bounce (Call)
                (self.Close > upper_band) & (self.RSI > 70),  # Overbought Rejection (Put)
                (self.Close < lower_band) & (self.RSI > numpy.roll(self.RSI, 1)),  # Bullish Divergence (Call)
                (self.Close > upper_band) & (self.RSI < numpy.roll(self.RSI, 1)),  # Bearish Divergence (Put)
                (self.Close < lower_band) & (self.MACD > self.MACD_signal),  # self.MACD Bullish Crossover (Call)
                (self.Close > upper_band) & (self.MACD < self.MACD_signal),  # self.MACD Bearish Crossover (Put)
                (self.Close < lower_band) & (self.Vol > self.VOL_MA),  # Volume Confirmed Buy (Call)
                (self.Close > upper_band) & (self.Vol > self.VOL_MA),  # Volume Confirmed Sell (Put)
                (channel_width > numpy.percentile(channel_width, 80)) & (self.Close > upper_band),  # Volatility Breakout Up (Call)
                (channel_width > numpy.percentile(channel_width, 80)) & (self.Close < lower_band),  # Volatility Breakout Down (Put)
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default='nut'
        )
        
        del upper_band, lower_band, middle_band, channel_width, DONCHAN
        
        return {
            'donchian': donchian,
            'donchian_color': donchian_color,
            'donchian_dir': donchian_dir
            }
    
    # ENVELOPE - Envelope
    # ----------------------------------------------------
    def ENVELOPE(self):
        
        """ Calculate Envelope bands. """
        middle_band = self.SMA50
        upper_band = middle_band * (1 + 2 / 100)
        lower_band = middle_band * (1 - 2 / 100)
        
        Envlp = self._triple_percentage(upper_band, middle_band, lower_band)
        
        # Envelope Width as a Percentage
        envelope = Envlp.round(1)
        envelope_color = self._single_column_color(Envlp)
        envelope_dir = numpy.select(
            [
                (self.Close > upper_band),  # Breakout above upper band
                (self.Close < lower_band),  # Breakout below lower band
                (self.Close >= upper_band),  # Riding the upper band
                (self.Close <= lower_band),  # Riding the lower band
                (self.Close <= lower_band) & (self.RSI < 30),  # Mean Reversion Buy
                (self.Close >= upper_band) & (self.RSI > 70),  # Mean Reversion Sell
                (self.Close <= lower_band) & (self.MACD > self.MACD_signal),  # self.MACD Buy
                (self.Close >= upper_band) & (self.MACD < self.MACD_signal),  # self.MACD Sell
                (self.Close <= lower_band) & (self.VOL_CH > 0.1),  # Volume Buy
                (self.Close >= upper_band) & (self.VOL_CH > 0.1)   # Volume Sell
            ],
            ['put', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del middle_band, upper_band, lower_band, Envlp
        
        return {
            'envelope': envelope,
            'envelope_color': envelope_color,
            'envelope_dir': envelope_dir
            }
    
    # SAR - Parabolic SAR
    # ----------------------------------------------------
    def Parabolic_Sar(self):
        
        para_SAR = self._single_percentage(self.SAR)
        para_SAR_color = self._single_column_color(self.SAR)
        para_SAR_dir = numpy.select(
            [
                (self.Close > self.SAR),  # Buy signal: price above SAR (bullish)
                (self.Close < self.SAR),  # Sell signal: price below SAR (bearish)
                (self.Close > self.SAR) & (self.EMA50 > self.EMA200),  # Buy signal: price above SAR and EMA crossover (bullish)
                (self.Close < self.SAR) & (self.EMA50 < self.EMA200),  # Sell signal: price below SAR and EMA crossover (bearish)
                (self.Close > self.SAR) & (self.RSI < 30),  # Buy signal: price above SAR and self.RSI < 30 (oversold)
                (self.Close < self.SAR) & (self.RSI > 70),  # Sell signal: price below SAR and self.RSI > 70 (overbought)
                (self.Close > self.SAR) & (self.MACD > self.MACD_signal),  # Buy signal: price above SAR and self.MACD above signal line
                (self.Close < self.SAR) & (self.MACD < self.MACD_signal),  # Sell signal: price below SAR and self.MACD below signal line
                (self.Close > self.SAR) & (self.Close <= self.Lower_BBand),  # Buy signal: price above SAR and touches lower Bollinger Band
                (self.Close < self.SAR) & (self.Close >= self.Upper_BBand),  # Sell signal: price below SAR and touches upper Bollinger Band
                (self.Close > self.SAR) & (self.Close >= self.Upper_BBand),  # Buy signal: price above SAR and upper band (riding the trend)
                (self.Close < self.SAR) & (self.Close <= self.Lower_BBand)  # Sell signal: price below SAR and lower band (riding the trend)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        return {
            'para_SAR': para_SAR.round(1),
            'para_SAR_color': para_SAR_color, 
            'para_SAR_dir': para_SAR_dir
            }
    
    # APO - Absolute Price Oscillator
    # ----------------------------------------------------
    def Absolute_Price_Oscillator(self):
        
        APO = talib.APO(self.Close, fastperiod=self.period, slowperiod=self.period*2, matype=0)
        
        apo = self._single_percentage(APO).round(1)
        apo_color = self._single_column_color(APO)
        apo_dir = numpy.select(
            [
                (APO > 0) & (self.RSI < 30) & (self.MACD > self.MACD_signal),
                (APO < 0) & (self.RSI > 70) & (self.MACD < self.MACD_signal),
                (APO > 0) & (self.RSI < 30) & (self.MACD > self.MACD_signal) & (self.Close > self.EMA50) & (self.EMA50 > self.EMA200),
                (APO < 0) & (self.RSI > 70) & (self.MACD < self.MACD_signal) & (self.Close < self.EMA50) & (self.EMA50 < self.EMA200),
                (APO > 0) & (self.RSI < 30) & (self.MACD > self.MACD_signal) & (self.Close > self.EMA50) & (self.Close > self.EMA200),
                (APO < 0) & (self.RSI > 70) & (self.MACD < self.MACD_signal) & (self.Close < self.EMA50) & (self.Close < self.EMA200)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del APO
        
        return {
            'apo': apo,
            'apo_color': apo_color,
            'apo_dir': apo_dir
            }
    
    # AROON - Aroon
    # ----------------------------------------------------
    def Aroon(self):
        
        AROON_dwn, AROON_up = talib.AROON(self.High, self.Low, timeperiod=self.period)
        
        aroon_up = AROON_up.round(1)
        aroon_dwn = AROON_dwn.round(1)
        aroon_color = self._douple_column_color(AROON_up, AROON_dwn)
        aroon_dir = numpy.select(
            [
                (AROON_up > AROON_dwn) & (self.MACD > self.MACD_signal),  # Buy Signal: Aroon Up crosses above Aroon Down and self.MACD crosses above Signal Line
                (AROON_dwn > AROON_up) & (self.MACD < self.MACD_signal),  # Sell Signal: Aroon Down crosses above Aroon Up and self.MACD crosses below Signal Line
                (AROON_up > 50) & (self.Close < self.Upper_BBand),  # Buy Signal: Aroon Up above 50, price below upper BB
                (AROON_dwn > 50) & (self.Close > self.Lower_BBand),  # Sell Signal: Aroon Down above 50, price above lower BB
                (self.Close < self.Close.shift(1)) & (AROON_up > AROON_up.shift(1)) & (self.RSI > self.RSI.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (AROON_dwn > AROON_dwn.shift(1)) & (self.RSI < self.RSI.shift(1)),  # Bearish Divergence
                (AROON_up > 50) & (self.Vol > self.VOL_MA),  # Buy Signal: Aroon Up above 50, Volume spike
                (AROON_dwn > 50) & (self.Vol > self.VOL_MA),  # Sell Signal: Aroon Down above 50, Volume spike
                (AROON_up > 50) & (self.STOCHk < 20) & (self.STOCHk > self.STOCHd),  # Buy Signal: Aroon Up above 50 and Stochastic Oversold
                (AROON_dwn > 50) & (self.STOCHk > 80) & (self.STOCHk < self.STOCHd)   # Sell Signal: Aroon Down above 50 and Stochastic Overbought
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del AROON_dwn, AROON_up
        
        return {
            'aroon_up': aroon_up,
            'aroon_dwn': aroon_dwn,
            'aroon_color': aroon_color,
            'aroon_dir': aroon_dir
            }
    
    # AROONOSC - Aroon Oscillator
    # ----------------------------------------------------
    def Aroon_Oscillator(self):
        
        AROON_OSC = talib.AROONOSC(self.High, self.Low, timeperiod=self.period)
        
        aroon_osc = AROON_OSC.round(1)
        aroon_osc_color = self._single_column_color(AROON_OSC)
        aroon_osc_dir = numpy.select(
            [
                (AROON_OSC > 0),  # Bullish trend
                (AROON_OSC < 0),  # Bearish trend
                (AROON_OSC > 0) & (self.RSI < 30),  # Buy when Aroon Oscillator is positive and self.RSI is oversold
                (AROON_OSC < 0) & (self.RSI > 70),  # Sell when Aroon Oscillator is negative and self.RSI is overbought
                (AROON_OSC > 0) & (self.Close > self.Upper_BBand),  # Buy Signal when Aroon Oscillator is positive and price is above upper Bollinger Band
                (AROON_OSC < 0) & (self.Close < self.Lower_BBand),  # Sell Signal when Aroon Oscillator is negative and price is below lower Bollinger Band
                (AROON_OSC > 0) & (self.MACD > self.MACD_signal),  # Buy Signal when Aroon Oscillator is positive and self.MACD crosses above signal line
                (AROON_OSC < 0) & (self.MACD < self.MACD_signal)   # Sell Signal when Aroon Oscillator is negative and self.MACD crosses below signal line
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del AROON_OSC
        
        return {
            'aroon_osc': aroon_osc,
            'aroon_osc_color': aroon_osc_color,
            'aroon_osc_dir': aroon_osc_dir
            }
    
    # CCI - Commodity Channel Index
    # ----------------------------------------------------
    def Commodity_Channel_Index(self):
        
        CCI = talib.CCI(self.High, self.Low, self.Close, timeperiod=self.period)
        
        cci = CCI.round(1)
        cci_color = self._single_column_color(CCI)
        cci_dir = numpy.select(
            [
                (CCI > 100),  # Overbought: Sell
                (CCI < -100),  # Oversold: Buy
                (CCI > 100) & (self.Close > self.SMA50),  # Strong uptrend: Buy
                (CCI < -100) & (self.Close < self.SMA50),  # Strong downtrend: Sell
                (CCI < -100) & (self.RSI < 30),  # Oversold Buy self.RSI Confirmation
                (CCI > 100) & (self.RSI > 70),  # Overbought Sell self.RSI Confirmation
                (CCI > -100) & (self.MACD > self.MACD_signal),  # Bullish self.MACD crossover
                (CCI < 100) & (self.MACD < self.MACD_signal),  # Bearish self.MACD crossover
                (CCI > 100) & (self.Close > self.Upper_BBand),  # Buy Bollinger Bands Breakout
                (CCI < -100) & (self.Close < self.Lower_BBand),  # Sell Bollinger Bands Breakout
                (CCI > 100) & (self.VOL_CH > 0.1),  # Strong buy confirmation
                (CCI < -100) & (self.VOL_CH > 0.1),  # Strong sell confirmation
                (CCI > 100) & (self.Close > self.SAR),  # Bullish Trend Buy
                (CCI < -100) & (self.Close < self.SAR)  # Bearish Trend Sell
            ],
            ['put', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del CCI
        
        return {
            'cci': cci, 
            'cci_color': cci_color, 
            'cci_dir': cci_dir
            }
    
    # CHANDE_MOMENTUM_OSCILLATOR - Chande Momentum Oscillator
    # ----------------------------------------------------
    def Chande_Momentum_Oscillator(self):
        
        CMO = talib.CMO(self.Close, timeperiod=self.period)
        
        cmo = CMO.round(1)
        cmo_color = self._single_column_color(CMO)
        cmo_dir = numpy.select(
            [
                (CMO > 50),  # Overbought: Sell
                (CMO < -50),  # Oversold: Buy
                (CMO > 50) & (self.Close > self.SMA50),  # Strong uptrend: Buy
                (CMO < -50) & (self.Close < self.SMA50),  # Strong downtrend: Sell
                (CMO < -50) & (self.RSI < 30),  # Oversold Buy
                (CMO > 50) & (self.RSI > 70),  # Overbought Sell
                (CMO > -50) & (self.MACD > self.MACD_signal),  # Bullish self.MACD crossover
                (CMO < 50) & (self.MACD < self.MACD_signal),  # Bearish self.MACD crossover
                (CMO > 50) & (self.Close > self.Upper_BBand),  # Buy Bollinger Bands Breakout
                (CMO < -50) & (self.Close < self.Lower_BBand),  # Sell Bollinger Bands Breakout
                (CMO > 50) & (self.VOL_CH > 0.1),  # Strong buy confirmation
                (CMO < -50) & (self.VOL_CH > 0.1),  # Strong sell confirmation
                (CMO > 50) & (self.Close > self.SAR),  # Bullish Trend Buy
                (CMO < -50) & (self.Close < self.SAR)  # Bearish Trend Sell
            ],
            ['put', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del CMO
        
        return {
            'cmo': cmo, 
            'cmo_color': cmo_color,
            'cmo_dir': cmo_dir
            }
    
    # MOM - Momentum
    # ----------------------------------------------------
    def Momentum(self):
        
        MOM = talib.MOM(self.Close, timeperiod=self.period)
        
        mom_shift = MOM - MOM.shift(1)
        price_shift = self.Close - self.Close.shift(1)
        EMA_MOM = talib.EMA(MOM, timeperiod=self.period)
        
        mom = self._single_percentage(MOM)
        mom_color = self._single_column_color(MOM)
        mom_dir = numpy.select(
            [
                (MOM > 0),  # Momentum Breakout (Bullish)
                (MOM < 0),  # Momentum Breakout (Bearish)
                (price_shift > 0) & (mom_shift > 0),  # Momentum Trend Confirmation (Bullish)
                (price_shift < 0) & (mom_shift < 0),  # Momentum Trend Confirmation (Bearish)
                (MOM < 0) & (mom_shift > 0),  # Momentum Reversal (Bullish)
                (MOM > 0) & (mom_shift < 0),  # Momentum Reversal (Bearish)
                (self.Close > self.SMA50) & (MOM > 0),  # Momentum + Moving Average (Bullish)
                (self.Close < self.SMA50) & (MOM < 0),  # Momentum + Moving Average (Bearish)
                (MOM > 0) & (MOM > EMA_MOM),  # Momentum EMA Confirmation (Bullish)
                (MOM < 0) & (MOM < EMA_MOM),  # Momentum EMA Confirmation (Bearish)
                (MOM > 0) & (self.RSI < 70),  # Momentum + self.RSI (Bullish)
                (MOM < 0) & (self.RSI > 30),  # Momentum + self.RSI (Bearish)
                (MOM > 0) & (self.MACD > 0),  # Momentum + self.MACD (Bullish)
                (MOM < 0) & (self.MACD < 0),  # Momentum + self.MACD (Bearish)
                (MOM > 0) & (self.Close > self.Close.shift(self.period)),  # Momentum Higher High (Bullish)
                (MOM < 0) & (self.Close < self.Close.shift(self.period))  # Momentum Lower Low (Bearish)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del MOM, mom_shift, price_shift, EMA_MOM
        
        return {
            'mom': mom.round(1), 
            'mom_color': mom_color, 
            'mom_dir': mom_dir
            }
    
    # ADX - Average Directional Movement Index
    # ----------------------------------------------------
    def Average_Directional_Movement_Index(self):
        
        ADXR = talib.ADXR(self.High, self.Low, self.Close, timeperiod=self.period)
        PLUS_DI = talib.PLUS_DI(self.High, self.Low, self.Close, timeperiod=self.period)
        MINUS_DI = talib.MINUS_DI(self.High, self.Low, self.Close, timeperiod=self.period)
        ADX_per = ((self.ADX / (PLUS_DI + MINUS_DI)) * 100)
        
        # Support & Resistance (Rolling High/Low)
        resistance = self.High.shift(1).rolling(window=self.period).max()
        support = self.Low.shift(1).rolling(window=self.period).min()
        
        adx = self.ADX.round(1)
        adx_per = ADX_per.round(1)
        adxr = ADXR.round(1)
        adxr_color = self._single_column_color(ADXR)
        plus_di = PLUS_DI.round(1)
        minus_di = MINUS_DI.round(1)
        di_color = self._douple_column_color(PLUS_DI, MINUS_DI)
        adx_dir = numpy.select(
            [
                (PLUS_DI > MINUS_DI) & (PLUS_DI.shift(1) < MINUS_DI.shift(1)),  # bullish_crossover
                (MINUS_DI > PLUS_DI) & (MINUS_DI.shift(1) < PLUS_DI.shift(1)),  # bearish_crossover
                (PLUS_DI > MINUS_DI) & (self.ADX > 25),    # bullish_confirmation
                (MINUS_DI > PLUS_DI) & (self.ADX > 25),    # bearish_confirmation
                (self.ADX > 25) & (self.ADX.shift(1) < 25), # ADX_breakout
                (self.ADX > self.ADX.shift(1)) & (self.Close > self.Close.shift(1)),    # bullish_trend_strength
                (self.ADX > self.ADX.shift(1)) & (self.Close < self.Close.shift(1)),    # bearish_trend_strength
                (PLUS_DI > MINUS_DI) & (PLUS_DI.shift(1) < MINUS_DI.shift(1)) & (self.ADX < self.ADX.shift(1)),   # bullish_fakeout
                (MINUS_DI > PLUS_DI) & (MINUS_DI.shift(1) < PLUS_DI.shift(1)) & (self.ADX < self.ADX.shift(1)),   # bearish_fakeout
                (self.Close > self.Close.shift(1)) & (self.ADX < self.ADX.shift(1)),    # bullish_divergence
                (self.Close < self.Close.shift(1)) & (self.ADX < self.ADX.shift(1)),    # bearish_divergence
                (PLUS_DI > MINUS_DI) & (self.ADX > 25) & (self.Close < self.Close.shift(1)),    # bullish_pullback
                (MINUS_DI > PLUS_DI) & (self.ADX > 25) & (self.Close > self.Close.shift(1)),    # bearish_pullback
                (self.ADX > 25) & (self.Close > self.SMA50) & (self.SMA50 > self.SMA200),  # bullish_sma_confirmation
                (self.ADX > 25) & (self.Close < self.SMA50) & (self.SMA50 < self.SMA200),  # bearish_sma_confirmation
                (PLUS_DI > MINUS_DI) & (self.ADX > 25) & (self.RSI < 30),  # bullish_self.RSI_confirmation
                (MINUS_DI > PLUS_DI) & (self.ADX > 25) & (self.RSI > 70)   # bearish_self.RSI_confirmation
            ],
            ['call', 'put', 'call', 'put', 'call', 'call', 'put', 'put', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        adxr_dir = numpy.select(
            [
                (ADXR > ADXR.shift(1)) & (self.ADX > 25),    # bullish_momentum
                (ADXR < ADXR.shift(1)) & (self.ADX < 25),    # bearish_momentum
                (ADXR > 25) & (self.Close > resistance),     # bullish_breakout
                (ADXR < 20) & (self.Close < support),        # bearish_breakout
                (ADXR > 25) & (self.RSI < 30),              # bullish_RSI
                (ADXR < 20) & (self.RSI > 70),              # bearish_RSI
                (ADXR > 25) & (self.MACD > self.MACD_signal), # bullish_MACD
                (ADXR < 20) & (self.MACD < self.MACD_signal), # bearish_MACD
                (ADXR > 40) & (ADXR < ADXR.shift(1)),        # bullish_exhaustion
                (ADXR < 10) & (ADXR > ADXR.shift(1)),        # bearish_exhaustion
                (ADXR > 25) & (self.Close > self.Upper_BBand), # bullish_bb_breakout
                (ADXR < 20) & (self.Close < self.Lower_BBand)  # bearish_bb_breakout
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del  ADXR, PLUS_DI, MINUS_DI, resistance, support
        
        return {
            'adx': adx, 
            'adx_per': adx_per,
            'plus_di': plus_di,
            'minus_di': minus_di, 
            'di_color': di_color,
            'adx_dir': adx_dir,
            'adxr': adxr, 
            'adxr_color':adxr_color, 
            'adxr_dir': adxr_dir
            }
    
    # DX - Directional Movement Index
    # ----------------------------------------------------
    def Directional_Movement_Index(self):
        
        DX = talib.DX(self.High, self.Low, self.Close, timeperiod=self.period)
        
        dx = DX.round(1)
        dx_color = self._single_column_color(DX)
        dx_dir = numpy.select([(DX >= 25), (DX < 20), ((DX < 25) & (DX >= 20))], ['Strong', 'weak', 'nut'], 0)
        
        del DX
        
        return {
            'dx': dx, 
            'dx_color': dx_color,
            'dx_dir': dx_dir
            }
    
    # DM - Directional Movement
    # ----------------------------------------------------
    def DIrectional_Movement(self):
        
        PLUS_DM = talib.PLUS_DM(self.High, self.Low, timeperiod=self.period)
        MINUS_DM = talib.MINUS_DM(self.High, self.Low, timeperiod=self.period)
        DM_per = self._douple_percentage(PLUS_DM, MINUS_DM)
        
        dm = DM_per
        dm_color = self._douple_column_color(PLUS_DM, MINUS_DM)
        dm_dir = numpy.select([(DM_per >= 10), (DM_per <= -10), ((DM_per < 10) & (DM_per > -10))], ['call', 'put', 'nut'], 0)
        
        del PLUS_DM, MINUS_DM, DM_per
        
        return {
            'dm': dm, 
            'dm_color': dm_color,
            'dm_dir': dm_dir
            }
    
    # PPO - Percentage Price Oscillator
    # ----------------------------------------------------
    def Percentage_Price_Oscillator(self):
        
        PPO = talib.PPO(self.Close, fastperiod=self.period, slowperiod=self.period * 2, matype=0)
        Signal = talib.EMA(PPO, timeperiod=self.period)
        
        ppo = self._single_percentage(PPO)
        ppo_color = self._single_column_color(PPO)
        ppo_dir = numpy.select(
            [
                (PPO < -5),  # Buy signal: PPO below -5% (oversold condition)
                (PPO > 5),  # Sell signal: PPO above +5% (overbought condition)
                (PPO > Signal) & (PPO.shift(1) <= Signal.shift(1)),  # Buy signal: PPO crosses above the signal line
                (PPO < Signal) & (PPO.shift(1) >= Signal.shift(1)),  # Sell signal: PPO crosses below the signal line
                (PPO > PPO.shift(1)) & (self.Close < self.Close.shift(1)),  # Bullish divergence
                (PPO < PPO.shift(1)) & (self.Close > self.Close.shift(1))  # Bearish divergence
            ],
            ['call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del PPO, Signal
        
        return {
            'ppo': ppo.round(1),
            'ppo_color': ppo_color, 
            'ppo_dir': ppo_dir
            }
    
    # STOCHF - Stochastic Fast
    # ----------------------------------------------------
    def Stochastic_Fast(self):
        
        STOCHF_fastk, STOCHF_fastd = talib.STOCHF(self.High, self.Low, self.Close, fastk_period=self.period, fastd_period=self.period / 3, fastd_matype=0)
        
        stochf_k = STOCHF_fastk.round(1)
        stochf_d = STOCHF_fastd.round(1)
        stochf_k_color = self._single_column_color(STOCHF_fastk)
        stochf_d_color = self._single_column_color(STOCHF_fastd)
        stochf_dir = numpy.select(
            [
                (STOCHF_fastk > STOCHF_fastd) & (STOCHF_fastk.shift(1) < STOCHF_fastd.shift(1)) & (STOCHF_fastk > 80),   # Stochastic Crossover - Buy
                (STOCHF_fastk < STOCHF_fastd) & (STOCHF_fastk.shift(1) > STOCHF_fastd.shift(1)) & (STOCHF_fastk < 20),  # Stochastic Crossover - Sell
                (self.Close > self.Close.shift(1)) & (STOCHF_fastk < STOCHF_fastk.shift(1)),   # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (STOCHF_fastk > STOCHF_fastk.shift(1)),   # Bearish Divergence
                (STOCHF_fastk > STOCHF_fastd) & (STOCHF_fastk.shift(1) < STOCHF_fastd.shift(1)) & (self.MACD > self.MACD_signal),   # self.MACD + Stochastic Buy
                (STOCHF_fastk < STOCHF_fastd) & (STOCHF_fastk.shift(1) > STOCHF_fastd.shift(1)) & (self.MACD < self.MACD_signal),  # self.MACD + Stochastic Sell
                (STOCHF_fastk < 20) & (self.RSI < 30) & (self.RSI.shift(1) > 30),  # self.RSI + Stochastic Buy
                (STOCHF_fastk > 80) & (self.RSI > 70) & (self.RSI.shift(1) < 70),  # self.RSI + Stochastic Sell
                (STOCHF_fastk > 50),  # Trend Following Up
                (STOCHF_fastk < 50)   # Trend Following Down
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del STOCHF_fastk, STOCHF_fastd
        
        return {
            'stochf_k': stochf_k, 
            'stochf_d': stochf_d, 
            'stochf_k_color': stochf_k_color,
            'stochf_d_color': stochf_d_color, 
            'stochf_dir': stochf_dir
            }
    
    # STOCHS - Stochastic Slow
    # ----------------------------------------------------
    def Stochastic_Slow(self):
        
        STOCHS_slowk, STOCHS_slowd = talib.STOCH(self.High, self.Low, self.Close, fastk_period=self.period, slowk_period=self.period /3, slowk_matype=0, slowd_period=self.period / 3, slowd_matype=0)
        
        stochs_k = STOCHS_slowk.round(1)
        stochs_d = STOCHS_slowd.round(1)
        stochs_k_color = self._single_column_color(STOCHS_slowk)
        stochs_d_color = self._single_column_color(STOCHS_slowd)
        stochs_dir = numpy.select(
            [
                (STOCHS_slowk > STOCHS_slowd) & (STOCHS_slowk.shift(1) < STOCHS_slowd.shift(1)) & (STOCHS_slowk > 80),   # Stochastic Crossover - Buy
                (STOCHS_slowk < STOCHS_slowd) & (STOCHS_slowk.shift(1) > STOCHS_slowd.shift(1)) & (STOCHS_slowk < 20),  # Stochastic Crossover - Sell
                (self.Close > self.Close.shift(1)) & (STOCHS_slowk < STOCHS_slowk.shift(1)),   # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (STOCHS_slowk > STOCHS_slowk.shift(1)),   # Bearish Divergence
                (STOCHS_slowk > STOCHS_slowd) & (STOCHS_slowk.shift(1) < STOCHS_slowd.shift(1)) & (self.MACD > self.MACD_signal),   # self.MACD + Stochastic Buy
                (STOCHS_slowk < STOCHS_slowd) & (STOCHS_slowk.shift(1) > STOCHS_slowd.shift(1)) & (self.MACD < self.MACD_signal),  # self.MACD + Stochastic Sell
                (STOCHS_slowk < 20) & (self.RSI < 30) & (self.RSI.shift(1) > 30),  # self.RSI + Stochastic Buy
                (STOCHS_slowk > 80) & (self.RSI > 70) & (self.RSI.shift(1) < 70),  # self.RSI + Stochastic Sell
                (STOCHS_slowk > 50),  # Trend Following Up
                (STOCHS_slowk < 50)   # Trend Following Down
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del STOCHS_slowk, STOCHS_slowd
        
        return {
            'stochs_k': stochs_k, 
            'stochs_d': stochs_d, 
            'stochs_k_color': stochs_k_color,
            'stochs_d_color': stochs_d_color, 
            'stochs_dir': stochs_dir
            }
    
    # STOCHself.RSI - Stochastic Relative Strength Index
    # ----------------------------------------------------
    def Stochastic_Relative_Strength_Index(self):
        
        STOCHRSI_k, STOCHRSI_d = talib.STOCHRSI(self.Close, timeperiod=self.period, fastk_period=self.period, fastd_period=self.period / 3, fastd_matype=0)
        
        stochrsi_k = STOCHRSI_k.round(1)
        stochrsi_d = STOCHRSI_d.round(1)
        stochrsi_k_color = self._single_column_color(STOCHRSI_k)
        stochrsi_d_color = self._single_column_color(STOCHRSI_d)
        stochrsi_dir = numpy.select(
            [
                (STOCHRSI_k > STOCHRSI_d) & (STOCHRSI_k.shift(1) < STOCHRSI_d.shift(1)) & (STOCHRSI_k > 80),   # Stochastic Crossover - Buy
                (STOCHRSI_k < STOCHRSI_d) & (STOCHRSI_k.shift(1) > STOCHRSI_d.shift(1)) & (STOCHRSI_k < 20),  # Stochastic Crossover - Sell
                (self.Close > self.Close.shift(1)) & (STOCHRSI_k < STOCHRSI_k.shift(1)),   # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (STOCHRSI_k > STOCHRSI_k.shift(1)),   # Bearish Divergence
                (STOCHRSI_k > STOCHRSI_d) & (STOCHRSI_k.shift(1) < STOCHRSI_d.shift(1)) & (self.MACD > self.MACD_signal),   # self.MACD + Stochastic Buy
                (STOCHRSI_k < STOCHRSI_d) & (STOCHRSI_k.shift(1) > STOCHRSI_d.shift(1)) & (self.MACD < self.MACD_signal),  # self.MACD + Stochastic Sell
                (STOCHRSI_k < 20) & (self.RSI < 30) & (self.RSI.shift(1) > 30),  # self.RSI + Stochastic Buy
                (STOCHRSI_k > 80) & (self.RSI > 70) & (self.RSI.shift(1) < 70),  # self.RSI + Stochastic Sell
                (STOCHRSI_k > 50),  # Trend Following Up
                (STOCHRSI_k < 50)   # Trend Following Down
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del STOCHRSI_k, STOCHRSI_d
        
        return {
            'stochrsi_k': stochrsi_k, 
            'stochrsi_d': stochrsi_d, 
            'stochrsi_k_color': stochrsi_k_color,
            'stochrsi_d_color': stochrsi_d_color, 
            'stochrsi_dir': stochrsi_dir
            }
    
    # ULTOSC - Ultimate Oscillator
    # ----------------------------------------------------
    def Ultimate_Oscillator(self):
        
        ULTOSC = talib.ULTOSC(self.High, self.Low, self.Close, timeperiod1=self.period, timeperiod2=self.period * 2, timeperiod3=self.period * 2.5)
        
        ultosc = ULTOSC.round(1)
        ultosc_color = self._single_column_color(ULTOSC)
        ultosc_dir = numpy.select(
            [
                (ULTOSC < 30) & (ULTOSC.shift(1) < 30),  # Oversold Buy
                (ULTOSC > 70) & (ULTOSC.shift(1) > 70),  # Overbought Sell
                (self.Close > self.Close.shift(1)) & (ULTOSC < ULTOSC.shift(1)),  # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (ULTOSC > ULTOSC.shift(1)),  # Bearish Divergence
                (ULTOSC > 50) & (self.Close > self.Close.shift(1)),  # Breakout Up
                (ULTOSC < 50) & (self.Close < self.Close.shift(1)),  # Breakout Down
                (ULTOSC > 50),  # Trend Confirmation Up
                (ULTOSC < 50),  # Trend Confirmation Down
                (ULTOSC > 50) & (self.MACD > self.MACD_signal),  # ULTOSC + self.MACD Buy
                (ULTOSC < 50) & (self.MACD < self.MACD_signal),  # ULTOSC + self.MACD Sell
                (ULTOSC > 50) & (self.Close > self.SMA50),  # ULTOSC + MA Buy
                (ULTOSC < 50) & (self.Close < self.SMA50)   # ULTOSC + MA Sell
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del ULTOSC
        
        return {
            'ultosc': ultosc, 
            'ultosc_color': ultosc_color, 
            'ultosc_dir': ultosc_dir
            }
    
    # WILLR - Williams' %R
    # ----------------------------------------------------
    def Williams_R(self):
        
        WILLR = talib.WILLR(self.High, self.Low, self.Close, timeperiod=self.period)
        
        willr = WILLR.round(1)
        willr_color = self._single_column_color(WILLR)
        willr_dir = numpy.select(
            [
                (WILLR < -80) & (WILLR.shift(1) < -80),  # Oversold Buy
                (WILLR > -20) & (WILLR.shift(1) > -20),  # Overbought Sell
                (self.Close > self.Close.shift(1)) & (WILLR < WILLR.shift(1)),  # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (WILLR > WILLR.shift(1)),  # Bearish Divergence
                (WILLR > -50) & (self.Close > self.Close.shift(1)),  # Breakout Up
                (WILLR < -50) & (self.Close < self.Close.shift(1)),  # Breakout Down
                (WILLR > -50),  # Trend Confirmation Up
                (WILLR < -50),  # Trend Confirmation Down
                (WILLR < -80) & (self.MACD > self.MACD_signal),  # Williams %R + self.MACD Buy
                (WILLR > -20) & (self.MACD < self.MACD_signal),  # Williams %R + self.MACD Sell
                (WILLR > -50) & (self.Close > self.SMA50),  # Williams %R + MA Buy
                (WILLR < -50) & (self.Close < self.SMA50)   # Williams %R + MA Sell
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del WILLR
        
        return  {
            'willr': willr, 
            'willr_color': willr_color, 
            'willr_dir': willr_dir
            }
    
    # MFI - Money Flow Index
    # ----------------------------------------------------
    def Money_Flow_Index(self):
        
        MFI = talib.MFI(self.High, self.Low, self.Close, self.Vol, timeperiod=self.period)
        
        mfi = MFI.round(1)
        mfi_color = self._single_column_color(MFI)
        mfi_dir = numpy.select(
            [
                (MFI < 20) & (MFI.shift(1) < 20),  # Oversold Buy
                (MFI > 80) & (MFI.shift(1) > 80),  # Overbought Sell
                (self.Close > self.Close.shift(1)) & (MFI < MFI.shift(1)),  # Bullish Divergence
                (self.Close < self.Close.shift(1)) & (MFI > MFI.shift(1)),  # Bearish Divergence
                (MFI > 50) & (self.Close > self.Close.shift(1)),  # Breakout Up
                (MFI < 50) & (self.Close < self.Close.shift(1)),  # Breakout Down
                (MFI < 20) & (self.MACD > self.MACD_signal),  # MFI + self.MACD Buy
                (MFI > 80) & (self.MACD < self.MACD_signal),  # MFI + self.MACD Sell
                (MFI < 30) & (self.RSI < 30),  # MFI + self.RSI Buy
                (MFI > 70) & (self.RSI > 70),  # MFI + self.RSI Sell
                (MFI > 50) & (self.Close > self.SMA50),  # MFI + MA Buy
                (MFI < 50) & (self.Close < self.SMA50)   # MFI + MA Sell
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del MFI
        
        return {
            'mfi': mfi, 
            'mfi_color': mfi_color, 
            'mfi_dir': mfi_dir
            }
    
    # AD - Chaikin A/D Line
    # ----------------------------------------------------
    def Chaikin_AD_Line(self):
        
        AD = talib.AD(self.High, self.Low, self.Close, self.Vol)
        AD_Per = self._single_percentage(AD)
        
        ad = AD_Per
        ad_color = self._single_column_color(AD)
        ad_dir = numpy.select(
            [
                (AD > AD.shift(1)),  # Trend Confirmation Up
                (AD < AD.shift(1)),  # Trend Confirmation Down
                (AD < self.Lower_BBand),  # Bollinger Band Lower Buy
                (AD > self.Upper_BBand),  # Bollinger Band Upper Sell
                (AD > AD.shift(1)) & (self.RSI > 50),  # self.RSI Confirmation Buy
                (AD < AD.shift(1)) & (self.RSI < 50),  # self.RSI Confirmation Sell
                (AD > AD.shift(1)) & (self.MACD > self.MACD_signal),  # self.MACD Crossover Buy
                (AD < AD.shift(1)) & (self.MACD < self.MACD_signal),  # self.MACD Crossover Sell
                (AD > AD.shift(1)) & (self.STOCHk > self.STOCHd) & (self.STOCHk < 20),  # Stochastic Buy
                (AD < AD.shift(1)) & (self.STOCHk < self.STOCHd) & (self.STOCHk > 80)  # Stochastic Sell
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del AD, AD_Per
        
        return {
            'ad': ad.round(1), 
            'ad_color': ad_color, 
            'ad_dir': ad_dir
            }
    
    # ADOSC - Chaikin A/D Oscillator
    # ----------------------------------------------------
    def Chaikin_AD_Oscillator(self):
        
        ADOSC = talib.ADOSC(self.High, self.Low, self.Close, self.Vol, fastperiod=self.period / 3, slowperiod=self.period)
        
        adosc = ADOSC.round(1)
        adosc_color = self._single_column_color(ADOSC)
        adosc_dir = numpy.select(
            [
                (ADOSC.shift(periods=1) < 0) & (ADOSC > 0),  # ADOSC crosses above zero (buy signal)
                (ADOSC.shift(periods=1) > 0) & (ADOSC < 0),  # ADOSC crosses above zero (sell signal)
                (self.Close < self.Close.shift(periods=1)) & (ADOSC > ADOSC.shift(periods=1)),  # Bullish Divergence self.Close
                (self.Close > self.Close.shift(periods=1)) & (ADOSC < ADOSC.shift(periods=1)),  # Bearish Divergence self.Close
                (self.Low < self.Low.shift(periods=1)) & (ADOSC > ADOSC.shift(periods=1)),  # Bullish Divergence low
                (self.High > self.High.shift(periods=1)) & (ADOSC < ADOSC.shift(periods=1)),  # Bearish Divergence high
                (ADOSC.shift(periods=1) < 0) & (ADOSC > 0) & (self.Close > self.SMA50),  # Bullish crossover above MA50
                (ADOSC.shift(periods=1) > 0) & (ADOSC < 0) & (self.Close < self.SMA50),  # Bearish crossover below MA50
                (ADOSC.shift(periods=1) < 0) & (ADOSC > 0) & (self.MACD > self.MACD_signal),  # Strong bullish signal
                (ADOSC.shift(periods=1) > 0) & (ADOSC < 0) & (self.MACD < self.MACD_signal),  # Strong bearish signal
                (ADOSC > 0) & (self.RSI < 30),  # Buy if A/D % is rising & self.RSI oversold
                (ADOSC < 0) & (self.RSI > 70)  # Sell if A/D % is falling & self.RSI overbought
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del ADOSC
        
        return {
            'adosc': adosc, 
            'adosc_color': adosc_color, 
            'adosc_dir': adosc_dir
            }
    
    # OBV - On Balance Volume
    # ----------------------------------------------------
    def On_Balance_Volume(self):
        
        OBV_High = self.OBV.rolling(window=self.period).max()
        OBV_Low = self.OBV.rolling(window=self.period).min()
        
        obv = self._single_percentage(self.OBV)
        obv_color = self._single_column_color(self.OBV)
        obv_dir = numpy.select(
            [
                (self.Close > self.Close.shift(periods=1)) & (self.OBV > self.OBV.shift(periods=1)),  # OBV Breakout Confirmation (Buy)
                (self.Close < self.Close.shift(periods=1)) & (self.OBV < self.OBV.shift(periods=1)),  # OBV Breakout Confirmation (Sell)
                (self.OBV > self.SMA50),  # OBV MA Crossover (Buy)
                (self.OBV < self.SMA50),  # OBV MA Crossover (Sell)
                (self.OBV > self.OBV.shift(1)) & (self.RSI < 30),  # OBV + self.RSI Bullish Confirmation (Buy)
                (self.OBV < self.OBV.shift(1)) & (self.RSI > 70),  # OBV + self.RSI Bearish Confirmation (Sell)
                (self.Low < self.Low.shift(periods=1)) & (self.OBV > self.OBV.shift(periods=1)),  # Bullish Divergence (Buy)
                (self.High > self.High.shift(periods=1)) & (self.OBV < self.OBV.shift(periods=1)),  # Bearish Divergence (Sell)
                (self.OBV.shift(1) < 0) & (self.OBV > 0) & (self.MACD > self.MACD_signal),  # OBV + self.MACD Bullish (Buy)
                (self.OBV.shift(1) > 0) & (self.OBV < 0) & (self.MACD < self.MACD_signal),  # OBV + self.MACD Bearish (Sell)
                (self.OBV > OBV_High.shift(1)),  # OBV Support/Resistance Breakout (Buy)
                (self.OBV < OBV_Low.shift(1))    # OBV Support/Resistance Breakdown (Sell)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del OBV_High, OBV_Low
        
        return {
            'obv': obv.round(1), 
            'obv_color': obv_color, 
            'obv_dir': obv_dir
            }
    
    # HT_DCPERIOD - Hilbert Transform - Dominant Cycle Period
    # ----------------------------------------------------
    def Dominant_Cycle_Period(self):
        
        DCPERIOD = talib.HT_DCPERIOD(self.Close)
        Long_MA = talib.SMA(self.Close, timeperiod=DCPERIOD.max().astype(int))
        
        dcperiod = DCPERIOD.round(1)
        dcperiod_per = self._single_percentage(DCPERIOD)
        dcperiod_color = self._single_column_color(DCPERIOD)
        dcperiod_dir = numpy.select(
            [
                (DCPERIOD > DCPERIOD.shift(1)),  # Trend Increasing
                (DCPERIOD < DCPERIOD.shift(1)),  # Trend Decreasing
                (self.SMA50 > Long_MA),  # Adaptive MA Crossover Buy
                (self.SMA50 < Long_MA),  # Adaptive MA Crossover Sell
                (self.ATR > self.ATR.shift(1)) & (DCPERIOD > DCPERIOD.shift(1)),  # Volatility Expansion Buy
                (self.ATR > self.ATR.shift(1)) & (DCPERIOD < DCPERIOD.shift(1)),  # Volatility Expansion Sell
                (self.MACD > self.MACD_signal) & (DCPERIOD > DCPERIOD.shift(1)),  # self.MACD Buy
                (self.MACD < self.MACD_signal) & (DCPERIOD < DCPERIOD.shift(1)),  # self.MACD Sell
                ((DCPERIOD - DCPERIOD.shift(1)) > 3),  # Sudden Cycle Shift Buy
                ((DCPERIOD.shift(1) - DCPERIOD) > 3),  # Sudden Cycle Shift Sell
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del DCPERIOD, Long_MA
        
        return {
            'dcperiod': dcperiod,
            'dcperiod_per': dcperiod_per.round(1),
            'dcperiod_color': dcperiod_color,
            'dcperiod_dir': dcperiod_dir
            }
    
    # HT_DCPHASE - Hilbert Transform - Dominant Cycle Phase
    # ----------------------------------------------------
    def Dominant_Cycle_Phase(self):
        
        DCPHASE = talib.HT_DCPHASE(self.Close)
        
        dcphase = DCPHASE.round(1)
        dcphase_per = self._single_percentage(DCPHASE)
        dcphase_color = self._single_column_color(DCPHASE)
        dcphase_dir = numpy.select(
            [
                (DCPHASE.shift(1) > 180) & (DCPHASE <= 0),   # Cycle Reset (Buy)
                (DCPHASE.shift(1) < 180) & (DCPHASE >= 180), # Mid-Cycle (Sell)
                (DCPHASE.shift(1) > 180) & (DCPHASE <= 0) & (self.RSI < 30),   # Buy (HT_DCPHASE + self.RSI)
                (DCPHASE.shift(1) < 180) & (DCPHASE >= 180) & (self.RSI > 70), # Sell (HT_DCPHASE + self.RSI)
                (DCPHASE.shift(1) > 180) & (DCPHASE <= 0) & (self.MACD > self.MACD_signal),   # Buy (HT_DCPHASE + self.MACD)
                (DCPHASE.shift(1) < 180) & (DCPHASE >= 180) & (self.MACD < self.MACD_signal), # Sell (HT_DCPHASE + self.MACD)
                (DCPHASE.shift(1) > 180) & (DCPHASE <= 0) & (self.ADX > 25),   # Buy (HT_DCPHASE + ADX)
                (DCPHASE.shift(1) < 180) & (DCPHASE >= 180) & (self.ADX > 25), # Sell (HT_DCPHASE + ADX)
                (DCPHASE.shift(1) > 180) & (DCPHASE <= 0) & (self.Close < self.Lower_BBand),  # Buy (HT_DCPHASE + Bollinger Bands)
                (DCPHASE.shift(1) < 180) & (DCPHASE >= 180) & (self.Close > self.Upper_BBand) # Sell (HT_DCPHASE + Bollinger Bands)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del DCPHASE
        
        return {
            'dcphase': dcphase,
            'dcphase_per': dcphase_per.round(1),
            'dcphase_color': dcphase_color,
            'dcphase_dir': dcphase_dir
            }
    
    # HT_TRENDMODE - Hilbert Transform - Trend vs Cycle Mode
    # ----------------------------------------------------
    def Trend_Cycle_Mode(self):
        
        TRENDMODE = talib.HT_TRENDMODE(self.Close)
        
        CMF = (2 * self.Close - self.High - self.Low) / (self.High - self.Low) * self.Vol
        CMF = CMF.rolling(self.period).sum() / self.Vol.rolling(self.period).sum()
        
        trendmode = TRENDMODE
        trendmode_dir = numpy.select(
            [
                (TRENDMODE == 1) & (self.Close > self.SMA50),  # Trend + Price Above MA (BUY)
                (TRENDMODE == 1) & (self.Close < self.SMA50),  # Trend + Price Below MA (SELL)
                (TRENDMODE == 0) & (self.Close < self.SMA50) & (self.Close < self.Close.shift(1)),  # Cycle + Price Falling (BUY)
                (TRENDMODE == 0) & (self.Close > self.SMA50) & (self.Close > self.Close.shift(1)),  # Cycle + Price Rising (SELL)
                (TRENDMODE == 1) & (self.Close > self.SMA50) & (self.ADX > 25),  # Trend + MA + ADX (BUY)
                (TRENDMODE == 1) & (self.Close < self.SMA50) & (self.ADX > 25),  # Trend + MA + ADX (SELL)
                (TRENDMODE == 0) & (self.RSI < 30) & (self.Close < self.Lower_BBand),  # Cycle + self.RSI + BB (BUY)
                (TRENDMODE == 0) & (self.RSI > 70) & (self.Close > self.Upper_BBand),  # Cycle + self.RSI + BB (SELL)
                (TRENDMODE == 1) & (self.MACD > self.MACD_signal),  # Trend + self.MACD (BUY)
                (TRENDMODE == 1) & (self.MACD < self.MACD_signal),  # Trend + self.MACD (SELL)
                (TRENDMODE == 0) & (self.STOCHk > self.STOCHd) & (self.STOCHk < 20),  # Cycle + Stoch (BUY)
                (TRENDMODE == 0) & (self.STOCHk < self.STOCHd) & (self.STOCHk > 80),  # Cycle + Stoch (SELL)
                (TRENDMODE == 1) & (self.OBV > self.OBV.shift(1)),  # Trend + OBV (BUY)
                (TRENDMODE == 1) & (self.OBV < self.OBV.shift(1)),  # Trend + OBV (SELL)
                (TRENDMODE == 1) & (CMF > 0),  # Trend + CMF (BUY)
                (TRENDMODE == 1) & (CMF < 0)   # Trend + CMF (SELL)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del TRENDMODE, CMF
        
        return {
            'trendmode': trendmode,
            'trendmode_dir': trendmode_dir
            }
    
    # HT_PHASOR - Hilbert Transform - Phasor Components
    # ----------------------------------------------------
    def Phasor_Components(self):
        
        inphase, quadrature = talib.HT_PHASOR(self.Close)
        Cycle_Phase = numpy.degrees(numpy.arctan2(quadrature, inphase))
        Phasor_Magnitude = numpy.sqrt(inphase**2 + quadrature**2)
        
        cycle_phase = Cycle_Phase.round(1)
        phasor_inphase = self._single_percentage(inphase)
        phasor_inphase_color = self._single_column_color(inphase)
        phasor_quad = self._single_percentage(quadrature)
        phasor_quad_color = self._single_column_color(quadrature)
        cycle_phase_dir = numpy.select(
            [
                (Phasor_Magnitude.shift(1) < Phasor_Magnitude),  # Trend Strengthening
                (Phasor_Magnitude.shift(1) > Phasor_Magnitude),  # Trend Weakening
                (Cycle_Phase.shift(1) < 0) & (Cycle_Phase > 0),  # Bullish Cycle Reversal
                (Cycle_Phase.shift(1) > 0) & (Cycle_Phase < 0),  # Bearish Cycle Reversal
                (self.Close > self.Close.shift(1)) & (Cycle_Phase < Cycle_Phase.shift(1)),  # Bearish Divergence
                (self.Close < self.Close.shift(1)) & (Cycle_Phase > Cycle_Phase.shift(1)),  # Bullish Divergence
                (inphase.shift(1) > inphase) & (quadrature.shift(1) < quadrature),  # Uptrend (Clockwise)
                (inphase.shift(1) < inphase) & (quadrature.shift(1) > quadrature)   # Downtrend (Counterclockwise)
            ],
            ['call', 'put', 'call', 'put', 'put', 'call', 'call', 'put'],
            default='nut'
        )
        
        del inphase, quadrature, Cycle_Phase, Phasor_Magnitude
        
        return {
            'cycle_phase': cycle_phase,
            'phasor_inphase': phasor_inphase.round(1),
            'phasor_inphase_color': phasor_inphase_color,
            'phasor_quad': phasor_quad.round(1),
            'phasor_quad_color': phasor_quad_color,
            'cycle_phase_dir': cycle_phase_dir
            }
    
    # HT_SINE - Hilbert Transform - SineWave
    # ----------------------------------------------------
    def SineWave(self):
        
        SINE, LEADSINE =  talib.HT_SINE(self.Close)
        
        sine_wave = self._single_percentage(SINE)
        sine_wave_color = self._single_column_color(SINE)
        lead_wave = self._single_percentage(LEADSINE)
        lead_wave_color = self._single_column_color(LEADSINE)
        sine_wave_dir = numpy.select(
            [
                (SINE.shift(1) < LEADSINE.shift(1)) & (SINE > LEADSINE),
                (SINE.shift(1) > LEADSINE.shift(1)) & (SINE < LEADSINE),
                (SINE.shift(1) < -0.9) & (SINE > -0.9),
                (SINE.shift(1) > 0.9) & (SINE < 0.9),
                (LEADSINE > LEADSINE.shift(1)),
                (LEADSINE < LEADSINE.shift(1)),
                (abs(SINE - SINE.shift(1)) < 0.05) & (abs(LEADSINE - LEADSINE.shift(1)) < 0.05),
                (SINE > 0.9) & self.Close > self.Close.shift(1),
                (SINE < -0.9) & self.Close < self.Close.shift(1),
                (abs(SINE) > 0.5) & (SINE > 0.9),
                (abs(SINE) < 0.5) & (SINE < -0.9)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'nut', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del SINE, LEADSINE
        
        return {
            'sine_wave': sine_wave.round(1),
            'sine_wave_color': sine_wave_color,
            'lead_wave': lead_wave.round(1),
            'lead_wave_color': lead_wave_color,
            'sine_wave_dir': sine_wave_dir
            }
    
    # ATR - Average True Range
    # ----------------------------------------------------
    def Average_True_Range(self):
        
        NATR = talib.NATR(self.High, self.Low, self.Close, timeperiod=self.period)
        
        atr = self._single_percentage(self.ATR)
        atr_color = self._single_column_color(self.ATR)
        natr = self._single_percentage(NATR)
        natr_color = self._single_column_color(NATR)
        atr_dir = numpy.select(
    [
                (self.Close > self.Close.shift(1) + (2 * self.ATR)),  # ATR Breakout (Bullish)
                (self.Close < self.Close.shift(1) - (2 * self.ATR)),  # ATR Breakdown (Bearish)
                (NATR > 0.5) & (self.SMA50 > self.SMA200),  # ATR + MA Bullish Crossover
                (NATR > 0.5) & (self.SMA50 < self.SMA200),  # ATR + MA Bearish Crossover
                (self.Close > self.Upper_BBand) & (NATR > 0.5),  # ATR + Bollinger Band Bullish Breakout
                (self.Close < self.Lower_BBand) & (NATR > 0.5),  # ATR + Bollinger Band Bearish Breakdown
                (self.RSI < 30) & (NATR < 0.5),  # ATR + self.RSI Oversold (Bullish Reversal)
                (self.RSI > 70) & (NATR > 0.5),  # ATR + self.RSI Overbought (Bearish Reversal)
                (self.MACD > self.MACD_signal) & (NATR > 0.5),  # ATR + self.MACD Bullish Signal
                (self.MACD < self.MACD_signal) & (NATR > 0.5),  # ATR + self.MACD Bearish Signal
                (NATR < 1) & (self.Close > self.SMA50),  # Low Volatility Reversal (Bullish)
                (NATR < 1) & (self.Close < self.SMA50),  # Low Volatility Reversal (Bearish)
                (NATR > NATR.shift(1)) & (self.Close > self.SMA50),  # ATR Trend Confirmation (Bullish)
                (NATR > NATR.shift(1)) & (self.Close < self.SMA50),  # ATR Trend Confirmation (Bearish)
                (NATR > 5)  # Trend Exhaustion (Possible Reversal)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'nut'],
            default='nut'
        )
        
        natr_dir = numpy.select(
            [
                (self.Close > self.Close.shift(periods=1) + (NATR / 100 * self.Close.shift(periods=1))),
                (self.Close < self.Close.shift(periods=1) - (NATR / 100 * self.Close.shift(periods=1))),
                (NATR < 1) & (self.Close > self.SMA50),
                (NATR < 1) & (self.Close < self.SMA50),
                (NATR > NATR.shift(1)) & (self.Close > self.SMA50),
                (NATR > NATR.shift(1)) & (self.Close < self.SMA50),
                (NATR > 5),
                (NATR > 0.5) & (self.SMA50 > self.SMA200),
                (NATR > 0.5) & (self.SMA50 < self.SMA200),
                (NATR > 0.5) & (self.Close < self.Lower_BBand),
                (NATR > 0.5) & (self.Close > self.Upper_BBand),
                (NATR < 0.5) & (self.RSI < 30),
                (NATR > 0.5) & (self.RSI > 70),
                (NATR > 0.5) & (self.MACD > self.MACD_signal),
                (NATR > 0.5) & (self.MACD < self.MACD_signal)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'nut', 'call', 'put', 'put', 'call', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del NATR
        
        return {
            'atr': atr.round(1),
            'atr_color': atr_color,
            'atr_dir': atr_dir,
            'natr': natr.round(1),
            'natr_color': natr_color,
            'natr_dir': natr_dir
            }
    
    # TRANGE - True Range
    # ----------------------------------------------------
    def True_Range(self):
        
        TRANGE = talib.TRANGE(self.High, self.Low, self.Close)
        
        TSMA = talib.SMA(TRANGE, timeperiod=self.period)
        TR_Threshold = numpy.percentile(TRANGE, 75)
        TR_STD = TRANGE.rolling(10).std()
        Upper_Band = TSMA + 2 * TR_STD
        Lower_Band = TSMA - 2 * TR_STD
        Donchian_High = self.High.rolling(window=20).max()
        Donchian_Low = self.Low.rolling(window=20).min()
        
        trange = self._single_percentage(TRANGE)
        trange_color = self._single_column_color(TRANGE)
        trange_dir = numpy.select(
            [
                (TRANGE > TRANGE.shift(1)) & (self.Close > self.SMA50) & (self.ADX > 25),  # Strong Bullish Trend
                (TRANGE > TRANGE.shift(1)) & (self.Close < self.SMA50) & (self.ADX > 25),  # Strong Bearish Trend
                (self.Close > self.Close.shift(1) + TRANGE) & (TRANGE > TR_Threshold),  # Bullish TR Breakout
                (self.Close < self.Close.shift(1) - TRANGE) & (TRANGE > TR_Threshold),  # Bearish TR Breakdown
                (self.Close > Donchian_High) & (TRANGE > TR_Threshold),  # Bullish Donchian Breakout
                (self.Close < Donchian_Low) & (TRANGE > TR_Threshold),  # Bearish Donchian Breakdown
                (self.Close > Donchian_High.shift(1)) & (self.Close < Donchian_High),  # Bullish False Breakout
                (self.Close < Donchian_Low.shift(1)) & (self.Close > Donchian_Low),  # Bearish False Breakout
                (TRANGE > (2 * TSMA)),  # Sudden TR Spike → Possible Reversal
                (TRANGE > TR_Threshold) & (self.RSI > 70),  # Overbought (Bearish Reversal)
                (TRANGE < TR_Threshold) & (self.RSI < 30),  # Oversold (Bullish Reversal)
                (TRANGE > TR_Threshold) & (self.MACD > self.MACD_signal),  # Bullish self.MACD Crossover
                (TRANGE > TR_Threshold) & (self.MACD < self.MACD_signal),  # Bearish self.MACD Crossover
                (TRANGE < Lower_Band),  # Low TR → Consolidation (Breakout Expected)
                (TRANGE > Upper_Band),  # High TR → Possible Reversal
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'put', 'call', 'nut', 'put', 'call', 'call', 'put', 'nut', 'nut'],
            default='nut'
        )
        
        del TRANGE, TSMA, TR_Threshold, TR_STD, Upper_Band, Lower_Band, Donchian_High, Donchian_Low
        
        return {
            'trange': trange.round(1),
            'trange_color': trange_color,
            'trange_dir': trange_dir
            }
    
    # TRIX - Triple Smooth EMA
    # ----------------------------------------------------
    def Triple_Smooth_EMA(self):
        
        TRIX = talib.TRIX(self.Close, timeperiod=self.period)
        TRIX_short = talib.TRIX(self.Close, timeperiod=(self.period/3))
        TRIX_long = talib.TRIX(self.Close, timeperiod=self.period*3)
        SLOPE = TRIX.diff()
        
        ATR_per = (self.ATR / self.Close) * 100  # Normalize ATR
        
        trix = self._single_percentage(TRIX)
        trix_color = self._single_column_color(TRIX)
        trix_dir = numpy.select(
            [
                (self.Close > TRIX) & (SLOPE > 0),  # Price above T3 EMA & T3 EMA rising
                (self.Close < TRIX) & (SLOPE < 0),  # Price below T3 EMA & T3 EMA falling
                TRIX_short > TRIX_long,  # T3 EMA Bullish Crossover
                TRIX_short < TRIX_long,  # T3 EMA Bearish Crossover
                (self.RSI < 30) & (self.Close > TRIX),  # self.RSI Oversold + Price Above T3 EMA
                (self.RSI > 70) & (self.Close < TRIX),  # self.RSI Overbought + Price Below T3 EMA
                (self.MACD > self.MACD_signal) & (self.Close > TRIX),  # self.MACD Bullish Crossover + Uptrend
                (self.MACD < self.MACD_signal) & (self.Close < TRIX),  # self.MACD Bearish Crossover + Downtrend
                (self.Close > TRIX) & (ATR_per.diff() > 0),  # ATR Increasing + Uptrend
                (self.Close < TRIX) & (ATR_per.diff() < 0),  # ATR Decreasing + Downtrend
                (self.Close < self.Lower_BBand) & (self.Close > TRIX),  # Bollinger Reversal (Bullish)
                (self.Close > self.Upper_BBand) & (self.Close < TRIX),  # Bollinger Reversal (Bearish)
                (self.STOCHk > self.STOCHd) & (self.STOCHk < 20) & (self.Close > TRIX),  # Stochastic Bullish
                (self.STOCHk < self.STOCHd) & (self.STOCHk > 80) & (self.Close < TRIX)  # Stochastic Bearish
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del TRIX, TRIX_short, TRIX_long, SLOPE, ATR_per
        
        return {
            'trix': trix.round(1),
            'trix_color': trix_color,
            'trix_dir': trix_dir
            }
    
    # Houlihan Lokey Inc 
    # ----------------------------------------------------
    def Houlihan_Lokey_Inc_Average(self):
        
        # Houlihan Price Ratio (HPR)
        HPR = talib.DIV(self.High, talib.ADD(self.High, self.Low))
        # Houlihan Moving Average (HMA)
        HMA = talib.SMA(HPR, timeperiod=self.period)
        # Houlihan Strength Index (HSI)
        HSI = ((self.Close - self.Low) / (self.High - self.Low)) * 100
        
        houlihan_hpr = self._single_percentage(HPR)
        houlihan_hpr_color = self._single_column_color(HPR)
        houlihan_hma = self._single_percentage(HMA)
        houlihan_hma_color = self._single_column_color(HMA)
        houlihan_hsi = HSI.round(1)
        houlihan_hsi_color = self._single_column_color(HSI)
        houlihan_dir = numpy.select(
            [
                (HPR > 0.6) & (HSI.shift(periods=1) < 30) & (HSI > 30) & (HMA > HMA.shift(1)),  # Buy
                (HPR < 0.4) & (HSI.shift(periods=1) > 70) & (HSI < 70) & (HMA < HMA.shift(1)),  # Sell
                # Trend Reversal Strategy
                (HMA > HMA.shift(1)) & (HSI.shift(1) < 50) & (HSI > 50),  # Buy
                (HMA < HMA.shift(1)) & (HSI.shift(1) > 50) & (HSI < 50),  # Sell
                # Overbought/Oversold Strategy
                (HSI.shift(1) < 20) & (HSI > 20),  # Buy when leaving oversold
                (HSI.shift(1) > 80) & (HSI < 80),  # Sell when leaving overbought
                # Volatility Breakout Strategy
                (HPR > HPR.shift(1)) & (HSI.shift(1) < 50) & (HSI > 50),  # Buy
                (HPR < HPR.shift(1)) & (HSI.shift(1) > 50) & (HSI < 50),  # Sell
                # Divergence Strategy
                (self.Low < self.Low.shift(1)) & (HSI > HSI.shift(1)),  # Bullish Divergence (Buy)
                (self.High > self.High.shift(1)) & (HSI < HSI.shift(1))   # Bearish Divergence (Sell)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],  # Buy or Sell
            default='nut'  # No trade
        )
        
        del HPR, HMA, HSI
        
        return {
            'houlihan_hpr': houlihan_hpr.round(1),
            'houlihan_hpr_color': houlihan_hpr_color,
            'houlihan_hma': houlihan_hma.round(1),
            'houlihan_hma_color': houlihan_hma_color,
            'houlihan_hsi': houlihan_hsi,
            'houlihan_hsi_color': houlihan_hsi_color,
            'houlihan_dir': houlihan_dir
            }
    
    # MAD - Moving Average Deviation
    # ----------------------------------------------------
    def Moving_Average_Deviation(self):
        
        MAD_Upper = self.MAD.rolling(self.period).quantile(0.75)
        MAD_Lower = self.MAD.rolling(self.period).quantile(0.25)
        
        SMA_ADX = talib.SMA(self.ADX, timeperiod=self.period)
        BB_Width = (self.Upper_BBand - self.Lower_BBand) / self.SMA50 * 100
        SMA_BB_Width = talib.SMA(BB_Width, timeperiod=self.period)
        
        mad = self._triple_percentage(self.MAD, MAD_Upper, MAD_Lower)
        mad_per = self._single_percentage(self.MAD)
        mad_color = self._single_column_color(self.MAD)
        mad_dir = numpy.select(
            [
                (self.MAD > 0) & (self.ADX > SMA_ADX),  # Bullish Trend
                (self.MAD < 0) & (self.ADX > SMA_ADX),  # Bearish Trend
                (self.MAD < MAD_Lower) & (self.RSI < 30),  # Oversold Buy
                (self.MAD > MAD_Upper) & (self.RSI > 70),  # Overbought Sell
                (self.MAD < MAD_Lower) & (self.Close > self.SMA50) & (self.RSI < 40),  # Bullish Reversal RSI
                (self.MAD > MAD_Upper) & (self.Close < self.SMA50) & (self.RSI > 60),  # Bearish Reversal RSI
                (self.Close < self.Lower_BBand) & (self.MAD < MAD_Lower) & (BB_Width > SMA_BB_Width),  # Bullish Bollinger Bands Breakout
                (self.Close > self.Upper_BBand) & (self.MAD > MAD_Upper) & (BB_Width > SMA_BB_Width),  # Bearish Bollinger Bands Breakout
                (self.MAD > 0) & (self.MAD > self.MAD.shift(1)) & (self.MACD > self.MACD_signal) & (self.ADX > SMA_ADX),  # Bullish MACD Confirmation (Only when ADX is strong)
                (self.MAD < 0) & (self.MAD < self.MAD.shift(1)) & (self.MACD < self.MACD_signal) & (self.ADX > SMA_ADX),  # Bearish MACD Confirmation (Only when ADX is strong)
                (self.MAD.shift(1) < 0) & (self.MAD > 0),  # MAD Crosses Above Zero
                (self.MAD.shift(1) > 0) & (self.MAD < 0),  # MAD Crosses Below Zero
                (self.Close < self.Close.shift(1)) & (self.MAD > self.MAD.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (self.MAD < self.MAD.shift(1))   # Bearish Divergence
            ],
            ['call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del MAD_Upper, MAD_Lower, SMA_ADX, BB_Width, SMA_BB_Width
        
        return {
            'mad': mad.round(1),
            'mad_per': mad_per.round(1),
            'mad_color': mad_color,
            'mad_dir': mad_dir
            }
    
    # ALLIGATOR - Alligator Indicator
    # ----------------------------------------------------
    def Alligator_Indicator(self):
        
        Alligator_Expansion = (self.Gator_JAW - self.Gator_TEETH).abs() + (self.Gator_TEETH - self.Gator_LIPS).abs()
        
        alligator = (((((self.Gator_TEETH / (self.Gator_JAW + self.Gator_LIPS)) * 100) % 1) *100) % 1) * 100
        # ALLIGATOR Width as a Percentage
        alligator_per = self._triple_percentage(self.Gator_JAW, self.Gator_TEETH, self.Gator_LIPS)
        alligator_color = self._single_column_color(alligator_per)
        alligator_dir = numpy.select(
            [
                (self.Gator_LIPS.shift(1) < self.Gator_TEETH.shift(1)) & (self.Gator_LIPS > self.Gator_TEETH) & 
                (self.Gator_TEETH.shift(1) < self.Gator_JAW.shift(1)) & (self.Gator_TEETH > self.Gator_JAW),  # Bullish crossover
                (self.Gator_LIPS.shift(1) > self.Gator_TEETH.shift(1)) & (self.Gator_LIPS < self.Gator_TEETH) & 
                (self.Gator_TEETH.shift(1) > self.Gator_JAW.shift(1)) & (self.Gator_TEETH < self.Gator_JAW),  # Bearish crossover
                (self.Gator_LIPS > self.Gator_TEETH) & (self.Gator_TEETH > self.Gator_JAW) & (self.RSI < 30) & (self.MACD > self.MACD_signal) & 
                (self.Close > self.Upper_BBand) & (self.Vol > self.VOL_MA) & (self.ATR > self.ATR.shift(1)), # Strong BUY (Uptrend + Momentum + Oversold RSI + Breakout + High Volume + Rising ATR)
                (self.Gator_LIPS < self.Gator_TEETH) & (self.Gator_TEETH < self.Gator_JAW) & (self.MACD < self.MACD_signal) & (self.RSI > 70) & 
                (self.Close < self.Lower_BBand) & (self.Vol > self.VOL_MA) & (self.ATR > self.ATR.shift(1)), # Strong SELL (Downtrend + Momentum + Overbought self.RSI + Breakdown + High Volume + Rising ATR)
                (self.Gator_LIPS > self.Gator_TEETH) & (self.Gator_TEETH > self.Gator_JAW) & (self.ATR > self.ATR.shift(1)) & 
                (Alligator_Expansion > Alligator_Expansion.shift(1)),   # Weak BUY (Uptrend + Expanding Alligator + Rising ATR)
                (self.Gator_LIPS < self.Gator_TEETH) & (self.Gator_TEETH < self.Gator_JAW) & (self.ATR > self.ATR.shift(1)) & 
                (Alligator_Expansion > Alligator_Expansion.shift(1))    # Weak SELL (Downtrend + Expanding Alligator + Rising ATR)
            ],
            ['call', 'put', 'call', 'put', 'call', 'put'],
            default='nut'
        )
        
        del Alligator_Expansion
        
        return {
            'alligator': alligator.round(1),
            'alligator_per': alligator_per.round(1),
            'alligator_color': alligator_color,
            'alligator_dir': alligator_dir
            }
    
    # GATOR - Gator Oscillator
    # ----------------------------------------------------
    def Gator_Oscillator(self):
        
        Gator_Expansion = self.Gator_UPPER + self.Gator_LOWER
        gator_upper_per = self._single_percentage(self.Gator_UPPER)
        gator_lower_per = self._single_percentage(self.Gator_LOWER)
        
        gator_upper = gator_upper_per
        gator_upper_color = self.Gator_UPPER_color
        gator_lower = gator_lower_per
        gator_lower_color = self.Gator_LOWER_color
        gator_dir = numpy.select(
            [
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Gator_LOWER < self.Gator_LOWER.shift(1)),  # Gator Awakening (BUY)
                (self.Gator_UPPER < self.Gator_UPPER.shift(1)) & (self.Gator_LOWER > self.Gator_LOWER.shift(1)),  # Gator Sleeping (HOLD)
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Gator_LOWER > self.Gator_LOWER.shift(1)),  # Gator Expanding (Strong Trend)
                (self.Gator_UPPER < self.Gator_UPPER.shift(1)) & (self.Gator_LOWER < self.Gator_LOWER.shift(1)),  # Gator Contracting (Weak Trend)
                (self.Gator_UPPER > self.Gator_LOWER),  # Gator Bullish Crossover
                (self.Gator_UPPER < self.Gator_LOWER),  # Gator Bearish Crossover
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.RSI > 50),  # Gator Expanding + self.RSI Bullish
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.RSI < 50),  # Gator Expanding + self.RSI Bearish
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.MACD > self.MACD_signal),  # Gator + self.MACD Bullish
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.MACD < self.MACD_signal),  # Gator + self.MACD Bearish
                (self.Gator_UPPER > self.Upper_BBand),  # Bollinger Bands Breakout (BUY)
                (self.Gator_LOWER < self.Lower_BBand),  # Bollinger Bands Breakdown (SELL)
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.ATR > self.ATR.shift(1)),  # Gator Expanding + High Volatility (BUY)
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.ATR < self.ATR.shift(1)),  # Gator Expanding + Low Volatility (SELL)
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Vol > self.Vol.shift(1)),  # Gator Expanding + Rising Volume (BUY)
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Vol < self.Vol.shift(1)),  # Gator Expanding + Falling Volume (SELL)
                (self.Vol > self.VOL_MA * 1.5) & (self.Gator_UPPER > self.Gator_UPPER.shift(1)),  # High Volume Bullish
                (self.Vol > self.VOL_MA * 1.5) & (self.Gator_UPPER < self.Gator_UPPER.shift(1)),  # High Volume Bearish
                (gator_upper_per > 10) & (gator_lower_per > 10),  # Strong Trend
                (gator_upper_per < 5) & (gator_lower_per < 5),  # Weak Trend
                (gator_upper_per > 0) & (gator_lower_per < 0),  # Bullish Divergence
                (gator_upper_per < 0) & (gator_lower_per > 0),  # Bearish Divergence
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Gator_LOWER > self.Gator_LOWER.shift(1)) & (self.MACD > self.MACD_signal),  # Gator Bullish + self.MACD Bullish
                (self.Gator_UPPER < self.Gator_UPPER.shift(1)) & (self.Gator_LOWER < self.Gator_LOWER.shift(1)) & (self.MACD < self.MACD_signal),  # Gator Bearish + self.MACD Bearish
                (self.Gator_UPPER > self.Gator_UPPER.shift(1)) & (self.Gator_LOWER < self.Gator_LOWER.shift(1)) & (self.RSI > 50) & (self.MACD > self.MACD_signal),  # Strong BUY (Gator Awakening + self.RSI > 50 + self.MACD Bullish)
                (self.Gator_UPPER < self.Gator_UPPER.shift(1)) & (self.Gator_LOWER > self.Gator_LOWER.shift(1)) & (self.RSI < 50) & (self.MACD < self.MACD_signal),  # Strong SELL (Gator Awakening + self.RSI < 50 + self.MACD Bearish)
                (Gator_Expansion > Gator_Expansion.shift(1)) & (self.RSI > 50),  # Weak BUY (Expanding Gator + self.RSI)
                (Gator_Expansion > Gator_Expansion.shift(1)) & (self.RSI < 50),  # Weak SELL (Expanding Gator + self.RSI)
            ],
            [
                "call", "nut", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", 
                "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", 
                "call", "put", "call", "put"
            ],
            default="nut"
        )
        
        del Gator_Expansion, gator_upper_per, gator_lower_per
        
        return {
            'gator_upper': gator_upper.round(1),
            'gator_upper_color': gator_upper_color,
            'gator_lower': gator_lower.round(1),
            'gator_lower_color': gator_lower_color,
            'gator_dir': gator_dir
            }
    
    # ERI - ELDER RAY INDEX
    # ----------------------------------------------------
    def Elder_Ray_Index(self):
        
        Bull_Power = self.High - self.EMA50
        Bear_Power = self.Low - self.EMA50
        
        High_Volume = self.Vol > self.VOL_MA * 1.5  # High Volume Signal
        
        bull_power = self._single_percentage(Bull_Power)
        bull_power_color = self._single_column_color(Bull_Power)
        bear_power = self._single_percentage(Bear_Power)
        bear_power_color = self._single_column_color(Bear_Power)
        ERI_dir = numpy.select(
            [
                (Bull_Power > 0) & (Bull_Power > Bull_Power.shift(1)),  # Strengthening Bull Power → BUY
                (Bear_Power < 0) & (Bear_Power < Bear_Power.shift(1)),  # Strengthening Bear Power → SELL
                # 🔥 STRONG BUY: Elder Ray + ADX Trend + self.RSI Bullish + self.MACD Bullish + Volume Surge
                (Bull_Power > 0) & (self.ADX > 25) & (self.RSI > 50) & (self.MACD > self.MACD_signal) & (High_Volume),
                # 📈 Regular BUY: Elder Ray + self.RSI Bullish + Bollinger Breakout
                (Bull_Power > 0) & (self.RSI > 50) & (self.Close > self.Upper_BBand),
                # ⚠️ WEAK BUY: Elder Ray + Stochastic Overbought + Low Volatility
                (Bull_Power > 0) & (self.STOCHk > self.STOCHd) & (self.ATR < self.ATR.shift(1)),
                # 🔻 STRONG SELL: Elder Ray Bearish + ADX Trend + self.RSI Bearish + self.MACD Bearish + Volume Surge
                (Bear_Power < 0) & (self.ADX > 25) & (self.RSI < 50) & (self.MACD < self.MACD_signal) & (High_Volume),
                # 📉 Regular SELL: Elder Ray + self.RSI Bearish + Bollinger Breakdown
                (Bear_Power < 0) & (self.RSI < 50) & (self.Close < self.Lower_BBand),
                # ⚠️ WEAK SELL: Elder Ray + Stochastic Oversold + Low Volatility
                (Bear_Power < 0) & (self.STOCHk < self.STOCHd) & (self.ATR < self.ATR.shift(1)),
                # ❌ HOLD: No Strong Signal
                (Bull_Power < 0) & (Bear_Power > 0)
            ],
            ['call', 'put', 'call', 'call', 'call', 'put', 'put', 'put', 'nut'],
            default='nut'
        )
        
        del Bull_Power, Bear_Power, High_Volume
        
        return {
            'bull_power': bull_power.round(1),
            'bull_power_color': bull_power_color,
            'bear_power': bear_power.round(1),
            'bear_power_color': bear_power_color,
            'ERI_dir': ERI_dir
            }
    
    # ACCELERATOR_OSCILLATOR - Accelerator Oscillator + Awesome_Osillator
    # ----------------------------------------------------
    def Accelerator_Oscillator(self):
        
        ACCELERATOR_OSCILLATOR = self.AWO - talib.SMA(self.AWO, timeperiod=self.period)
        Tenkan_Sen = (self.High.rolling(self.period).max() + self.Low.rolling(self.period).min()) / 2
        Kijun_Sen = (self.High.rolling(self.period*2).max() + self.Low.rolling(self.period*2).min()) / 2
        Senkou_Span_A = ((Tenkan_Sen + Kijun_Sen) / 2).shift(self.period*2)
        Senkou_Span_B = ((self.High.rolling(self.period*3).max() + self.Low.rolling(self.period*3).min()) / 2).shift(self.period*2)
        
        awo = self._single_percentage(self.AWO).round(1)
        awo_color = self._single_column_color(self.AWO)
        aco = self._single_percentage(ACCELERATOR_OSCILLATOR).round(1)
        aco_color = self._single_column_color(ACCELERATOR_OSCILLATOR)
        awo_dir = numpy.select(
            [
                # 🔥 Strong Buy/Sell Confirmation with AO + self.MACD + self.RSI
                (self.AWO > 0) & (self.MACD > self.MACD_signal) & (self.RSI > 50),  # Strong Buy
                (self.AWO < 0) & (self.MACD < self.MACD_signal) & (self.RSI < 50),  # Strong Sell
                # 📈 Momentum & Volume Confirmation
                (self.AWO > self.AWO.shift(1)) & (self.Vol > self.Vol.shift(1)),  # Buy (AO Rising + Volume Increasing)
                (self.AWO < self.AWO.shift(1)) & (self.Vol < self.Vol.shift(1)),  # Sell (AO Falling + Volume Decreasing)
                # 🔄 Trend Reversal & Divergence Signals
                (self.Close < self.Close.shift(1)) & (self.AWO > self.AWO.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (self.AWO < self.AWO.shift(1)),  # Bearish Divergence
                # 🏆 Twin Peaks & Saucer Patterns
                (self.AWO.shift(2) > self.AWO.shift(1)) & (self.AWO.shift(1) < self.AWO) & (self.AWO > 0),  # Bullish Twin Peaks
                (self.AWO.shift(2) < self.AWO.shift(1)) & (self.AWO.shift(1) > self.AWO) & (self.AWO < 0),  # Bearish Twin Peaks
                (self.AWO > 0) & (self.AWO.shift(2) > self.AWO.shift(1)) & (self.AWO.shift(1) < self.AWO),  # Bullish Saucer
                (self.AWO < 0) & (self.AWO.shift(2) < self.AWO.shift(1)) & (self.AWO.shift(1) > self.AWO),  # Bearish Saucer
                # ⚡ AO Crossovers & Trend Confirmation
                (self.AWO > 0) & (self.AWO.shift(1) < 0),  # Bullish Crossover
                (self.AWO < 0) & (self.AWO.shift(1) > 0),  # Bearish Crossover
                (self.AWO > 0) & (self.Close > self.SMA50),  # Strong Uptrend Confirmation
                (self.AWO < 0) & (self.Close < self.SMA50),  # Strong Downtrend Confirmation
                # 📊 AO + self.MACD + self.RSI
                (self.AWO > 0) & (self.MACD > self.MACD_signal),  # AO + self.MACD Bullish
                (self.AWO < 0) & (self.MACD < self.MACD_signal),  # AO + self.MACD Bearish
                (self.AWO > 0) & (self.RSI > 50),  # AO + self.RSI Bullish
                (self.AWO < 0) & (self.RSI < 50),  # AO + self.RSI Bearish
                # 🚀 Breakout & Breakdown Trades
                (self.AWO > 0) & (self.Close > self.Upper_BBand),  # Bullish Breakout
                (self.AWO < 0) & (self.Close < self.Lower_BBand),  # Bearish Breakdown
                # 🔊 Volume-Based Confirmation
                (self.AWO > self.AWO.shift(1)) & (self.Vol > self.Vol.shift(1)),  # Bullish Volume Surge
                (self.AWO < self.AWO.shift(1)) & (self.Vol < self.Vol.shift(1)),  # Bearish Volume Drop
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        
        aco_dir = numpy.select(
            [
                (ACCELERATOR_OSCILLATOR > 0) & (self.ADX > 25),  # AC + ADX Strong Trend
                (ACCELERATOR_OSCILLATOR < 0) & (self.ADX > 25),  # AC + ADX Strong Downtrend
                (ACCELERATOR_OSCILLATOR > 0) & (self.Close > self.Upper_BBand),  # AC + BB Breakout
                (ACCELERATOR_OSCILLATOR < 0) & (self.Close < self.Lower_BBand),  # AC + BB Breakdown
                (ACCELERATOR_OSCILLATOR > 0) & (self.Close > self.VWAP),  # AC + VWAP Bullish
                (ACCELERATOR_OSCILLATOR < 0) & (self.Close < self.VWAP),  # AC + VWAP Bearish
                (ACCELERATOR_OSCILLATOR > 0) & (self.Vol > self.VOL_MA * 1.5),  # AC + Volume Spike Bullish
                (ACCELERATOR_OSCILLATOR < 0) & (self.Vol > self.VOL_MA * 1.5),  # AC + Volume Spike Bearish
                (ACCELERATOR_OSCILLATOR > 0) & (self.Close > Senkou_Span_A) & (self.Close > Senkou_Span_B),  # AC + Ichimoku Bullish
                (ACCELERATOR_OSCILLATOR < 0) & (self.Close < Senkou_Span_A) & (self.Close < Senkou_Span_B),  # AC + Ichimoku Bearish
                (ACCELERATOR_OSCILLATOR > 0) & (self.MACD > self.MACD_signal) & (self.RSI > 50),  # Strong Buy: AC + self.MACD + self.RSI Bullish
                (ACCELERATOR_OSCILLATOR < 0) & (self.MACD < self.MACD_signal) & (self.RSI < 50),  # Strong Sell: AC + self.MACD + self.RSI Bearish
                (ACCELERATOR_OSCILLATOR > ACCELERATOR_OSCILLATOR.shift(1)) & (self.Vol > self.Vol.shift(1)),  # AC + Rising Volume (BUY)
                (ACCELERATOR_OSCILLATOR < ACCELERATOR_OSCILLATOR.shift(1)) & (self.Vol < self.Vol.shift(1)),  # AC + Falling Volume (SELL)
                (self.Close < self.Close.shift(1)) & (ACCELERATOR_OSCILLATOR > ACCELERATOR_OSCILLATOR.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (ACCELERATOR_OSCILLATOR < ACCELERATOR_OSCILLATOR.shift(1)),  # Bearish Divergence
                (ACCELERATOR_OSCILLATOR > 0) & (self.AWO > 0),  # AC + AO Bullish Confirmation
                (ACCELERATOR_OSCILLATOR < 0) & (self.AWO < 0),  # AC + AO Bearish Confirmation
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default='nut'
        )
        
        del ACCELERATOR_OSCILLATOR, Tenkan_Sen, Kijun_Sen, Senkou_Span_A, Senkou_Span_B
        
        return {
            'awo': awo,
            'awo_color': awo_color,
            'awo_dir': awo_dir,
            'aco': aco,
            'aco_color': aco_color,
            'aco_dir': aco_dir
            }
    
    # CHAIKIN_OSCILLATOR - Chaikin Oscillator
    # ----------------------------------------------------
    def Chaikin_Oscillator(self):
        
        MFM = ((self.Close - self.Low) - (self.High - self.Close)) / (self.High - self.Low)
        MFV = MFM * self.Vol
        ADL = MFV.cumsum()
        CO_Fast = ADL.ewm(span=self.period/3, adjust=False).mean()
        CO_Slow = ADL.ewm(span=self.period, adjust=False).mean()
        CO = CO_Fast - CO_Slow
        
        co = self._single_percentage(CO)
        co_per = (CO_Fast / (CO_Slow - CO_Fast)).round(1)
        co_color = self._single_column_color(CO)
        co_dir = numpy.select(
            [
                # 🔥 Bullish & Bearish Crossovers
                (CO > 0) & (CO.shift(1) < 0),  # Bullish Crossover
                (CO < 0) & (CO.shift(1) > 0),  # Bearish Crossover
                # 📈 Strong Buy/Sell Confirmation (CO + self.MACD + self.RSI)
                (CO > 0) & (self.MACD > self.MACD_signal) & (self.RSI > 50),  # Strong Buy
                (CO < 0) & (self.MACD < self.MACD_signal) & (self.RSI < 50),  # Strong Sell
                # 📊 Trend Confirmation (CO + AO + ADX)
                (CO > 0) & (self.AWO > 0) & (self.ADX > 25),  # Strong Uptrend
                (CO < 0) & (self.AWO < 0) & (self.ADX > 25),  # Strong Downtrend
                # 🔄 Divergences (Price vs CO)
                (self.Close < self.Close.shift(1)) & (CO > CO.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (CO < CO.shift(1)),  # Bearish Divergence
                # 🚀 Breakouts & Breakdowns (CO + Bollinger Bands)
                (CO > 0) & (self.Close > self.Upper_BBand),  # Breakout Buy
                (CO < 0) & (self.Close < self.Lower_BBand),  # Breakdown Sell
                # 🔊 Volume Confirmation (CO + VWAP)
                (CO > 0) & (self.Close > self.VWAP),  # Bullish Volume Confirmation
                (CO < 0) & (self.Close < self.VWAP),  # Bearish Volume Confirmation
                # 🏆 CO Momentum Confirmation
                (CO > CO.shift(1)) & (self.Vol > self.Vol.shift(1)),  # Bullish Volume Momentum
                (CO < CO.shift(1)) & (self.Vol < self.Vol.shift(1)),  # Bearish Volume Momentum
                # 🎯 Overbought & Oversold Conditions (CO + self.RSI)
                (CO > 0) & (self.RSI > 70),  # Overbought - Potential Reversal
                (CO < 0) & (self.RSI < 30),  # Oversold - Potential Reversal
                # 🚀 Momentum Surge & Breakdown (CO + ADX)
                (CO > 0) & (self.ADX > 30),  # Bullish Momentum Surge
                (CO < 0) & (self.ADX > 30)   # Bearish Momentum Breakdown
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "put", "call", "call", "put"],
            default="nut"
        )
        
        del  MFM, MFV, ADL, CO_Fast, CO_Slow, CO
        
        return {
            'co': co.round(1),
            'co_per': co_per,
            'co_color': co_color,
            'co_dir': co_dir
            }
    
    # HISTORICAL_VOLATILITY - Historical Volatility
    # ----------------------------------------------------
    def Historical_Volatility(self):
        
        hv_period = 60 # since 60 Minutes per hour
        trading_minutes_per_hour = 60   # since 60 Minutes per hour
        log_returns = numpy.log(self.Close / self.Close.shift(1))
        HV = (log_returns.rolling(window=hv_period).std() * numpy.sqrt(trading_minutes_per_hour))
        
        hv = self._single_percentage(HV)
        hv_color = self._single_column_color(HV)
        hv_dir = numpy.select(
            [
                (HV > HV.shift(1)),  # Increasing Volatility
                (HV < HV.shift(1)),  # Decreasing Volatility
                (HV > HV.rolling(hv_period).mean()),  # HV Above Average
                (HV < HV.rolling(hv_period).mean()),  # HV Below Average
                (HV > HV.rolling(hv_period).quantile(0.9)),  # Extreme High Volatility
                (HV < HV.rolling(hv_period).quantile(0.1)),  # Extreme Low Volatility
                (HV > HV.shift(1)) & (self.Close > self.Upper_BBand),  # High self.Vol + Breakout
                (HV > HV.shift(1)) & (self.Close < self.Lower_BBand),  # High self.Vol + Breakdown
                (HV < HV.shift(1)) & (self.Close > self.Upper_BBand),  # Low self.Vol + Fake Breakout
                (HV < HV.shift(1)) & (self.Close < self.Lower_BBand),  # Low self.Vol + Fake Breakdown
                (HV > HV.shift(1)) & (self.ADX > 25) & (self.MACD > self.MACD_signal),  # Strong Uptrend
                (HV > HV.shift(1)) & (self.ADX > 25) & (self.MACD < self.MACD_signal),  # Weak Downtrend
                (HV < HV.shift(1)) & (self.RSI < 30),  # Mean Reveself.RSIon Buy (Oversold)
                (HV < HV.shift(1)) & (self.RSI > 70),  # Mean Reveself.RSIon Sell (Overbought)
                (HV.rolling(hv_period).std() < HV.rolling(hv_period).std().mean()),  # Volatility Squeeze
                (HV < HV.shift(1)) & (self.Close > self.VWAP),  # Low Volatility Buy
                (HV > HV.shift(1)) & (self.Close < self.VWAP)  # High Volatility Sell
            ],
            ["call", "put", "call", "put", "put", "call", "call", "put", "put", "call", "call", "put", "call", "put", "call", "call", "put"],
            default="nut"
        )
        
        del hv_period, trading_minutes_per_hour, log_returns, HV
        
        return {
            'hv': hv.round(1),
            'hv_color': hv_color,
            'hv_dir': hv_dir
            }
    
    # COPPOCK_CURVE - Coppock Curve
    # ----------------------------------------------------
    def Coppock_Curve(self):
        
        ROC_11 = talib.ROCP(self.Close, timeperiod=self.period) * 100
        ROC_14 = talib.ROCP(self.Close, timeperiod=self.period*2) * 100
        Coppock_Raw = ROC_11 + ROC_14
        Coppock_Curve = talib.WMA(Coppock_Raw, timeperiod=self.period)
        
        coppock_raw = self._single_percentage(Coppock_Raw)
        coppock_raw_color = self._single_column_color(Coppock_Raw)
        coppock_curve = self._single_percentage(Coppock_Curve)
        coppock_curve_color = self._single_column_color(Coppock_Curve)
        coppock_curve_dir = numpy.select(
            [
                (Coppock_Curve > 0) & (Coppock_Curve.shift(1) <= 0),  # Bullish Crossover
                (Coppock_Curve < 0) & (Coppock_Curve.shift(1) >= 0),  # Bearish Crossover
                (Coppock_Curve > Coppock_Curve.shift(1)),  # Rising Momentum
                (Coppock_Curve < Coppock_Curve.shift(1)),  # Falling Momentum
                (Coppock_Curve > 0) & (self.Close > self.EMA50),  # EMA Bullish Confirmation
                (Coppock_Curve < 0) & (self.Close < self.EMA50),  # EMA Bearish Confirmation
                (Coppock_Curve > Coppock_Curve.shift(1)) & (self.RSI < 30),  # self.RSI Oversold Buy
                (Coppock_Curve < Coppock_Curve.shift(1)) & (self.RSI > 70),  # self.RSI Overbought Sell
                (Coppock_Curve > Coppock_Curve.shift(1)) & (self.Close > self.Upper_BBand),  # Bollinger Bands Breakout Buy
                (Coppock_Curve < Coppock_Curve.shift(1)) & (self.Close < self.Lower_BBand),  # Bollinger BandsBreakdown Sell
                (Coppock_Curve > Coppock_Curve.shift(1)) & (self.MACD > self.MACD_signal),  # self.MACD Strong Buy
                (Coppock_Curve < Coppock_Curve.shift(1)) & (self.MACD < self.MACD_signal)   # self.MACD Strong Sell
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        
        del ROC_11, ROC_14, Coppock_Raw, Coppock_Curve
        
        return {
            'coppock_raw': coppock_raw.round(1),
            'coppock_raw_color': coppock_raw_color,
            'coppock_curve': coppock_curve.round(1),
            'coppock_curve_color': coppock_curve_color,
            'coppock_curve_dir': coppock_curve_dir
            }
    
    # TSI - True Strength Index
    # ----------------------------------------------------
    def True_Strength_Index(self):
        
        delta = self.Close.diff()
        smoothed_delta = talib.EMA(talib.EMA(delta, timeperiod=self.period), timeperiod=5)
        smoothed_abs_delta = talib.EMA(talib.EMA(abs(delta), timeperiod=self.period), timeperiod=5)
        TSI = 100 * (smoothed_delta / smoothed_abs_delta)
        TSI_Signal = talib.EMA(TSI, timeperiod=self.period)
        
        tsi = self._single_percentage(TSI)
        tsi_color = self._single_column_color(TSI)
        tsi_dir = numpy.select(
            [
                (TSI > TSI_Signal) & (TSI.shift(1) < TSI_Signal.shift(1)),  # TSI Bullish Crossover
                (TSI < TSI_Signal) & (TSI.shift(1) > TSI_Signal.shift(1)),  # TSI Bearish Crossover
                (TSI > 25),  # Overbought - Potential Sell
                (TSI < -25),  # Oversold - Potential Buy
                (TSI > 0),  # Strong Uptrend
                (TSI < 0),  # Strong Downtrend
                (self.Close < self.Close.shift(1)) & (TSI > TSI.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (TSI < TSI.shift(1)),  # Bearish Divergence
                (TSI > TSI.shift(1)),  # Bullish Momentum Surge
                (TSI < TSI.shift(1)),  # Bearish Momentum Drop
                (TSI > TSI_Signal) & (self.MACD > self.MACD_signal),  # TSI + self.MACD Confirm Buy
                (TSI < TSI_Signal) & (self.MACD < self.MACD_signal),  # TSI + self.MACD Confirm Sell
                (TSI > TSI_Signal) & (self.RSI > 50),  # TSI + self.RSI Confirm Uptrend
                (TSI < TSI_Signal) & (self.RSI < 50),  # TSI + self.RSI Confirm Downtrend
                (TSI > 0) & (self.ADX > 25),  # TSI + ADX Strong Trend
                (TSI < 0) & (self.ADX > 25)   # TSI + ADX Strong Downtrend
            ],
            ["call", "put", "put", "call", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        
        del delta, smoothed_delta, smoothed_abs_delta, TSI, TSI_Signal
        
        return {
            'tsi': tsi.round(1),
            'tsi_color': tsi_color,
            'tsi_dir': tsi_dir
            }
    
    # WRSI - Weighted Relative Strength Index
    # ----------------------------------------------------
    def Weighted_Relative_Strength_Index(self):
        
        WRSI = talib.WMA(self.RSI, timeperiod=self.period)
        WRSI_MA = talib.SMA(WRSI, timeperiod=self.period)
        WRSI_Overbought = WRSI.rolling(self.period).quantile(0.90)
        WRSI_Oversold = WRSI.rolling(self.period).quantile(0.10)
        
        wrsi = self._single_percentage(WRSI)
        wrsi_color = self._single_column_color(WRSI)
        wrsi_dir = numpy.select(
            [
                (WRSI > 30) & (WRSI.shift(1) <= 30),  # Oversold Reversal (Buy)
                (WRSI < 70) & (WRSI.shift(1) >= 70),  # Overbought Reversal (Sell)
                (WRSI > WRSI_MA),  # Bullish Crossover
                (WRSI < WRSI_MA),  # Bearish Crossover
                (self.Close < self.Close.shift(1)) & (WRSI > WRSI.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (WRSI < WRSI.shift(1)),  # Bearish Divergence
                (WRSI > 40) & (WRSI < 50),  # Mean Reveself.RSIon Buy
                (WRSI > 50) & (WRSI < 60),  # Mean Reveself.RSIon Sell
                (WRSI > WRSI_Oversold) & (WRSI.shift(1) <= WRSI_Oversold),  # Dynamic Oversold Reversal
                (WRSI < WRSI_Overbought) & (WRSI.shift(1) >= WRSI_Overbought),  # Dynamic Overbought Reversal
                (WRSI < 30) & (self.Close <= self.Lower_BBand),  # Wself.RSI + BB Buy
                (WRSI > 70) & (self.Close >= self.Upper_BBand),  # Wself.RSI + BB Sell
                (WRSI > 50) & (self.MACD > self.MACD_signal),  # Wself.RSI + self.MACD Buy
                (WRSI < 50) & (self.MACD < self.MACD_signal),  # Wself.RSI + self.MACD Sell
                (self.Close < self.Close.shift(5)) & (WRSI > WRSI.shift(5)),  # Bullish Divergence
                (self.Close > self.Close.shift(5)) & (WRSI < WRSI.shift(5)),  # Bearish Divergence
                (WRSI > 50) & (self.ADX > 25),  # Strong Uptrend (Wself.RSI + ADX)
                (WRSI < 50) & (self.ADX > 25),  # Strong Downtrend (Wself.RSI + ADX)
                (WRSI > 50) & (self.Close > self.EMA50), # Wself.RSI + EMA Buy
                (WRSI < 50) & (self.Close < self.EMA50)  # Wself.RSI + EMA Sell
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        del WRSI, WRSI_MA, WRSI_Overbought, WRSI_Oversold
        
        return {
            'wrsi': wrsi.round(1),
            'wrsi_color': wrsi_color,
            'wrsi_dir': wrsi_dir
            }
    
    # KST - Know Sure Thing
    # ----------------------------------------------------
    def Know_Sure_Thing(self):
        
        roc1 = talib.ROC(self.Close, timeperiod=self.period)
        roc2 = talib.ROC(self.Close, timeperiod=self.period+5)
        roc3 = talib.ROC(self.Close, timeperiod=self.period+10)
        roc4 = talib.ROC(self.Close, timeperiod=self.period+20)
        KST = (talib.SMA(roc1, timeperiod=self.period) * 1 +
            talib.SMA(roc2, timeperiod=self.period) * 2 +
            talib.SMA(roc3, timeperiod=self.period) * 3 +
            talib.SMA(roc4, timeperiod=self.period+5) * 4)
        KST_Signal = talib.SMA(KST, timeperiod=self.period)
        
        KST_per = self._single_percentage(KST)
        kst = KST_per
        kst_color = self._single_column_color(KST)
        kst_siganl = self._single_percentage(KST_Signal)
        kst_siganl_color = self._single_column_color(KST_Signal)
        kst_dir = numpy.select(
            [
                (KST > KST_Signal),  # Bullish Crossover
                (KST < KST_Signal),  # Bearish Crossover
                (KST_per > 100),  # Overbought - Sell
                (KST_per < -100),  # Oversold - Buy
                (KST > 0) & (KST.diff() > 0),  # Strong Uptrend
                (KST < 0) & (KST.diff() < 0),  # Strong Downtrend
                (self.Close < self.Close.shift(1)) & (KST > KST.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (KST < KST.shift(1)),  # Bearish Divergence
                (KST > 0) & (self.RSI),  # KST + self.RSI Confirm Uptrend
                (KST < 0) & (self.RSI < 50),  # KST + self.RSI Confirm Downtrend
                (KST > 0) & (self.MACD > self.MACD_signal),  # KST + self.MACD Confirm Buy
                (KST < 0) & (self.MACD < self.MACD_signal),  # KST + self.MACD Confirm Sell
                (KST > 0) & (self.ADX > 25),  # KST + ADX Strong Uptrend
                (KST < 0) & (self.ADX > 25),  # KST + ADX Strong Downtrend
                (KST.diff() > 0),  # KST Momentum Surge
                (KST.diff() < 0),  # KST Momentum Drop
            ],
            ["call", "put", "put", "call", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        
        del roc1, roc2, roc3, roc4, KST, KST_Signal, KST_per
        
        return {
            'kst': kst.round(1),
            'kst_color': kst_color,
            'kst_siganl': kst_siganl.round(1),
            'kst_siganl_color': kst_siganl_color,
            'kst_dir': kst_dir
            }
    
    # IC - Ichimoku Cloud
    # ----------------------------------------------------
    def Ichimoku_Cloud(self):
        
        Tenkan = (talib.MAX(self.High, timeperiod=5) + talib.MIN(self.Low, timeperiod=5)) / 2
        Kijun = (talib.MAX(self.High, timeperiod=self.period) + talib.MIN(self.Low, timeperiod=self.period)) / 2
        Senkou_A = (Tenkan + Kijun) / 2
        Senkou_B = (talib.MAX(self.High, timeperiod=self.period * 2) + talib.MIN(self.Low, timeperiod=self.period * 2)) / 2
        Senkou_A = Senkou_A.shift(self.period)
        Senkou_B = Senkou_B.shift(self.period)
        Chikou = self.Close.shift(-self.period)
        combined_senkou_Max = Senkou_A.combine(Senkou_B, max)
        combined_senkou_Min = Senkou_A.combine(Senkou_B, min)
        
        chikou = (((((self.Close) / (combined_senkou_Max + combined_senkou_Min)) * 100) % 1) * 100).round(1)
        chikou_dir = numpy.select(
            [
                (self.Close > Senkou_A) & (self.Close > Senkou_B),  # Bullish Cloud Crossover
                (self.Close < Senkou_A) & (self.Close < Senkou_B),  # Bearish Cloud Crossover
                (Tenkan > Kijun) & (Tenkan.shift(1) < Kijun.shift(1)),  # Bullish Tenkan/Kijun Crossover
                (Tenkan < Kijun) & (Tenkan.shift(1) > Kijun.shift(1)),  # Bearish Tenkan/Kijun Crossover
                (Chikou > self.Close),  # Bullish Chikou Span Crossover
                (Chikou < self.Close),  # Bearish Chikou Span Crossover
                (Senkou_A > Senkou_B),  # Bullish Senkou Span A/B Crossover
                (Senkou_A < Senkou_B),  # Bearish Senkou Span A/B Crossover
                (Senkou_A > Senkou_B) & (Senkou_A.shift(1) < Senkou_B.shift(1)),  # Bullish Kumo Twist
                (Senkou_A < Senkou_B) & (Senkou_A.shift(1) > Senkou_B.shift(1)),  # Bearish Kumo Twist
                (self.Close > Senkou_A) & (self.Close > Senkou_B),  # Bullish Cloud Breakout
                (self.Close < Senkou_A) & (self.Close < Senkou_B),  # Bearish Cloud Breakdown
                (self.Close < self.Close.shift(1)) & (Chikou > Chikou.shift(1)),  # Bullish Divergence
                (self.Close > self.Close.shift(1)) & (Chikou < Chikou.shift(1)),  # Bearish Divergence
                (Senkou_A > Senkou_A.shift(1)),  # Bullish Senkou Span A Slope
                (Senkou_A < Senkou_A.shift(1)),  # Bearish Senkou Span A Slope
                (Tenkan > Kijun) & (self.Close > Senkou_A) & (self.Close > Senkou_B),  # Bullish Crossover with Cloud
                (Tenkan < Kijun) & (self.Close < Senkou_A) & (self.Close < Senkou_B),  # Bearish Crossover with Cloud
                (self.Close > Senkou_A) & (self.Close > Senkou_B) & (Kijun > Senkou_A),  # Bullish Kijun/Cloud Confirmation
                (self.Close < Senkou_A) & (self.Close < Senkou_B) & (Kijun < Senkou_A),  # Bearish Kijun/Cloud Confirmation
                (Tenkan > Kijun) & (self.Close > Senkou_A) & (Senkou_A > Senkou_B),  # Bullish Kumo Squeeze
                (Tenkan < Kijun) & (self.Close < Senkou_A) & (Senkou_A < Senkou_B),  # Bearish Kumo Squeeze
                (Chikou > self.Close),  # Bullish Chikou Span
                (Chikou < self.Close),  # Bearish Chikou Span
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut")
        
        del Tenkan, Kijun, Senkou_A, Senkou_B, Chikou, combined_senkou_Max, combined_senkou_Min
        
        return {
            'chikou': chikou,
            'chikou_dir': chikou_dir
            }
    
    # FORCE_INDEX - Force Index
    # ----------------------------------------------------
    def Force_Index(self):
        
        Force_Index = (self.Close - self.Close.shift(1)) * self.Vol
        Force_Index_max_min = (self.High.combine(self.Low, max) - self.Low.combine(self.High, min)) * self.Vol
        Force_Index_MA = talib.SMA(Force_Index, timeperiod=self.period)
        
        FI_per = self._single_percentage(Force_Index)
        fi = FI_per
        fi_color = self._single_column_color(Force_Index)
        fi_mm = self._single_percentage(Force_Index_max_min)
        fi_mm_color = self._single_column_color(Force_Index_max_min)
        fi_dir = numpy.select(
            [
                (Force_Index > 0) & (Force_Index.shift(1) <= 0),  # Bullish crossover
                (Force_Index < 0) & (Force_Index.shift(1) >= 0),  # Bearish crossover
                (Force_Index_max_min > 0) & (Force_Index_max_min.shift(1) <= 0),  # Bullish Max/Min crossover
                (Force_Index_max_min < 0) & (Force_Index_max_min.shift(1) >= 0),  # Bearish Max/Min crossover
                (Force_Index > 0) & (Force_Index.shift(1) <= 0) & (Force_Index_max_min > 0),  # Bullish crossover with Max/Min confirmation
                (Force_Index < 0) & (Force_Index.shift(1) >= 0) & (Force_Index_max_min < 0),  # Bearish crossover with Max/Min confirmation
                (Force_Index > 0) & (Force_Index.shift(1) <= 0) & self.Vol > self.Vol.shift(1),  # Bullish with Volume
                (Force_Index < 0) & (Force_Index.shift(1) >= 0) & self.Vol > self.Vol.shift(1),  # Bearish with Volume
                (Force_Index > 0) & (Force_Index.shift(1) <= 0) & (Force_Index_max_min > 0) & self.Vol > self.Vol.shift(1),  # Bullish combo
                (Force_Index < 0) & (Force_Index.shift(1) >= 0) & (Force_Index_max_min < 0) & self.Vol > self.Vol.shift(1),  # Bearish combo
                (FI_per > 100) & (FI_per.shift(1) <= 100),    # Strong Bullish
                (FI_per < -100) & (FI_per.shift(1) >= -100),  # Strong Bearish
                (Force_Index > 0) & (Force_Index > Force_Index.shift(1)),  # Bullish momentum
                (Force_Index < 0) & (Force_Index < Force_Index.shift(1)),  # Bearish momentum
                (self.Close < self.Close.shift(1)) & (Force_Index > Force_Index.shift(1)),  # Price making lower lows, FI making higher lows
                (self.Close > self.Close.shift(1)) & (Force_Index < Force_Index.shift(1)),  # Price making higher highs, FI making lower highs
                (Force_Index > Force_Index_MA) & (Force_Index.shift(1) <= Force_Index_MA.shift(1)),  # Bullish crossover
                (Force_Index < Force_Index_MA) & (Force_Index.shift(1) >= Force_Index_MA.shift(1)),  # Bearish crossover
                (Force_Index > 0) & self.Vol > self.Vol.shift(1),     # Bullish FI with Volume Confirmation
                (Force_Index < 0) & self.Vol > self.Vol.shift(1),     # Bearish FI with Volume Confirmation
                (Force_Index > 0) & (self.RSI > 50),  # Bullish confirmation FI + self.RSI Uptrend
                (Force_Index < 0) & (self.RSI < 50),  # Bearish confirmation FI + self.RSI Downtrend
                (Force_Index > 0) & (self.MACD > self.MACD_signal),  # Bullish confirmation FI + self.MACD Uptrend
                (Force_Index < 0) & (self.MACD < self.MACD_signal),  # Bearish confirmation FI + self.MACD Downtrend
            ],
            ["call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put", "call", "put"],
            default="nut"
        )
        
        del Force_Index, Force_Index_max_min, Force_Index_MA
        
        return {
            'fi': fi.round(1),
            'fi_color': fi_color,
            'fi_mm': fi_mm.round(1),
            'fi_mm_color': fi_mm_color,
            'fi_dir': fi_dir
            }
    
    # RAIN_OSC - Rainbow Oscillator
    # ----------------------------------------------------
    def Rainbow_Oscillator(self):
        
        RAIN_OSC_Slope = self.rb.diff()
        
        rain_osc = self._single_percentage(self.rbo)
        rain_osc_color = self._single_column_color(self.rbo)
        rain_osc_lmt = self._single_percentage(self.rb)
        rain_osc_lmt_color = self._single_column_color(self.rb)
        rain_osc_dir = numpy.select(
            [
                (self.rb > 50) & (self.rb.shift(1) <= 50) & (self.ADX > 25) & (self.rbo > 0),  # Trend-following Buy
                (self.rb < 50) & (self.rb.shift(1) >= 50) & (self.ADX > 25) & (self.rbo < 0),  # Trend-following Sell
                (self.rb > 80) & (self.RSI > 70) & (self.rbo > 50),  # Overbought Condition
                (self.rb < 20) & (self.RSI < 30) & (self.rbo < -50),  # Oversold Condition
                (self.rb > self.rb.shift(1)) & (self.Close < self.Close.shift(1)) & (self.MACD > self.MACD_signal) & (self.rbo > 0),  # Bullish Divergence
                (self.rb < self.rb.shift(1)) & (self.Close > self.Close.shift(1)) & (self.MACD < self.MACD_signal) & (self.rbo < 0),  # Bearish Divergence
                (RAIN_OSC_Slope > 10) & (self.Close > self.Upper_BBand) & (self.rbo > 25),  # Breakout to Upside
                (RAIN_OSC_Slope < -10) & (self.Close < self.Lower_BBand) & (self.rbo < -25),  # Breakout to Downside
                (self.rb > 75) & (RAIN_OSC_Slope > 0) & (self.SMA50 > self.SMA200) & (self.rbo > 10),  # Strong Uptrend
                (self.rb < 25) & (RAIN_OSC_Slope < 0) & (self.SMA50 < self.SMA200) & (self.rbo < -10),  # Strong Downtrend
                (RAIN_OSC_Slope > 0) & (self.ADX > 20) & (self.rbo > 0),  # Momentum Increasing
                (RAIN_OSC_Slope < 0) & (self.ADX > 20) & (self.rbo < 0),  # Momentum Decreasing
                (self.rb.shift(1) < 0) & (self.rb > 0) & (self.MACD > self.MACD_signal) & (self.rbo > 0),  # Zero-Crossing Buy
                (self.rb.shift(1) > 0) & (self.rb < 0) & (self.MACD < self.MACD_signal) & (self.rbo < 0),  # Zero-Crossing Sell
                (RAIN_OSC_Slope.abs() > 10) & (self.ADX > 25) & (self.rbo.abs() > 20),  # Volatility Expansion
                (self.rb > 50) & (RAIN_OSC_Slope < 0) & (self.RSI < 50) & (self.rbo < 0),  # Pullback in Uptrend
                (self.rb < 50) & (RAIN_OSC_Slope > 0) & (self.RSI > 50) & (self.rbo > 0)  # Pullback in Downtrend
            ],
            ['call', 'put', 'put', 'call', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'put', 'call', 'call', 'put'],
            default='nut'
        )
        
        del RAIN_OSC_Slope
        
        return {
            'rain_osc': rain_osc.round(1),
            'rain_osc_color': rain_osc_color,
            'rain_osc_lmt': rain_osc_lmt.round(1),
            'rain_osc_lmt_color': rain_osc_lmt_color,
            'rain_osc_dir': rain_osc_dir
            }
    
    # CPATTERNS - group Patterns
    # ----------------------------------------------------
    def Patterns(self):
        
        # Detect self.groupstick Patterns Efficiently
        Pattern_Names = talib.get_function_groups()['Pattern Recognition']
        # Initialize a numpy array to store pattern results
        Pattern_Results = numpy.empty((len(self.group), len(Pattern_Names)), dtype=object)
        # Vectorized Pattern Detection
        for i, pattern in enumerate(Pattern_Names):
            pattern_values = getattr(talib, pattern)(self.Open, self.High, self.Low, self.Close)
            # Store results in the numpy array
            Pattern_Results[:, i] = [
                f"{pattern}-Bull" if val > 0 else f"{pattern}-Bear" if val < 0 else numpy.nan
                    for val in pattern_values
            ]
        # Pattern_Results = numpy.array([" | ".join([x for x in row if x != ""]) for row in numpy.array([["" if pandas.isna(x) else x for x in row] for row in Pattern_Results])])
        Pattern_Results = numpy.array([", ".join([x for x in row if pandas.notna(x)]) for row in Pattern_Results])
        
        pattern = Pattern_Results
        pattern_dir = numpy.select(
            [
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (self.RSI < 30),  # Bullish Engulfing + Oversold self.RSI
                (numpy.char.find(Pattern_Results, "CDLMORNINGSTAR-Bull") >= 0) & (self.MACD > self.MACD_signal),  # Morning Star + self.MACD Crossover
                (numpy.char.find(Pattern_Results, "CDLHAMMER-Bull") >= 0) & (self.Close < self.Lower_BBand),  # Hammer + Bollinger Lower Band
                (numpy.char.find(Pattern_Results, "CDLPIERCING-Bull") >= 0) & (self.Close > self.SMA50),  # Piercing Line + Above SMA50
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (self.RSI > 70),  # Bearish Engulfing + Overbought self.RSI
                (numpy.char.find(Pattern_Results, "CDLEVENINGSTAR-Bear") >= 0) & (self.MACD < self.MACD_signal),  # Evening Star + self.MACD Bearish Crossover
                (numpy.char.find(Pattern_Results, "CDLSHOOTINGSTAR-Bear") >= 0) & (self.Close > self.Upper_BBand),  # Shooting Star + Bollinger Upper Band
                (numpy.char.find(Pattern_Results, "CDLDARKCLOUDCOVER-Bear") >= 0) & (self.Close < self.SMA50),  # Dark Cloud Cover + Below SMA50
                (numpy.char.find(Pattern_Results, "CDLRISING3METHODS-Bull") >= 0),  # Rising Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bull") >= 0),  # Bullish Marubozu (Strong Uptrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bull") >= 0),  # Upside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLFALLING3METHODS-Bear") >= 0),  # Falling Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bear") >= 0),  # Bearish Marubozu (Strong Downtrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bear") >= 0),  # Downside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLDOJI") >= 0) & (self.ADX > 25),  # Doji with High ADX (Breakout Signal)
                (numpy.char.find(Pattern_Results, "CDLLONGLEGGEDDOJI") >= 0) & (self.ADX > 30),  # Long-Legged Doji with High ADX
                (numpy.char.find(Pattern_Results, "CDLSPINNINGTOP") >= 0) & (self.Vol > self.VOL_MA),  # Spinning Top with High Volume
                (numpy.char.find(Pattern_Results, "CDLHIGHWAVE") >= 0) & (self.Vol > self.VOL_MA),  # High-Wave self.group with High Volume
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (self.Close < self.Lower_BBand),  # Bullish Engulfing at Support
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (self.Close > self.Upper_BBand)   # Bearish Engulfing at Resistance
            ],
            ["call", "call", "call", "call",  # Bullish Reversals
            "put", "put", "put", "put",  # Bearish Reversals
            "call", "call", "call",  # Bullish Continuation
            "put", "put", "put",  # Bearish Continuation
            "call", "call", "call", "call",  # Breakout Patterns
            "call", "put"  # Support & Resistance Trades
            ],
            default='nut'
        )
        
        del Pattern_Names, pattern_values, Pattern_Results
        
        return {
            'pattern': pattern,
            'pattern_dir': pattern_dir
            }
    
    # MY Strategy
    # ----------------------------------------------------
    def Strategy(self):
        
        # Define conditions
        cond_outer = (abs(self.bop) > 3)
        cond_inner = (self.wup > 1) | (self.wlo > 1)
        g_upper = (self.bop > 0) & (self.wup > self.wlo) & (self.wup >= (self.wlo * 0.1))
        g_lower = (self.bop > 0) & (self.wup < self.wlo) & (self.wlo >= (self.wup * 0.1))
        r_upper = (self.bop < 0) & (self.wup > self.wlo) & (self.wup >= (self.wlo * 0.1))
        r_lower = (self.bop < 0) & (self.wup < self.wlo) & (self.wlo >= (self.wup * 0.1))
        mad_p_g = ((self.MAD > 0) & (self.MAD_color == 'g'))
        mad_p_r = ((self.MAD > 0) & (self.MAD_color == 'r'))
        mad_n_g = ((self.MAD < 0) & (self.MAD_color == 'g'))
        mad_n_r = ((self.MAD < 0) & (self.MAD_color == 'r'))
        
        Greater_upper = self.Gator_UPPER > self.Gator_LOWER
        Greater_lower = self.Gator_UPPER <= self.Gator_LOWER
        
        rbo_cond = (self.rbo >= (self.rb * 0.15)) & (self.rbo <= (self.rb * 0.85)) | (self.rbo >= (self.rb * 1.2)) & (self.rbo <= (self.rb * 1.8))
        GATOR_g_g = (self.Gator_UPPER_color == 'g') & (self.Gator_LOWER_color == 'g')
        GATOR_r_g = (self.Gator_UPPER_color == 'r') & (self.Gator_LOWER_color == 'g')
        GATOR_r_r = (self.Gator_UPPER_color == 'r') & (self.Gator_LOWER_color == 'r')
        GATOR_g_r = (self.Gator_UPPER_color == 'g') & (self.Gator_LOWER_color == 'r')
        Gator_g_RB_h = (self.Gator_UPPER_color == 'g') & (self.rbo > 0)
        Gator_r_RB_h = (self.Gator_UPPER_color == 'r') & (self.rbo > 0)
        Gator_g_RB_l = (self.Gator_UPPER_color == 'g') & (self.rbo < 0)
        Gator_r_RB_l = (self.Gator_UPPER_color == 'r') & (self.rbo < 0)
        Gator_upper_80 = (self.Gator_UPPER >= (self.Gator_LOWER * 0.8))
        Gator_upper_70 = (self.Gator_UPPER >= (self.Gator_LOWER * 0.7))
        Gator_lower_90 = (self.Gator_LOWER >= (self.Gator_UPPER * 0.9))
        Gator_lower_80 = (self.Gator_LOWER >= (self.Gator_UPPER * 0.8))
        Gator_Upper_90_80 = (self.Gator_UPPER >= (self.Gator_LOWER * 0.9)) | (self.Gator_UPPER >= (self.Gator_LOWER * 0.8))
        Gator_Lower_90_80 = (self.Gator_LOWER >= (self.Gator_UPPER * 0.9)) | (self.Gator_LOWER >= (self.Gator_UPPER * 0.8))
        Gator_Upper_80_70 = (self.Gator_UPPER >= (self.Gator_LOWER * 0.8)) | (self.Gator_UPPER >= (self.Gator_LOWER * 0.7))
        Gator_Lower_80_70 = (self.Gator_LOWER >= (self.Gator_UPPER * 0.8)) | (self.Gator_LOWER >= (self.Gator_UPPER * 0.7))
        
        GATOR_UPPER_div_1 = talib.DIV(abs(self.Gator_UPPER), talib.MAX(abs(self.Gator_UPPER), timeperiod=11)) * 100 >= 5
        GATOR_LOWER_div_1 = talib.DIV(abs(self.Gator_LOWER), talib.MAX(abs(self.Gator_LOWER), timeperiod=11)) * 100 >= 5
        
        MTD = numpy.where(cond_outer,
            numpy.where(cond_inner,
                numpy.select([g_upper, g_lower, r_upper, r_lower],
                    [
                        numpy.select([mad_p_g, mad_n_g, mad_p_r, mad_n_r], ['put', 'call', 'call', 'put'], 'nut'),
                        numpy.select([mad_p_g, mad_n_g, mad_p_r, mad_n_r], ['call', 'put', 'put', 'call'], 'nut'),
                        numpy.select([mad_p_g, mad_n_g, mad_p_r, mad_n_r], ['put', 'call', 'call', 'put'], 'nut'),
                        numpy.select([mad_p_g, mad_n_g, mad_p_r, mad_n_r], ['call', 'put', 'put', 'call'], 'nut')
                    ], 'nut'
                ), 'nut'
            ), 'nut'
        )
        
        MTD_Conversion = numpy.select([(MTD == 'call'), (MTD == 'put')], ['put', 'call'], 'nut')
        
        GTD = numpy.where(
            (MTD != 'nut'),
            numpy.where(
                ((self.Gator_UPPER > 0) & (self.Gator_LOWER > 0)) | ((self.Gator_UPPER < 0) & (self.Gator_LOWER < 0)),
                numpy.where(GATOR_UPPER_div_1 & GATOR_LOWER_div_1,
                    numpy.select(
                        [GATOR_g_g, GATOR_r_g, GATOR_r_r, GATOR_g_r],
                        [
                            numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_lower_90, MTD_Conversion, MTD), numpy.where(Gator_upper_80, MTD_Conversion, MTD)], MTD),
                            numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_lower_80, MTD_Conversion, MTD), numpy.where(Gator_upper_70, MTD_Conversion, MTD)], MTD),
                            numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_lower_90, MTD, MTD_Conversion), numpy.where(Gator_upper_80, MTD, MTD_Conversion)], MTD_Conversion),
                            numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_lower_80, MTD, MTD_Conversion), numpy.where(Gator_upper_70, MTD, MTD_Conversion)], MTD_Conversion)
                        ], 'nut'
                    ), 'nut'
                ), 'nut'
            ), MTD
        )
        
        GTD_Conversion = numpy.select([(GTD == 'call'), (GTD == 'put')], ['put', 'call'], 'nut')
        Cond = numpy.select([(self.rbo > 0), (self.rbo < 0)], [numpy.where(rbo_cond, GTD, GTD_Conversion), numpy.where(rbo_cond, GTD_Conversion, GTD)], GTD_Conversion)

        RTD = numpy.where(
            (GTD != 'nut'),
            numpy.select(
                [GATOR_g_g, GATOR_r_g, GATOR_r_r, GATOR_g_r],
                [
                    numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_Lower_90_80, GTD, Cond), numpy.where(Gator_Upper_90_80, GTD, Cond)], Cond),
                    numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_Lower_80_70, GTD, Cond), numpy.where(Gator_Upper_80_70, GTD, Cond)], Cond),
                    numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_Lower_90_80, GTD, Cond), numpy.where(Gator_Upper_90_80, GTD, Cond)], Cond),
                    numpy.select([Greater_upper, Greater_lower], [numpy.where(Gator_Lower_80_70, GTD, Cond), numpy.where(Gator_Upper_80_70, GTD, Cond)], Cond)
                ], 'nut'
            ), GTD
        )
        
        Time = (5 * (abs((abs(self.Gator_UPPER) - abs(self.Gator_LOWER)) / (abs(self.Gator_UPPER) + abs(self.Gator_LOWER)).mean()) % 1)).round(0)
        
        Timing = numpy.select(
                [Greater_upper, Greater_lower],
                [
                    numpy.select([Gator_g_RB_h | Gator_r_RB_l, Gator_g_RB_l | Gator_r_RB_h], [(15 + 5 - Time), (15 + 9 + Time)]),
                    numpy.select([Gator_g_RB_h | Gator_r_RB_l, Gator_g_RB_l | Gator_r_RB_h], [(15 + 9 + Time), (15 + 5 - Time)])
                ], numpy.select([Gator_g_RB_h | Gator_r_RB_l, Gator_g_RB_l | Gator_r_RB_h], [(15 + 5 - Time), (15 + 9 + Time)])
        )
        
        Trade_time = numpy.where(Timing != 0, self.To + Timing, 0)
        
        #self.group['MTD'] = MTD
        #self.group['GTD'] = GTD
        #self.group['RTD'] = RTD
        #self.group['Timing'] = Timing
        
        del cond_outer, cond_inner, g_upper, g_lower, r_upper, r_lower, mad_p_g, mad_p_r, mad_n_g, mad_n_r, Greater_upper, Greater_lower, rbo_cond, GATOR_g_g, GATOR_r_g, GATOR_r_r, GATOR_g_r, Gator_g_RB_h, Gator_r_RB_h, Gator_g_RB_l, Gator_r_RB_l, Gator_upper_80, Gator_upper_70, Gator_lower_90, Gator_lower_80, Gator_Upper_90_80, Gator_Lower_90_80, Gator_Upper_80_70, Gator_Lower_80_70, GATOR_UPPER_div_1, GATOR_LOWER_div_1, Time, MTD_Conversion, GTD_Conversion, Cond
        
        return {
            'MTD': MTD,
            'GTD': GTD,
            'RTD': RTD,
            'Timing': Timing,
            'Trade_time': Trade_time
            }
    
    # Common Direction
    # ----------------------------------------------------
    def Common_Direction(self):
            # Step 1: Collect columns ending with '_dir' and ('MTD', 'GTD', 'RTD')
            dir_columns = [col for col in self.group.columns if col.endswith('_dir')]
            dir_columns.extend(['MTD', 'GTD', 'RTD'])
            
            # Step 2: Find the most common value for each row across these columns
            self.group['common_dir'] = self.group[dir_columns].mode(axis=1)[0]
            
            # Step 3: Collect columns ('MTD', 'GTD', 'RTD', 'common_dir')
            final_common_cols = ['MTD', 'GTD', 'RTD', 'common_dir']
            
            # Step 4: Find the most common value for each row across these columns
            self.group['final_common_dir'] = self.group[final_common_cols].mode(axis=1)[0]
            
            # Step 5: Collect columns ('RTD', 'common_dir', 'final_common_dir')
            semi_final_dir_cols = ['RTD', 'common_dir', 'final_common_dir']
            
            # Step 6: Find the most common value for each row across these columns
            self.group['semi_final_dir'] = self.group[semi_final_dir_cols].mode(axis=1)[0]
            
            # Step 7: Collect columns ('RTD', 'common_dir', 'final_common_dir', 'semi_final_dir')
            final_dir_cols = ['RTD', 'common_dir', 'final_common_dir', 'semi_final_dir']
            
            # Step 8: Find the most common value for each row across these columns
            self.group['final_dir'] = self.group[final_dir_cols].mode(axis=1)[0]

    
    def run(self):
        
        # Get all methods in the class (excluding private methods and 'run')
        Functions = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith('_') and method not in ['run', 'Common_Direction']]
        
        results = {}
        for function_name in Functions:
            function = getattr(self, function_name)
            result = function()  # Call the method
            results.update(result)
        
        indic = pandas.DataFrame(results)
        
        # Concatenate all results with the original DataFrame
        self.group = pandas.concat([self.group, indic], ignore_index=False, axis=1)
        self.Common_Direction()
        
        return self.group  # Return the updated DataFrame
        