from MH_libraries import talib, numpy, pandas, threading, gc
import logging

class Indicator_Signals():
    
    def __init__(self, df):
        self.df = df
        self.Open = self.df['open'].astype(float)
        self.High = self.df['max'].astype(float)
        self.Low = self.df['min'].astype(float)
        self.Close = self.df['close'].astype(float)
        self.Volume = self.df['volume'].astype(float)
        self.To = self.df['to'].astype(float)
        self.AVGPRICE = talib.AVGPRICE(self.Open, self.High, self.Low, self.Close)
        self.strategies_list = {}
        self._strategy_lock = threading.Lock()
        self.final_list = []
        self._final_lock = threading.Lock()
        self._strategy_methods = self._get_strategy_methods()
        self._threads = []  # Stores active threads

    def run(self) -> None:
        # Clear previous threads if any
        self._threads.clear()

        # Start a thread for each strategy
        for method_name in self._strategy_methods:
            thread = threading.Thread(target=getattr(self, method_name))
            thread.start()
            self._threads.append(thread)

        # Wait for all threads to complete
        while self._threads:
            thread = self._threads.pop()  # Remove thread from list
            if thread.is_alive():  # Only join if still running
                thread.join()  # Wait for completion
            del thread

        strategy = pandas.DataFrame(self.strategies_list)
        strategy.dropna(axis=1, inplace=True)
        strategy['final_dir'] = strategy.mode(axis=1)[0]
        strategy.loc[(strategy['final_dir'] == 'nan'), 'final_dir'] = strategy['RTD_dir']
        final_list = pandas.concat(self.final_list, axis=1)
        final_list = pandas.concat([final_list, strategy], axis=1)

        # Get all attributes set in __init__
        init_attrs = list(self.__dict__.keys())
        # Delete them dynamically
        for attr in init_attrs:
            delattr(self, attr)
        gc.collect()

        return final_list

    def _get_strategy_methods(self):
        """Identify strategy methods at init (cached for speed)."""
        return [
            method for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith('_')
            and method not in ['run']
        ]

    def _add_strategy(self, indicator_name, signal_series):
        
        with self._strategy_lock:  # Thread-safe update
            self.strategies_list[f'{indicator_name}_dir'] = signal_series

    def _assign_color_labels(self, df: pandas.DataFrame, columns:list, suffix='_color', default='n'):
        shifted = df[columns].shift(1)

        # Vectorized approach to assign labels
        gt = df[columns] > shifted  # 'g' for greater
        lt = df[columns] < shifted  # 'r' for lesser
        eq = df[columns] == shifted  # 'n' for equal

        # Assign 'g' where greater, 'r' where lesser, and 'n' where equal
        labels = numpy.select([gt, lt, eq], ['g', 'r', default], default=default)

        # Create the DataFrame for the labels
        label_df = pandas.DataFrame(
            {f"{col}{suffix}": labels[:, i] for i, col in enumerate(columns)},
            index=df.index
        )

        # Drop columns where all values are 'n'
        label_df = label_df.loc[:, ~(label_df == 'n').all()]

        # Add the label DataFrame to the results
        with self._final_lock:  # Thread-safe update
            self.final_list.append(label_df)

    def _adjust_decimal_precision(self, df: pandas.DataFrame, columns: list) -> pandas.DataFrame:
        # List to store adjusted columns
        adjusted_columns = []

        # Loop through each column in the list of columns
        for col in columns:
            if col in df.columns:
                # Get the non-zero values of the column
                non_zero = df[col][(df[col] != 0) & (~df[col].isna())].astype(float)
                
                if non_zero.empty:
                    adjusted_columns.append(df[col])  # No scaling required for this column
                    continue
                
                # Get the minimum absolute value in the column
                max_value = non_zero.abs().max()
                
                # Calculate the scaling factor based on the number of leading zeros in the fractional part
                log10_max_value = numpy.log10(max_value)
                leading_zeros = numpy.floor(-log10_max_value).astype(int)
                scale_factor = 10 ** abs(leading_zeros)
                
                # Scale the entire column by the calculated factor and add it to the list
                adjusted_columns.append(df[col] * scale_factor)
        
        # Create a new DataFrame with adjusted columns
        adjusted_columns = pandas.concat(adjusted_columns, axis=1)
        
        # Set the column names to match the original DataFrame
        adjusted_columns.columns = columns
        
        adjusted_columns = numpy.sign(adjusted_columns) * (adjusted_columns - numpy.floor(adjusted_columns))  # changing number before decimal to zero
        
        return adjusted_columns

    def Strategy(self):
        
        if 'BOP' in self.df.columns:
            BOP = self.df['BOP'] * 100
        else:
            BOP = talib.BOP(self.Open, self.High, self.Low, self.Close) * 100
        if all(col in self.df.columns for col in ['wick_up', 'wick_low']):
            wick_up = self.df['wick_up']
            wick_low = self.df['wick_low']
        else:
            wick_up = numpy.where(BOP < 0, (talib.BOP(self.Open, self.High, self.Low, self.High) * 100), (talib.BOP(self.Close, self.High, self.Low, self.High) * 100))
            wick_low = numpy.where(BOP < 0, (talib.BOP(self.Low, self.High, self.Low, self.Close) * 100), (talib.BOP(self.Low, self.High, self.Low, self.Open) * 100))
        if 'MAD' in self.df.columns:
            MAD = self.df['MAD']
        else:
            if 'EMA' in self.df.columns:
                EMA = self.df['EMA']
                MAD = self.AVGPRICE - EMA
            else:
                EMA = talib.EMA(self.AVGPRICE, timeperiod=11)
                MAD = self.AVGPRICE - EMA
        if all(col in self.df.columns for col in ['Gator_UPPER', 'Gator_LOWER']):
            Gator_UPPER = self.df['Gator_UPPER']
            Gator_LOWER = self.df['Gator_LOWER']
        else:
            Gator_JAW = talib.WMA(self.AVGPRICE, timeperiod=11).shift(6)
            Gator_TEETH = talib.WMA(self.AVGPRICE, timeperiod=6).shift(3) 
            Gator_LIPS = talib.WMA(self.AVGPRICE, timeperiod=3).shift(1)
            Gator_UPPER = abs(Gator_JAW - Gator_TEETH )
            Gator_LOWER = abs(Gator_TEETH - Gator_LIPS )
        if all(col in self.df.columns for col in ['rb', 'rbo']):
            rb = self.df['rb']
            rbo = self.df['rbo']
        else:
            ma_list = [EMA]
            for i in range(0, 10):  # 10 EMAs in total
                ma_list.append(talib.EMA(ma_list[i - 1], timeperiod=11))
            ma_stack_df = pandas.concat(ma_list, axis=1)  # Stack the EMAs into a DataFrame
            hh, ll = talib.MAX(self.AVGPRICE, 11), talib.MIN(self.AVGPRICE, 11)
            rb = 100 * (ma_stack_df.max(axis=1) - ma_stack_df.min(axis=1)) / (hh - ll)
            rbo = 100 * (self.AVGPRICE - ma_stack_df.mean(axis=1)) / (hh - ll)

        MAD_shift = MAD.shift(1)
        MAD_color = numpy.select([MAD > MAD_shift, MAD < MAD_shift, MAD == MAD_shift], ['g', 'r', 'n'], default='n')
        Gator_UPPER_color = numpy.select([Gator_UPPER > Gator_UPPER.shift(1), Gator_UPPER < Gator_UPPER.shift(1), Gator_UPPER == Gator_UPPER.shift(1)], ['g', 'r', 'n'], default='n')
        Gator_LOWER_color = numpy.select([Gator_LOWER > Gator_LOWER.shift(1), Gator_LOWER < Gator_LOWER.shift(1), Gator_LOWER == Gator_LOWER.shift(1)], ['g', 'r', 'n'], default='n')
        RBO_color = numpy.select([rbo > rbo.shift(1), rbo < rbo.shift(1), rbo == rbo.shift(1)], ['g', 'r', 'n'], default='n')

        # Define conditions
        G_Candl = (BOP > 100) & (abs(BOP) > 7)
        R_Candl = (BOP < 100) & (abs(BOP) > 7)
        U_Wick = wick_up >= (wick_low * 1.1)
        L_Wick = wick_low >= (wick_up * 1.1)
        P_G_MAD = ((MAD_color == 'g') & (MAD > 0))
        N_G_MAD = ((MAD_color == 'g') & (MAD < 0))
        P_R_MAD = ((MAD_color == 'r') & (MAD > 0))
        N_R_MAD = ((MAD_color == 'r') & (MAD < 0))
        
        put_condition = ((G_Candl | R_Candl) & (U_Wick & P_G_MAD)) | \
                        ((G_Candl | R_Candl) & (L_Wick & N_G_MAD)) | \
                        ((G_Candl | R_Candl) & (U_Wick & N_R_MAD)) | \
                        ((G_Candl | R_Candl) & (L_Wick & P_R_MAD))

        call_condition = ((G_Candl | R_Candl) & (U_Wick & N_G_MAD)) | \
                        ((G_Candl | R_Candl) & (L_Wick & P_G_MAD)) | \
                        ((G_Candl | R_Candl) & (U_Wick & P_R_MAD)) | \
                        ((G_Candl | R_Candl) & (L_Wick & N_R_MAD))
        MTD = numpy.select([put_condition, call_condition], ['put', 'call'], default=numpy.nan)
        MTD_Reversal = numpy.select([(MTD == 'call'), (MTD == 'put')], ['put', 'call'], default=numpy.nan)

        G_G_Gator = ((Gator_UPPER_color == 'g') & (Gator_LOWER_color == 'g'))
        R_R_Gator = ((Gator_UPPER_color == 'r') & (Gator_LOWER_color == 'r'))
        G_R_Gator = ((Gator_UPPER_color == 'g') & (Gator_LOWER_color == 'r'))
        R_G_Gator = ((Gator_UPPER_color == 'r') & (Gator_LOWER_color == 'g'))
        G_G_UPP_Gator = (G_G_Gator & (Gator_UPPER >= (Gator_LOWER * 1.9)))
        G_G_LOW_Gator = (G_G_Gator & (Gator_LOWER >= (Gator_UPPER * 1.8)))
        R_R_UPP_Gator = (R_R_Gator & (Gator_UPPER >= (Gator_LOWER * 1.9)))
        R_R_LOW_Gator = (R_R_Gator & (Gator_LOWER >= (Gator_UPPER * 1.8)))
        G_R_UPP_Gator = (G_R_Gator & (Gator_UPPER >= (Gator_LOWER * 1.8)))
        G_R_LOW_Gator = (G_R_Gator & (Gator_LOWER >= (Gator_UPPER * 1.7)))
        R_G_UPP_Gator = (R_G_Gator & (Gator_UPPER >= (Gator_LOWER * 1.8)))
        R_G_LOW_Gator = (R_G_Gator & (Gator_LOWER >= (Gator_UPPER * 1.7)))
        
        conditions = [
            ((rbo > 0) & G_G_Gator),  # First condition
            ((rbo > 0) & R_R_Gator),  # Second condition
            ((rbo > 0) & G_R_Gator),  # Third condition
            ((rbo > 0) & R_G_Gator),  # Fourth condition
            ((rbo < 0) & G_G_Gator),
            ((rbo < 0) & R_R_Gator),
            ((rbo < 0) & G_R_Gator),
            ((rbo < 0) & R_G_Gator)
        ]
        # Corresponding results for each condition
        choices = [
            numpy.where(G_G_UPP_Gator & G_G_LOW_Gator, MTD_Reversal, MTD),
            numpy.where(R_R_UPP_Gator & R_R_LOW_Gator, MTD, MTD_Reversal),
            numpy.where(G_R_UPP_Gator & G_R_LOW_Gator, MTD, MTD_Reversal),
            numpy.where(R_G_UPP_Gator & R_G_LOW_Gator, MTD_Reversal, MTD),
            numpy.where(G_G_UPP_Gator & G_G_LOW_Gator, MTD, MTD_Reversal),
            numpy.where(R_R_UPP_Gator & R_R_LOW_Gator, MTD_Reversal, MTD),
            numpy.where(G_R_UPP_Gator & G_R_LOW_Gator, MTD_Reversal, MTD),
            numpy.where(R_G_UPP_Gator & R_G_LOW_Gator, MTD, MTD_Reversal)
        ]
        GTD = numpy.select(conditions, choices, default=numpy.nan)
        GTD_Reversal = numpy.select([(GTD == 'call'), (GTD == 'put')], ['put', 'call'], default=numpy.nan)

        rain = ((abs(rbo) - abs(rb)) / (abs(rbo) + abs(rb))) * 100
        RTD = numpy.where((((rain >= 20) & (rain <= 80)) | ((rain >= 120) & (rain <= 180))),
                numpy.where((rb > 0), GTD, GTD_Reversal),
                numpy.where((rb > 0), GTD_Reversal, GTD)
        )

        GR_UPP_Gator = (Gator_UPPER > Gator_LOWER)
        GR_LOW_Gator = (Gator_UPPER < Gator_LOWER)
        P_G_RAIN = (rbo > 0) & (RBO_color == 'g')
        P_R_RAIN = (rbo > 0) & (RBO_color == 'r')
        N_G_RAIN = (rbo < 0) & (RBO_color == 'g')
        N_R_RAIN = (rbo < 0) & (RBO_color == 'r')

        Time = (3 * (abs((abs(Gator_UPPER) - abs(Gator_LOWER)) / (abs(Gator_UPPER) + abs(Gator_LOWER)).mean()) % 1)).round(2)
        time_ab = (15 + 9 + Time)
        time_lo = (15 + 5 - Time)

        Timing = numpy.select(
            [
                (GR_LOW_Gator | GR_UPP_Gator) & (P_G_RAIN & (Gator_UPPER_color == 'g')),
                (GR_LOW_Gator | GR_UPP_Gator) & (P_G_RAIN & (Gator_UPPER_color == 'r')),
                (GR_LOW_Gator | GR_UPP_Gator) & (P_R_RAIN & (Gator_UPPER_color == 'g')),
                (GR_LOW_Gator | GR_UPP_Gator) & (P_R_RAIN & (Gator_UPPER_color == 'r')),
                (GR_LOW_Gator | GR_UPP_Gator) & (N_G_RAIN & (Gator_UPPER_color == 'g')),
                (GR_LOW_Gator | GR_UPP_Gator) & (N_G_RAIN & (Gator_UPPER_color == 'r')),
                (GR_LOW_Gator | GR_UPP_Gator) & (N_R_RAIN & (Gator_UPPER_color == 'g')),
                (GR_LOW_Gator | GR_UPP_Gator) & (N_R_RAIN & (Gator_UPPER_color == 'r')),
            ],
            [
                time_lo,
                time_ab,
                time_ab,
                time_lo,
                time_ab,
                time_lo,
                time_lo,
                time_ab,
            ],
            default=numpy.nan
        )
        
        Trade_time = numpy.where(Timing != 0, self.To + Timing, 0)
        
        self._add_strategy('RTD', RTD)
        with self._final_lock:  # Thread-safe update
            self.final_list.append(pandas.DataFrame(Timing, columns=["Timing"]))
            self.final_list.append(pandas.DataFrame(Trade_time, columns=["Trade_time"]))
        return

    def Patterns(self):
        
        VOL_MA = talib.EMA(self.Volume, timeperiod=11)
        if 'RSI' in self.df.columns:
            RSI = self.df['RSI']
        else:
            RSI = talib.RSI(self.AVGPRICE, timeperiod=11)
        if all(col in self.df.columns for col in ['MACD_0', 'MACD_1']):
            MACD = self.df['MACD_0']
            MACD_signal = self.df['MACD_1']
        else:
            MACD, MACD_signal, _ = talib.MACD(self.AVGPRICE, fastperiod=11, slowperiod=11*2, signalperiod=9)
        if all(col in self.df.columns for col in ['BBANDS_0', 'BBANDS_2']):
            Upper_BBand = self.df['BBANDS_0']
            Lower_BBand = self.df['BBANDS_2']
        else:
            Upper_BBand, _, Lower_BBand = talib.BBANDS(self.AVGPRICE, timeperiod=11, nbdevup=2, nbdevdn=2, matype=2)
        if 'EMA' in self.df.columns:
            EMA = self.df['EMA']
        else:
            EMA = talib.EMA(self.AVGPRICE, timeperiod=11)
        if 'ADX' in self.df.columns:
            ADX = self.df['ADX']
        else:
            ADX = talib.ADX(self.High, self.Low, self.AVGPRICE, timeperiod=11)

        # Detect group stick Patterns Efficiently
        Pattern_Names = talib.get_function_groups()['Pattern Recognition']
        
        # Initialize a numpy array to store pattern results
        Pattern_Results = numpy.empty((len(self.df), len(Pattern_Names)), dtype=object)
        
        # Vectorized Pattern Detection
        for i, pattern in enumerate(Pattern_Names):
            pattern_values = getattr(talib, pattern)(self.Open, self.High, self.Low, self.Close)
            # Store results in the numpy array
            Pattern_Results[:, i] = numpy.where(pattern_values > 0, f"{pattern}-Bull",
                                                numpy.where(pattern_values < 0, f"{pattern}-Bear", None))
        
        Pattern_Results = [
            ", ".join([x for x in row if isinstance(x, str) and pandas.notna(x)]) or numpy.nan
            for row in Pattern_Results
        ]
    
        # Define pattern directions based on specific criteria
        pattern_dir = numpy.select(
            [
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (RSI < 30),  # Bullish Engulfing + Oversold RSI
                (numpy.char.find(Pattern_Results, "CDLMORNINGSTAR-Bull") >= 0) & (MACD > MACD_signal),  # Morning Star + MACD Crossover
                (numpy.char.find(Pattern_Results, "CDLHAMMER-Bull") >= 0) & (self.Close < Lower_BBand),  # Hammer + Bollinger Lower Band
                (numpy.char.find(Pattern_Results, "CDLPIERCING-Bull") >= 0) & (self.Close > EMA),  # Piercing Line + Above EMA
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (RSI > 70),  # Bearish Engulfing + Overbought RSI
                (numpy.char.find(Pattern_Results, "CDLEVENINGSTAR-Bear") >= 0) & (MACD < MACD_signal),  # Evening Star + MACD Bearish Crossover
                (numpy.char.find(Pattern_Results, "CDLSHOOTINGSTAR-Bear") >= 0) & (self.Close > Upper_BBand),  # Shooting Star + Bollinger Upper Band
                (numpy.char.find(Pattern_Results, "CDLDARKCLOUDCOVER-Bear") >= 0) & (self.Close < EMA),  # Dark Cloud Cover + Below EMA
                (numpy.char.find(Pattern_Results, "CDLRISING3METHODS-Bull") >= 0),  # Rising Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bull") >= 0),  # Bullish Marubozu (Strong Uptrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bull") >= 0),  # Upside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLFALLING3METHODS-Bear") >= 0),  # Falling Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bear") >= 0),  # Bearish Marubozu (Strong Downtrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bear") >= 0),  # Downside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLDOJI") >= 0) & (ADX > 25),  # Doji with High ADX (Breakout Signal)
                (numpy.char.find(Pattern_Results, "CDLLONGLEGGEDDOJI") >= 0) & (ADX > 30),  # Long-Legged Doji with High ADX
                (numpy.char.find(Pattern_Results, "CDLSPINNINGTOP") >= 0) & (self.Volume > VOL_MA),  # Spinning Top with High Volume
                (numpy.char.find(Pattern_Results, "CDLHIGHWAVE") >= 0) & (self.Volume > VOL_MA),  # High-Wave Pattern with High Volume
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (self.Close < Lower_BBand),  # Bullish Engulfing at Support
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (self.Close > Upper_BBand)   # Bearish Engulfing at Resistance
            ],
            ["call", "call", "call", "call",  # Bullish Reversals
            "put", "put", "put", "put",  # Bearish Reversals
            "call", "call", "call",  # Bullish Continuation
            "put", "put", "put",  # Bearish Continuation
            "call", "call", "call", "call",  # Breakout Patterns
            "call", "put"  # Support & Resistance Trades
            ],
            default=numpy.nan
        )
        
        self._add_strategy('pattern', pattern_dir)
        with self._final_lock:  # Thread-safe update
            self.final_list.append(pandas.DataFrame(Pattern_Results, columns=["pattern"]))
        return

    def Vectorizing(self):
        
        AVG = [
            'BBANDS_0', 'BBANDS_1', 'BBANDS_2', 'Chimoku', 'DEMA', 'EMA', 'Gator_JAW', 'Gator_LIPS', 'Gator_TEETH', 'KAMA', 'KST', 'KST_Signal', 'Kijun', 'MA', 'MAMA_0', 'MAMA_1', 'MEDPRICE', 'MIDPOINT', 'MIDPRICE', 
            'SAR', 'SAREXT', 'Senkou_A', 'Senkou_B', 'T3', 'TEMA', 'TRIMA', 'TYPPRICE', 'Tenkan', 'WCLPRICE', 'WMA', 'combined_senkou_Max', 'combined_senkou_Min', 
            'donchian_lower', 'donchian_middle', 'donchian_upper', 'envelope_lower', 'envelope_middle', 'envelope_upper', 'keltner_lower', 'keltner_upper'
        ]
        narrow_zeros = [
            'ACO', 'APO', 'ATR', 'AWO', 'Bear_Power', 'Bull_Power', 'Coppock_Curve', 'Gator_Expansion', 'Gator_LOWER', 'Gator_UPPER', 'HMA', 'HPR', 'HT_PHASOR_0', 'HT_PHASOR_1', 
            'HT_SINE_0', 'HT_SINE_1', 'HT_TRENDLINE', 'HT_TRENDMODE', 'HV', 'MACDEXT_0', 'MACDEXT_1', 'MACDEXT_2', 'MACDFIX_0', 'MACDFIX_1', 'MACDFIX_2', 'MACD_0', 'MACD_1', 'MACD_2', 
            'MAD', 'MAD_lower', 'MAD_upper', 'MFM', 'MFVCoppock_Raw', 'MINUS_DM', 'MOM', 'NATR', 'PLUS_DM', 'PPO', 'ROC', 'ROCP', 'TRANGE', 'TRIX', 'donchian_channel', 'ketlner_channel'
        ]
        round1 = [
            'AD', 'ADL', 'ADOSC', 'ADX', 'ADXR', 'AROONOSC', 'AROON_0', 'AROON_1', 'CCI', 'CMO', 'CO', 'CO_Fast', 'CO_Slow', 'DX', 
            'Force_Index', 'Force_Index_MA', 'Force_Index_max_min', 'HSI', 'HT_DCPERIOD', 'HT_DCPHASE', 'MFI', 'MINUS_DI', 'PLUS_DI', 'RSI', 'STOCHF_0', 'STOCHF_1', 
            'STOCHRSI_0', 'STOCHRSI_1', 'STOCH_0', 'STOCH_1', 'TSI', 'TSI_signal', 'ULTOSC', 'WILLR', 'WRSI', 'WRSI_MA', 'WRSI_Overbought', 'WRSI_Oversold', 'rb', 'rb_slope', 'rbo', 'wick_low', 'wick_up'
        ]
        exceed_100 = ['AD', 'ADL', 'ADOSC', 'CCI', 'CO_Fast', 'CO_Slow', 'rb', 'rbo', 'CO']
        AVG = [col for col in AVG if col in self.df.columns]
        narrow_zeros = [col for col in narrow_zeros if col in self.df.columns]
        multiply_hundred = [col for col in ['BOP', 'ROCR100', 'OBV', 'OBV_high', 'OBV_low'] if col in self.df.columns]
        round1 = [col for col in round1 if col in self.df.columns]
        color = [col for col in ['AVGPRICE', 'Force_Index_max_min'] if col in self.df.columns]

        self._assign_color_labels(df=self.df, columns=AVG, suffix='_LL_color')

        diffs = self.df[AVG].subtract(self.AVGPRICE, axis=0)

        diffs = pandas.concat([diffs, self.df[narrow_zeros]], axis=1)
        diffs = self._adjust_decimal_precision(diffs, columns=diffs.columns)

        to_concat = {}
        if 'ROCR100' in multiply_hundred:
            to_concat['ROCR100'] = self.df['ROCR100'] - 100
        if 'OBV' in multiply_hundred:
            to_concat['OBV'] = self.df['OBV'] / self.Volume / 10
        if 'OBV_high' in multiply_hundred:
            to_concat['OBV_high'] = self.df['OBV_high'] / self.Volume / 10
        if 'OBV_low' in multiply_hundred:
            to_concat['OBV_low'] = self.df['OBV_low'] / self.Volume / 10
        if 'BOP' in multiply_hundred:
            to_concat['BOP'] = self.df['BOP']
        if to_concat:  # only concat if not empty
            diffs = pandas.concat([diffs, pandas.DataFrame(to_concat)], axis=1) * 100
        
        # Concatenate the 'round1' columns into the 'diffs' DataFrame
        diffs = pandas.concat([diffs, self.df[round1]], axis=1, ignore_index=False)
        exceed_100 = [col for col in exceed_100 if col in diffs.columns]
        diffs[exceed_100] = diffs[exceed_100] / 10

        color_df = pandas.concat([diffs, self.df[color]], axis=1, ignore_index=False)
        self._assign_color_labels(df=color_df, columns=color_df.columns)

        diffs = diffs.round(1)

        with self._final_lock:  # Thread-safe update
            self.final_list.append(diffs)
        return

    def ACO(self):
        # 1. ACO (Accumulation/Distribution Oscillator)
        if 'ACO' in self.df.columns:
            aco_values = self.df['ACO']
            aco_prev_values = self.df['ACO'].shift(1)
            conditions = [
                (aco_values > 0) & (aco_prev_values <= 0),  # Crosses above zero (Buy Signal)
                (aco_values < 0) & (aco_prev_values >= 0),  # Crosses below zero (Sell Signal)
                (aco_values > 0) & (aco_prev_values > 0),   # No change, still positive
                (aco_values < 0) & (aco_prev_values < 0)    # No change, still negative
            ]
            choices = ['call', 'put', numpy.nan, numpy.nan]
            aco_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ACO', aco_signal)
        return

    def ADL(self):
        # 2. ADL (Accumulation/Distribution Line)
        if 'ADL' in self.df.columns:
            adl_values = self.df['ADL']
            adl_prev_values = self.df['ADL'].shift(1)
            conditions = [
                (adl_values > adl_prev_values),  # ADL is rising (Call Signal)
                (adl_values < adl_prev_values),  # ADL is falling (Put Signal)
                (adl_values > adl_prev_values) & (adl_prev_values > adl_prev_values.shift(1)),  # Reversal from fall to rise
                (adl_values < adl_prev_values) & (adl_prev_values < adl_prev_values.shift(1))   # Reversal from rise to fall
            ]
            choices = ['call', 'put', 'call', 'put']
            adl_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ADL', adl_signal)
        return

    def AROON_0(self):
        # 3. AROON_0 (Aroon Indicator - Up)
        if 'AROON_0' in self.df.columns:
            aroon_0_values = self.df['AROON_0']
            conditions = [
                (aroon_0_values > 70),  # Call signal when Aroon_0 rises above 70
                (aroon_0_values < 30),  # Put signal when Aroon_0 falls below 30
                (aroon_0_values <= 70) & (aroon_0_values >= 30)  # Hold signal
            ]
            choices = ['call', 'put', numpy.nan]
            aroon_0_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AROON_0', aroon_0_signal)
        return

    def AROON_1(self):
        # 4. AROON_1 (Aroon Indicator - Down)
        if 'AROON_1' in self.df.columns:
            aroon_1_values = self.df['AROON_1']
            conditions = [
                (aroon_1_values < 30),  # Buy Signal: weakening bearish momentum
                (aroon_1_values > 70),   # Sell Signal: strong bearish momentum
                (aroon_1_values <= 70) & (aroon_1_values >= 30)  # Neutral
            ]
            choices = ['call', 'put', numpy.nan]
            aroon_1_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AROON_1', aroon_1_signal)
        return

    def AWO(self):
        # 5. AWO (Awesome Oscillator)
        if 'AWO' in self.df.columns:
            awo_values = self.df['AWO']
            awo_prev_values = self.df['AWO'].shift(1)
            conditions = [
                (awo_values > 0) & (awo_prev_values <= 0),  # Crosses above zero
                (awo_values < 0) & (awo_prev_values >= 0),  # Crosses below zero
            ]
            choices = ['call', 'put']
            awo_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AWO', awo_signal)
        return

    def BBANDS(self):
        # 6-8. Bollinger Bands (BBANDS_0, BBANDS_1, BBANDS_2)
        if all(col in self.df.columns for col in ['BBANDS_0', 'BBANDS_1', 'BBANDS_2']):
            price = self.AVGPRICE
            bbands_0 = self.df['BBANDS_0']
            bbands_1 = self.df['BBANDS_1']
            bbands_2 = self.df['BBANDS_2']
            conditions = [
                (price <= bbands_2) & (price > bbands_1),  # Buy Signal: touches lower band
                (price >= bbands_0) & (price < bbands_1),  # Sell Signal: touches upper band
            ]
            choices = ['call', 'put']
            bbands_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('BBANDS', bbands_signal)
        return

    def Bear_Power(self):
        # 9. Bear Power
        if 'Bear_Power' in self.df.columns:
            bear_power = self.df['Bear_Power']
            bear_power_prev = self.df['Bear_Power'].shift(1)
            conditions = [
                (bear_power > bear_power_prev),  # Rising Bear Power
                (bear_power < bear_power_prev)    # Falling Bear Power
            ]
            choices = ['call', 'put']
            bear_power_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Bear_Power', bear_power_signal)
        return

    def Bull_Power(self):
        # 10. Bull Power
        if 'Bull_Power' in self.df.columns:
            bull_power = self.df['Bull_Power']
            bull_power_prev = self.df['Bull_Power'].shift(1)
            conditions = [
                (bull_power > bull_power_prev),  # Rising Bull Power
                (bull_power < bull_power_prev)    # Falling Bull Power
            ]
            choices = ['call', 'put']
            bull_power_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Bull_Power', bull_power_signal)
        return

    def Chaikin_Oscillator(self):
        # 11-13. Chaikin Oscillator (CO, CO_Fast, CO_Slow)
        for osc in ['CO', 'CO_Fast', 'CO_Slow']:
            if osc in self.df.columns:
                osc_values = self.df[osc]
                osc_prev_values = self.df[osc].shift(1)
                conditions = [
                    (osc_values > 0) & (osc_prev_values <= 0),  # Crosses above zero
                    (osc_values < 0) & (osc_prev_values >= 0)   # Crosses below zero
                ]
                choices = ['call', 'put']
                osc_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(osc, osc_signal)
        return

    def Ichimoku_Cloud(self):
        # 14. Ichimoku Cloud (Chimoku)
        if all(col in self.df.columns for col in ['Senkou_A', 'Senkou_B']):
            price = self.AVGPRICE
            chimoku = self.df['Chimoku']
            senkou_a = self.df['Senkou_A']
            senkou_b = self.df['Senkou_B']
            conditions = [
                (price > chimoku) & (senkou_a > senkou_b),  # Bullish trend
                (price < chimoku) & (senkou_a < senkou_b)   # Bearish trend
            ]
            choices = ['call', 'put']
            chimoku_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Chimoku', chimoku_signal)
        return

    def Coppock(self):
        # 15-16. Coppock Curve and Coppock Raw
        for coppock in ['Coppock_Curve', 'Coppock_Raw']:
            if coppock in self.df.columns:
                coppock_values = self.df[coppock]
                coppock_prev_values = self.df[coppock].shift(1)
                conditions = [
                    (coppock_values > 0) & (coppock_prev_values <= 0),  # Crosses above zero
                    (coppock_values < 0) & (coppock_prev_values >= 0)    # Crosses below zero
                ]
                choices = ['call', 'put']
                coppock_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(coppock, coppock_signal)
        return

    def MAA(self):
        # 17-20. Moving Averages (DEMA, EMA, TEMA, T3, HMA, KAMA, MA)
        for ma in ['DEMA', 'EMA', 'TEMA', 'T3', 'HMA', 'KAMA', 'MA']:
            if ma in self.df.columns:
                price = self.AVGPRICE
                ma_values = self.df[ma]
                conditions = [
                    (price > ma_values) & (ma_values > ma_values.shift(1)),  # Price above rising MA
                    (price < ma_values) & (ma_values < ma_values.shift(1))   # Price below falling MA
                ]
                choices = ['call', 'put']
                ma_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(ma, ma_signal)
        return

    def DX(self):
        # 18. DX (Directional Movement Index)
        if 'DX' in self.df.columns:
            dx_values = self.df['DX']
            conditions = [
                (dx_values > 25) & (dx_values.shift(1) <= 25),  # Rises above 25
                (dx_values < 25) & (dx_values.shift(1) >= 25)    # Falls below 25
            ]
            choices = ['call', 'put']
            dx_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('DX', dx_signal)
        return

    def Force_Index(self):
        # 20-22. Force Index variants
        for fi in ['Force_Index', 'Force_Index_MA', 'Force_Index_max_min']:
            if fi in self.df.columns:
                fi_values = self.df[fi]
                if fi == 'Force_Index_max_min':
                    # For max/min version, we look for peaks and troughs
                    fi_prev = fi_values.shift(1)
                    fi_next = fi_values.shift(-1)
                    conditions = [
                        (fi_values > fi_prev) & (fi_values > fi_next),  # Peak (potential sell)
                        (fi_values < fi_prev) & (fi_values < fi_next)   # Trough (potential buy)
                    ]
                    choices = ['put', 'call']
                elif fi == 'Force_Index_MA':
                    # For MA version, compare to its moving average
                    fi_ma = fi_values.rolling(window=14).mean()  # Assuming 14-period MA
                    conditions = [
                        (fi_values > fi_ma) & (fi_values.shift(1) <= fi_ma.shift(1)),  # Crosses above MA
                        (fi_values < fi_ma) & (fi_values.shift(1) >= fi_ma.shift(1))   # Crosses below MA
                    ]
                    choices = ['call', 'put']
                else:
                    # Regular Force Index
                    conditions = [
                        (fi_values > 0) & (fi_values.shift(1) <= 0),  # Crosses above zero
                        (fi_values < 0) & (fi_values.shift(1) >= 0)   # Crosses below zero
                    ]
                    choices = ['call', 'put']
                
                fi_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(fi, fi_signal)
        return

    def MAD(self):
        # 26-28. MAD variants
        for mad in ['MAD', 'MAD_lower', 'MAD_upper']:
            if mad in self.df.columns:
                price = self.AVGPRICE
                mad_values = self.df[mad]
                if mad == 'MAD_upper':
                    conditions = [
                        (price < mad_values) & (price.shift(1) >= mad_values.shift(1)),  # Crosses below upper
                        (price > mad_values) & (price.shift(1) <= mad_values.shift(1))   # Crosses above upper
                    ]
                    choices = ['call', 'put']  # Note: Upper band has inverse signals
                elif mad == 'MAD_lower':
                    conditions = [
                        (price > mad_values) & (price.shift(1) <= mad_values.shift(1)),  # Crosses above lower
                        (price < mad_values) & (price.shift(1) >= mad_values.shift(1))   # Crosses below lower
                    ]
                    choices = ['call', 'put']
                else:  # Regular MAD
                    conditions = [
                        (price > mad_values),  # Price above MAD
                        (price < mad_values)   # Price below MAD
                    ]
                    choices = ['call', 'put']
                
                mad_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(mad, mad_signal)
        return

    def MAMA(self):
        # 29-31. MAMA variants
        for mama in ['MAMA_0', 'MAMA_1']:
            if mama in self.df.columns:
                price = self.AVGPRICE
                mama_values = self.df[mama]
                conditions = [
                    (price > mama_values) & (price.shift(1) <= mama_values.shift(1)),  # Crosses above
                    (price < mama_values) & (price.shift(1) >= mama_values.shift(1))   # Crosses below
                ]
                choices = ['call', 'put']
                mama_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(mama, mama_signal)
        return

    def MFI(self):
        # 32. MFI (Money Flow Index)
        if 'MFI' in self.df.columns:
            mfi = self.df['MFI']
            conditions = [
                (mfi > 20) & (mfi.shift(1) <= 20),  # Crosses above 20
                (mfi < 80) & (mfi.shift(1) >= 80),  # Crosses below 80
                (mfi > 50) & (mfi.shift(1) <= 50),  # Crosses above 50
                (mfi < 50) & (mfi.shift(1) >= 50)   # Crosses below 50
            ]
            choices = ['call', 'put', 'call', 'put']
            mfi_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('MFI', mfi_signal)
            return

    def MFM(self):
        # 33-34. MFM and MFV
        for mf in ['MFM', 'MFV']:
            if mf in self.df.columns:
                mf_values = self.df[mf]
                if mf == 'MFM':
                    conditions = [
                        (mf_values > 0),  # Positive MFM
                        (mf_values < 0)   # Negative MFM
                    ]
                else:  # MFV
                    threshold = mf_values.rolling(window=11).mean()  # Using 14-period average as threshold
                    conditions = [
                        (mf_values > threshold) & (mf_values > mf_values.shift(1)),  # Above threshold and rising
                        (mf_values < threshold) & (mf_values < mf_values.shift(1))   # Below threshold and falling
                    ]
                choices = ['call', 'put']
                mf_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(mf, mf_signal)
        return

    def MIDPOINT(self):
        # 35-36. MIDPOINT and MIDPRICE
        for mid in ['MIDPOINT', 'MIDPRICE']:
            if mid in self.df.columns:
                price = self.AVGPRICE
                mid_values = self.df[mid]
                conditions = [
                    (price > mid_values) & (price.shift(1) <= mid_values.shift(1)),  # Crosses above
                    (price < mid_values) & (price.shift(1) >= mid_values.shift(1))   # Crosses below
                ]
                choices = ['call', 'put']
                mid_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(mid, mid_signal)
        return

    def MINUS_DI(self):
        # 37-38. MINUS_DI and PLUS_DI
        if all(col in self.df.columns for col in ['MINUS_DI', 'PLUS_DI']):
            minus_di = self.df['MINUS_DI']
            plus_di = self.df['PLUS_DI']
            conditions = [
                (minus_di < plus_di) & (minus_di.shift(1) >= plus_di.shift(1)),  # MINUS_DI crosses below PLUS_DI
                (minus_di > plus_di) & (minus_di.shift(1) <= plus_di.shift(1))   # MINUS_DI crosses above PLUS_DI
            ]
            choices = ['call', 'put']
            minus_di_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('DI', minus_di_signal)
        return

    def MINUS_DM(self):
        for DM in ['PLUS_DM', 'MINUS_DM']:
            if DM in self.df.columns:
                dm = self.df[DM]
                conditions = [
                    (dm > dm.shift(1)),  # Rising DM
                    (dm < dm.shift(1))   # Falling DM
                ]
                choices = ['call', 'put']
                plus_dm_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(DM, plus_dm_signal)
        return

    def TRIX(self):
        # 39. MOM (Momentum)
        for x in ['MOM', 'PPO', 'TRIX']:
            if x in self.df.columns:
                mom = self.df[x]
                conditions = [
                    (mom > 0) & (mom.shift(1) <= 0),  # Crosses above zero
                    (mom < 0) & (mom.shift(1) >= 0)   # Crosses below zero
                ]
                choices = ['call', 'put']
                mom_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(x, mom_signal)
        return

    def NATR(self):
        # 40. NATR (Normalized Average True Range)
        if 'NATR' in self.df.columns:
            natr = self.df['NATR']
            # NATR is typically used as a filter rather than direct signals
            # We'll create signals based on high volatility
            threshold = natr.rolling(window=11).mean()  # Using 14-period average as threshold
            conditions = [
                (natr > threshold * 1.5),  # High volatility
                (natr < threshold * 0.5)    # Low volatility
            ]
            choices = ['call', 'put']  # Interpretation depends on other indicators
            natr_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('NATR', natr_signal)
        return

    def OBV_high(self):
        # 41-43. OBV variants
        for obv in ['OBV', 'OBV_high', 'OBV_low']:
            if obv in self.df.columns:
                obv_values = self.df[obv]
                price = self.AVGPRICE
                conditions = [
                    (obv_values > obv_values.shift(1)) & (price <= price.shift(1)),  # OBV up, price flat/down
                    (obv_values < obv_values.shift(1)) & (price >= price.shift(1)),  # OBV down, price flat/up
                    (obv_values > obv_values.shift(1)) & (price > price.shift(1)),   # Both up
                    (obv_values < obv_values.shift(1)) & (price < price.shift(1))    # Both down
                ]
                choices = ['call', 'put', 'call', 'put']
                obv_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(obv, obv_signal)
        return

    def ROCP(self):
        # 47-49. ROC variants
        for roc in ['ROC', 'ROCP', 'ROCR100']:
            if roc in self.df.columns:
                roc_values = self.df[roc]
                if roc == 'ROCR100':
                    threshold = 100
                else:
                    threshold = 0
                conditions = [
                    (roc_values > threshold) & (roc_values.shift(1) <= threshold),  # Crosses above threshold
                    (roc_values < threshold) & (roc_values.shift(1) >= threshold)   # Crosses below threshold
                ]
                choices = ['call', 'put']
                roc_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(roc, roc_signal)
        return

    def SAREXT(self):
        # 50. SAREXT (Extended Parabolic SAR)
        if 'SAREXT' in self.df.columns:
            price = self.AVGPRICE
            sarext = self.df['SAREXT']
            conditions = [
                (price > sarext) & (price.shift(1) <= sarext.shift(1)),  # Price crosses above SAREXT
                (price < sarext) & (price.shift(1) >= sarext.shift(1))   # Price crosses below SAREXT
            ]
            choices = ['call', 'put']
            sarext_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('SAREXT', sarext_signal)
        return

    def Stochastic(self):
        # 51-56. Stochastic variants
        for stoch in ['STOCHF_0', 'STOCHF_1', 'STOCHRSI_0', 'STOCHRSI_1', 'STOCH_0', 'STOCH_1']:
            if stoch in self.df.columns:
                stoch_values = self.df[stoch]
                if stoch.endswith('_0'):  # %K lines
                    conditions = [
                        (stoch_values > 20) & (stoch_values.shift(1) <= 20),  # Crosses above 20
                        (stoch_values < 80) & (stoch_values.shift(1) >= 80)   # Crosses below 80
                    ]
                else:  # %D lines
                    k_line = self.df[stoch.replace('_1', '_0')]
                    d_line = self.df[stoch]
                    conditions = [
                        (k_line > d_line) & (k_line.shift(1) <= d_line.shift(1)),  # %K crosses above %D
                        (k_line < d_line) & (k_line.shift(1) >= d_line.shift(1))   # %K crosses below %D
                    ]
                choices = ['call', 'put']
                stoch_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(stoch, stoch_signal)
        return

    def Senkou(self):
        # 57-58. Senkou A and B
        for senkou in ['Senkou_A', 'Senkou_B']:
            if senkou in self.df.columns:
                price = self.AVGPRICE
                senkou_values = self.df[senkou]
                conditions = [
                    (price > senkou_values) & (price.shift(1) <= senkou_values.shift(1)),  # Crosses above
                    (price < senkou_values) & (price.shift(1) >= senkou_values.shift(1))   # Crosses below
                ]
                choices = ['call', 'put']
                senkou_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(senkou, senkou_signal)
        return

    def TRANGE(self):
        # 61. TRANGE (True Range)
        if 'TRANGE' in self.df.columns:
            trange = self.df['TRANGE']
            # TRANGE is typically used as a filter
            threshold = trange.rolling(window=11).mean()  # 14-period average
            conditions = [
                (trange > threshold * 1.5),  # High volatility
                (trange < threshold * 0.5)    # Low volatility
            ]
            choices = ['call', 'put']  # Interpretation depends on other indicators
            trange_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('TRANGE', trange_signal)
        return

    def TRIMA(self):
        # 62. TRIMA (Triangular Moving Average)
        if 'TRIMA' in self.df.columns:
            price = self.AVGPRICE
            trima = self.df['TRIMA']
            conditions = [
                (price > trima) & (price.shift(1) <= trima.shift(1)),  # Crosses above
                (price < trima) & (price.shift(1) >= trima.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            trima_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('TRIMA', trima_signal)
        return

    def TSI(self):
        # 64-65. TSI
        if 'TSI' in self.df.columns and 'TSI_signal' in self.df.columns:
            tsi = self.df['TSI']
            tsi_signal = self.df['TSI_signal']
            conditions = [
                (tsi > tsi_signal) & (tsi.shift(1) <= tsi_signal.shift(1)),  # TSI crosses above signal
                (tsi < tsi_signal) & (tsi.shift(1) >= tsi_signal.shift(1))   # TSI crosses below signal
            ]
            choices = ['call', 'put']
            osc_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('TSI', osc_signal)
        return

    def TYPPRICE(self):
        # 66. TYPPRICE (Typical Price)
        if 'TYPPRICE' in self.df.columns:
            price = self.AVGPRICE
            typprice = self.df['TYPPRICE']
            conditions = [
                (price > typprice) & (price.shift(1) <= typprice.shift(1)),  # Crosses above
                (price < typprice) & (price.shift(1) >= typprice.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            typprice_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('TYPPRICE', typprice_signal)
        return

    def Tenkan(self):
        # 67. Tenkan (Ichimoku Conversion Line)
        if 'Tenkan' in self.df.columns:
            price = self.AVGPRICE
            tenkan = self.df['Tenkan']
            conditions = [
                (price > tenkan) & (price.shift(1) <= tenkan.shift(1)),  # Crosses above
                (price < tenkan) & (price.shift(1) >= tenkan.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            tenkan_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Tenkan', tenkan_signal)
        return

    def ULTOSC(self):
        # 68. ULTOSC (Ultimate Oscillator)
        if 'ULTOSC' in self.df.columns:
            ultosc = self.df['ULTOSC']
            conditions = [
                (ultosc < 30) & (ultosc.shift(1) >= 30),  # Falls below 30 then crosses back up
                (ultosc > 70) & (ultosc.shift(1) <= 70)   # Rises above 70 then crosses back down
            ]
            choices = ['call', 'put']
            ultosc_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ULTOSC', ultosc_signal)
        return

    def WCLPRICE(self):
        # 69. WCLPRICE (Weighted Close Price)
        if 'WCLPRICE' in self.df.columns:
            price = self.AVGPRICE
            wclprice = self.df['WCLPRICE']
            conditions = [
                (price > wclprice) & (price > price.shift(1)),  # Above and rising
                (price < wclprice) & (price < price.shift(1))    # Below and falling
            ]
            choices = ['call', 'put']
            wclprice_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('WCLPRICE', wclprice_signal)
        return

    def WILLR(self):
        # 70. WILLR (Williams %R)
        if 'WILLR' in self.df.columns:
            willr = self.df['WILLR']
            conditions = [
                (willr > -80) & (willr.shift(1) <= -80),  # Crosses above -80
                (willr < -20) & (willr.shift(1) >= -20)   # Crosses below -20
            ]
            choices = ['call', 'put']
            willr_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('WILLR', willr_signal)
        return

    def WMA(self):
        # 71. WMA (Weighted Moving Average)
        if 'WMA' in self.df.columns:
            price = self.AVGPRICE
            wma = self.df['WMA']
            conditions = [
                (price > wma) & (price.shift(1) <= wma.shift(1)),  # Crosses above
                (price < wma) & (price.shift(1) >= wma.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            wma_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('WMA', wma_signal)
        return

    def WRSI(self):
        # 72-75. WRSI variants
        for wrsi in ['WRSI', 'WRSI_MA', 'WRSI_Overbought', 'WRSI_Oversold']:
            if all(col in self.df.columns for col in ['WRSI', wrsi]):
                wrsi_values = self.df['WRSI']
                if wrsi == 'WRSI_MA':
                    wrsi_ma = self.df['WRSI_MA']
                    conditions = [
                        (wrsi_values > wrsi_ma) & (wrsi_values.shift(1) <= wrsi_ma.shift(1)),  # Crosses above MA
                        (wrsi_values < wrsi_ma) & (wrsi_values.shift(1) >= wrsi_ma.shift(1))   # Crosses below MA
                    ]
                    choices = ['call', 'put']
                elif wrsi == 'WRSI_Overbought':
                    wrsi_ob = self.df[wrsi]
                    conditions = [
                        (wrsi_values < wrsi_ob) & (wrsi_values.shift(1) >= wrsi_ob.shift(1))  # Falls from overbought
                    ]
                    choices = ['put']
                elif wrsi == 'WRSI_Oversold':
                    wrsi_os = self.df[wrsi]
                    conditions = [
                        (wrsi_values > wrsi_os) & (wrsi_values.shift(1) <= wrsi_os.shift(1))  # Rises from oversold
                    ]
                    choices = ['call']
                else:  # Regular WRSI
                    conditions = [
                        (wrsi_values > 30) & (wrsi_values.shift(1) <= 30),  # Crosses above 30
                        (wrsi_values < 70) & (wrsi_values.shift(1) >= 70)   # Crosses below 70
                    ]
                    choices = ['call', 'put']
                
                wrsi_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(wrsi, wrsi_signal)
        return

    def senkou(self):
        # 76-77. combined_senkou_Max and Min
        for senkou in ['combined_senkou_Max', 'combined_senkou_Min']:
            if senkou in self.df.columns:
                price = self.AVGPRICE
                senkou_values = self.df[senkou]
                if senkou == 'combined_senkou_Max':
                    conditions = [
                        (price >= senkou_values) & (price.shift(1) < senkou_values.shift(1)),  # Tests resistance
                        (price < senkou_values) & (price.shift(1) >= senkou_values.shift(1))   # Rejects from resistance
                    ]
                    choices = ['put', 'call']
                else:  # combined_senkou_Min
                    conditions = [
                        (price <= senkou_values) & (price.shift(1) > senkou_values.shift(1)),  # Tests support
                        (price > senkou_values) & (price.shift(1) <= senkou_values.shift(1))   # Bounces from support
                    ]
                    choices = ['call', 'put']
                
                senkou_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(senkou, senkou_signal)
        return

    def channel(self):
        # 79-81. Envelope, Keltner Channels
        for channel in ['donchian', 'envelope', 'keltner']:
            lower = f'{channel}_lower'
            upper = f'{channel}_upper'
            if all(col in self.df.columns for col in [lower, upper]):
                price = self.AVGPRICE
                lower_values = self.df[lower]
                upper_values = self.df[upper]
                if channel == 'keltner':
                    conditions = [
                        (price <= upper_values),  # Touches upper band
                        (price >= lower_values),  # Touches lower band
                        (price > upper_values) & (price.shift(1) <= upper_values.shift(1)),  # Crosses above upper
                        (price < lower_values) & (price.shift(1) >= lower_values.shift(1))   # Crosses below lower
                    ]
                    choices = ['put', 'call', 'put', 'call']
                else:
                    conditions = [
                        (price <= lower_values),  # Touches lower band
                        (price >= upper_values),  # Touches upper band
                        (price > lower_values) & (price.shift(1) <= lower_values.shift(1)),  # Crosses above lower
                        (price < upper_values) & (price.shift(1) >= upper_values.shift(1))   # Crosses below upper
                    ]
                    choices = ['call', 'put', 'call', 'put']
                
                channel_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(channel, channel_signal)
        return

    def Rainbow(self):
        # 83-85. Rainbow Oscillator variants
        if 'rb' in self.df.columns:
            rb = self.df['rb']
            conditions = [
                (rb > rb.shift(1)) & (rb.shift(1) > rb.shift(2)),  # Upward stacking
                (rb < rb.shift(1)) & (rb.shift(1) < rb.shift(2))   # Downward stacking
            ]
            choices = ['call', 'put']
            rb_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('rb', rb_signal)
        return

    def rb_slope(self):
        if 'rb_slope' in self.df.columns:
            rb_slope = self.df['rb_slope']
            conditions = [
                (rb_slope > 0) & (rb_slope > rb_slope.shift(1)),  # Positive and increasing
                (rb_slope < 0) & (rb_slope < rb_slope.shift(1))   # Negative
            ]
            choices = ['call', 'put']
            rb_slope_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('rb_slope', rb_slope_signal)
        return

    def Rainbow_Oscillator(self):
        if 'rbo' in self.df.columns:
            rbo = self.df['rbo']
            conditions = [
                (rbo > rbo.shift(1)) & (rbo.shift(1) <= rbo.shift(2)),  # Turns upward
                (rbo < rbo.shift(1)) & (rbo.shift(1) >= rbo.shift(2))    # Turns downward
            ]
            choices = ['call', 'put']
            rbo_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('rbo', rbo_signal)
        return

    def Wicks(self):
        # 86. Wick analysis
        if all(col in self.df.columns for col in ['wick_up', 'wick_low']):
            wick_low = self.df['wick_low']
            wick_up = self.df['wick_up']
            price_change = self.df['close'] - self.df['open']
            conditions = [
                (wick_low > (self.df['max'] - self.df['min']) * 0.3) & (price_change > 0),  # Long lower wick, green candle
                (wick_up > (self.df['max'] - self.df['min']) * 0.3) & (price_change < 0)     # Long upper wick, red candle
            ]
            choices = ['call', 'put']
            wick_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('wicks', wick_signal)
        return

    def Gator(self):
        # 87-89. Gator indicators
        if all(col in self.df.columns for col in ['Gator_JAW', 'Gator_TEETH', 'Gator_LIPS']):
            jaw = self.df['Gator_JAW']
            teeth = self.df['Gator_TEETH']
            lips = self.df['Gator_LIPS']
            conditions = [
                (lips > teeth) & (teeth > jaw) & (lips.shift(1) <= teeth.shift(1)),  # Lips crosses above
                (lips < teeth) & (teeth < jaw) & (lips.shift(1) >= teeth.shift(1))   # Lips crosses below
            ]
            choices = ['call', 'put']
            gator_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Gator', gator_signal)
        return

    def Gator_bars(self):
        if all(col in self.df.columns for col in ['Gator_UPPER', 'Gator_LOWER']):
            gator_upper = self.df['Gator_UPPER']
            gator_lower = self.df['Gator_LOWER']
            conditions = [
                (gator_upper > gator_upper.shift(1)),  # Upper bars growing
                (gator_lower > gator_lower.shift(1))    # Lower bars growing
            ]
            choices = ['call', 'put']
            gator_bars_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Gator_bars', gator_bars_signal)
        return

    def Gator_Expansion(self):
        if 'Gator_Expansion' in self.df.columns:
            Gator_Expansion = self.df['Gator_Expansion']
            conditions = [
                (Gator_Expansion > 0),
                (Gator_Expansion < 0)
            ]
            choices = ['call', 'put']
            Gator_Expansion_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Gator_Expansion', Gator_Expansion_signal)
        return

    def HPR(self):
        # 91. HPR (Highest Price Range)
        if 'HPR' in self.df.columns:
            hpr = self.df['HPR']
            price = self.AVGPRICE
            conditions = [
                (price > hpr) & (price.shift(1) <= hpr.shift(1)),  # Breaks above HPR
                (price < hpr) & (price >= hpr.shift(1)) & (price.shift(1) >= hpr.shift(1))  # Rejects at HPR
            ]
            choices = ['call', 'put']
            hpr_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HPR', hpr_signal)
        return

    def HSI(self):
        # 92. HSI (Hurst Signal Indicator)
        if 'HSI' in self.df.columns:
            hsi = self.df['HSI']
            conditions = [
                (hsi > hsi.shift(1)),  # Rising HSI
                (hsi < hsi.shift(1))    # Falling HSI
            ]
            choices = ['call', 'put']
            hsi_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HSI', hsi_signal)
        return

    def HT_DCPERIOD(self):
        # 93-98. Hilbert Transform indicators
        if 'HT_DCPERIOD' in self.df.columns:
            ht_dcperiod = self.df['HT_DCPERIOD']
            conditions = [
                (ht_dcperiod > ht_dcperiod.shift(1)),  # Period lengthening
                (ht_dcperiod < ht_dcperiod.shift(1))    # Period shortening
            ]
            choices = ['call', 'put']
            ht_dcperiod_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_DCPERIOD', ht_dcperiod_signal)
        return

    def HT_DCPHASE(self):
        if 'HT_DCPHASE' in self.df.columns:
            ht_dcphase = self.df['HT_DCPHASE']
            conditions = [
                (ht_dcphase > ht_dcphase.shift(1)),  # Phase increasing
                (ht_dcphase < ht_dcphase.shift(1))    # Phase decreasing
            ]
            choices = ['call', 'put']
            ht_dcphase_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_DCPHASE', ht_dcphase_signal)
        return

    def HT_PHASOR(self):
        if all(col in self.df.columns for col in ['HT_PHASOR_0', 'HT_PHASOR_1']):
            phasor_0 = self.df['HT_PHASOR_0']
            phasor_1 = self.df['HT_PHASOR_1']
            conditions = [
                (phasor_0 > phasor_1) & (phasor_0.shift(1) <= phasor_1.shift(1)),  # Phasor0 crosses above
                (phasor_0 < phasor_1) & (phasor_0.shift(1) >= phasor_1.shift(1))   # Phasor0 crosses below
            ]
            choices = ['call', 'put']
            phasor_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_PHASOR', phasor_signal)
        return

    def HT_SINE(self):
        if all(col in self.df.columns for col in ['HT_SINE_0', 'HT_SINE_1']):
            sine_0 = self.df['HT_SINE_0']
            sine_1 = self.df['HT_SINE_1']
            conditions = [
                (sine_0 > sine_1) & (sine_0.shift(1) <= sine_1.shift(1)),  # Sine0 crosses above
                (sine_0 < sine_1) & (sine_0.shift(1) >= sine_1.shift(1))   # Sine0 crosses below
            ]
            choices = ['call', 'put']
            sine_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_SINE', sine_signal)
        return

    def HT_TRENDLINE(self):
        if 'HT_TRENDLINE' in self.df.columns:
            price = self.AVGPRICE
            ht_trendline = self.df['HT_TRENDLINE']
            conditions = [
                (price > ht_trendline) & (price.shift(1) <= ht_trendline.shift(1)),  # Crosses above
                (price < ht_trendline) & (price.shift(1) >= ht_trendline.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            ht_trendline_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_TRENDLINE', ht_trendline_signal)
        return

    def HT_TRENDMODE(self):
        if 'HT_TRENDMODE' in self.df.columns:
            ht_trendmode = self.df['HT_TRENDMODE']
            conditions = [
                (ht_trendmode == 1),  # Trending
                (ht_trendmode == 0)   # Not trending
            ]
            choices = ['call', 'put']  # Interpretation depends on other indicators
            ht_trendmode_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HT_TRENDMODE', ht_trendmode_signal)
        return

    def Historical(self):
        # 99. HV (Historical Volatility)
        if 'HV' in self.df.columns:
            hv = self.df['HV']
            threshold = hv.rolling(window=11).mean()
            conditions = [
                (hv > threshold * 1.5),  # High volatility
                (hv < threshold * 0.5)   # Low volatility
            ]
            choices = ['call', 'put']  # Interpretation depends on other indicators
            hv_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('HV', hv_signal)
        return

    def KST(self):
        # 101. KST (Know Sure Thing)
        if all(col in self.df.columns for col in ['KST', 'KST_Signal']):
            kst = self.df['KST']
            kst_signal = self.df['KST_Signal']
            conditions = [
                (kst > kst_signal) & (kst.shift(1) <= kst_signal.shift(1)),  # KST crosses above signal
                (kst < kst_signal) & (kst.shift(1) >= kst_signal.shift(1))   # KST crosses below signal
            ]
            choices = ['call', 'put']
            kst_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('KST', kst_signal)
        return

    def Kijun(self):
        # 102. Kijun (Ichimoku Base Line)
        if 'Kijun' in self.df.columns:
            price = self.AVGPRICE
            kijun = self.df['Kijun']
            conditions = [
                (price > kijun) & (price.shift(1) <= kijun.shift(1)),  # Crosses above
                (price < kijun) & (price.shift(1) >= kijun.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            kijun_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('Kijun', kijun_signal)
        return

    def MACD(self):
        # 104-109. MACDEXT/MACDFIX variants
        for macd_type in ['MACD', 'MACDEXT', 'MACDFIX']:
            macd_line = f"{macd_type}_0"
            signal_line = f"{macd_type}_1"
            histogram = f"{macd_type}_2"
            if all(col in self.df.columns for col in [macd_line, signal_line, histogram]):
                macd_line = self.df[macd_line]
                signal_line = self.df[signal_line]
                histogram = self.df[histogram]
                conditions = [
                    (macd_line > 0) & (macd_line.shift(1) <= 0) & (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1)) & (histogram > 0) & (histogram > histogram.shift(1)) & (histogram.shift(1) <= 0),  # MACD crosses above signal
                    (macd_line < 0) & (macd_line.shift(1) >= 0) & (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1)) & (histogram < 0) & (histogram < histogram.shift(1)) & (histogram.shift(1) >= 0),  # MACD crosses below signal
                ]
                choices = ['call', 'put']
                macd_signal = numpy.select(conditions, choices, default=numpy.nan)
                self._add_strategy(macd_type, macd_signal)
        return

    def AD(self):
        # 1. AD (Accumulation/Distribution Line)
        if 'AD' in self.df.columns:
            ad = self.df['AD']
            conditions = [
                (ad > ad.shift(1)),  # Rising AD
                (ad < ad.shift(1))   # Falling AD
            ]
            choices = ['call', 'put']
            ad_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AD', ad_signal)
        return

    def ADXR(self):
        # 2. ADXR (Average Directional Movement Index Rating)
        if 'ADXR' in self.df.columns:
            adxr = self.df['ADXR']
            conditions = [
                (adxr > 25) & (adxr.shift(1) <= 25),  # Rises above 25
                (adxr < 25) & (adxr.shift(1) >= 25)    # Falls below 25
            ]
            choices = ['call', 'put']
            adxr_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ADXR', adxr_signal)
        return

    def APO(self):
        # 3. APO (Absolute Price Oscillator)
        if 'APO' in self.df.columns:
            apo = self.df['APO']
            conditions = [
                (apo > 0) & (apo.shift(1) <= 0),  # Crosses above zero
                (apo < 0) & (apo.shift(1) >= 0)    # Crosses below zero
            ]
            choices = ['call', 'put']
            apo_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('APO', apo_signal)
        return

    def AROONOSC(self):
        # 4. AROONOSC (Aroon Oscillator)
        if 'AROONOSC' in self.df.columns:
            aroonosc = self.df['AROONOSC']
            conditions = [
                (aroonosc > 0) & (aroonosc.shift(1) <= 0),  # Crosses above zero
                (aroonosc < 0) & (aroonosc.shift(1) >= 0)    # Crosses below zero
            ]
            choices = ['call', 'put']
            aroonosc_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AROONOSC', aroonosc_signal)
        return

    def AVG(self):
        # 5. AVGPRICE (Average Price)
        if 'AVGPRICE' in self.df.columns:
            price = self.df['close']
            avgprice = self.df['AVGPRICE']
            conditions = [
                (price > avgprice) & (price.shift(1) <= avgprice.shift(1)),  # Crosses above
                (price < avgprice) & (price.shift(1) >= avgprice.shift(1))   # Crosses below
            ]
            choices = ['call', 'put']
            avgprice_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('AVGPRICE', avgprice_signal)
        return

    def BOP(self):
        # 6. BOP (Balance of Power)
        if 'BOP' in self.df.columns:
            bop = self.df['BOP']
            conditions = [
                (bop > 0) & (bop.shift(1) <= 0),  # Crosses above zero
                (bop < 0) & (bop.shift(1) >= 0)    # Crosses below zero
            ]
            choices = ['call', 'put']
            bop_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('BOP', bop_signal)
        return

    def CCI(self):
        # 7. CCI (Commodity Channel Index)
        if 'CCI' in self.df.columns:
            cci = self.df['CCI']
            conditions = [
                (cci > -100) & (cci.shift(1) <= -100),  # Crosses above -100
                (cci < 100) & (cci.shift(1) >= 100)      # Crosses below 100
            ]
            choices = ['call', 'put']
            cci_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('CCI', cci_signal)
        return

    def CMO(self):
        # 8. CMO (Chande Momentum Oscillator)
        if 'CMO' in self.df.columns:
            cmo = self.df['CMO']
            conditions = [
                (cmo > -50) & (cmo.shift(1) <= -50),  # Crosses above -50
                (cmo < 50) & (cmo.shift(1) >= 50)      # Crosses below 50
            ]
            choices = ['call', 'put']
            cmo_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('CMO', cmo_signal)
        return

    def ADOSC(self):
        # 1. ADOSC (Accumulation/Distribution Oscillator)
        if 'ADOSC' in self.df.columns:
            adosc = self.df['ADOSC']
            conditions = [
                (adosc > 0) & (adosc.shift(1) <= 0),  # Crosses above zero
                (adosc < 0) & (adosc.shift(1) >= 0)    # Crosses below zero
            ]
            choices = ['call', 'put']
            adosc_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ADOSC', adosc_signal)
        return

    def ADX(self):
        # 2. ADX (Average Directional Index)
        if all(col in self.df.columns for col in ['ADX', 'PLUS_DI', 'MINUS_DI']):
            adx = self.df['ADX']
            plus_di = self.df['PLUS_DI']
            minus_di = self.df['MINUS_DI']
            conditions = [
                (adx > 25) & (plus_di > minus_di),  # Strong bullish trend
                (adx > 25) & (plus_di < minus_di),  # Strong bearish trend
                (adx < 20)                          # Weak trend
            ]
            choices = ['call', 'put', numpy.nan]
            adx_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ADX', adx_signal)
        return

    def ATR(self):
        # 3. ATR (Average True Range)
        if 'ATR' in self.df.columns:
            atr = self.df['ATR']
            # ATR is typically used as a filter rather than direct signals
            threshold = atr.rolling(window=11).mean()
            conditions = [
                (atr > threshold * 1.5),  # High volatility
                (atr < threshold * 0.5)    # Low volatility
            ]
            choices = ['call', 'put']  # Interpretation depends on other indicators
            atr_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('ATR', atr_signal)
        return

    def RSI(self):
        # 6. RSI (Relative Strength Index)
        if 'RSI' in self.df.columns:
            rsi = self.df['RSI']
            conditions = [
                (rsi > 30) & (rsi.shift(1) <= 30),  # Crosses above 30
                (rsi < 70) & (rsi.shift(1) >= 70)    # Crosses below 70
            ]
            choices = ['call', 'put']
            rsi_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('RSI', rsi_signal)
        return

    def SAR(self):
        # 9. Parabolic SAR (Stop and Reverse)
        if 'SAR' in self.df.columns:
            price = self.AVGPRICE
            sar = self.df['SAR']
            conditions = [
                (price > sar) & (price.shift(1) <= sar.shift(1)),  # Dots below price
                (price < sar) & (price.shift(1) >= sar.shift(1))   # Dots above price
            ]
            choices = ['call', 'put']
            sar_signal = numpy.select(conditions, choices, default=numpy.nan)
            self._add_strategy('SAR', sar_signal)
        return