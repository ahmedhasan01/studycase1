import logging, talib, numpy, pandas, time, gc

class Indicator_Signals():
    
    def __init__(self, df):
        self.duration = 1 * 60
        self.df = df
        self.Open = self.df['open'].astype(float)
        self.High = self.df['max'].astype(float)
        self.Low = self.df['min'].astype(float)
        self.Close = self.df['close'].astype(float)
        self.Volume = self.df['volume'].astype(float)
        self.To = self.df['to'].astype(float)
        self.strategies_list = {}
        self.final_list = []
        self._strategy_methods = self._get_strategy_methods()
        self._Parse_logic()
        self.max_indicator = 1
        logging.info('computing Strategies inside Indicator_Signals class.')

    def run(self) -> None:

        start = time.time()
        results = {}

        for strategy in self._strategy_methods:
            try:
                # Call methods with required arguments (self.df for example)
                if 'df' in getattr(self, strategy).__code__.co_varnames:
                    result = getattr(self, strategy)(self.df)  # Pass self.df if needed
                else:
                    result = getattr(self, strategy)()  # Call without arguments
                if isinstance(result, dict):
                    results.update(result)
            except Exception as exc:
                logging.error(f"computing Strategies in Indicator_Signals class {strategy}: {exc}")

        self.strategies_list = pandas.DataFrame.from_dict(results)
        call_count_series = (self.strategies_list == 1).sum(axis=1)
        put_count_series = (self.strategies_list == -1).sum(axis=1)
        self.strategies_list['final_dir'] = numpy.select(
            [
                (call_count_series > put_count_series) & (call_count_series >= self.max_indicator),
                (put_count_series > call_count_series) & (put_count_series >= self.max_indicator)
            ],
            ['call', 'put'],
            'none'
        )
        self.final_list = pandas.concat(self.final_list, axis=1)
        final_list = pandas.concat([self.final_list, self.strategies_list], axis=1)
        logging.info(f" FINAL_DIR: {self.strategies_list['final_dir'].iloc[-1]} after {final_list['Timing'].iloc[-1]}, call_count_series: {call_count_series.iloc[-1]}, put_count_series: {put_count_series.iloc[-1]}")
        final_list['Trade_time'] = numpy.where(final_list['Timing'] != 0, (self.To + final_list['Timing']), 0)

        # Get all attributes set in __init__
        init_attrs = list(self.__dict__.keys())
        # Delete them dynamically
        for attr in init_attrs:
            delattr(self, attr)
        gc.collect()

        ends = time.time()
        logging.warning(f"computing Strategies in Indicator_Signals class 2. {ends - start}")
        return final_list

    def _Parse_logic(self):
        
        self.BOP_c = talib.BOP(self.Open, self.High, self.Low, self.Close)
        self.bullish_candle = self.Close > self.Open
        self.bearish_candle = self.Close < self.Open
        self.AVGPRICE = talib.AVGPRICE(self.Open, self.High, self.Low, self.Close)
        if self.Volume is not None and isinstance(self.Volume, pandas.Series):
            zero_vol = (self.Volume == 0).all()
            self.VOL_MA = talib.EMA(self.Volume.fillna(0), timeperiod=11)
            self.volume_spike = pandas.Series(True, index=self.Volume.index) if zero_vol else self.Volume > (1.8 * self.VOL_MA)
        self.EMA_c = talib.EMA(self.AVGPRICE, timeperiod=11)
        self.RSI_c = talib.RSI(self.AVGPRICE, timeperiod=11)
        self.mid_channel = self._mid_channel()
        self.support = self._support() | (self.RSI_c < 30)
        self.resistance = self._resistance() | (self.RSI_c > 70)
        self.price_above_ema = self.AVGPRICE > self.EMA_c
        self.price_below_ema = self.AVGPRICE < self.EMA_c

    def _get_strategy_methods(self):
        """Identify strategy methods at init (cached for speed)."""
        return [
            method for method in dir(self)
            if callable(getattr(self, method))
            and not method.startswith('_')
            and method not in ['run']
        ]

    def _add_strategy(self, indicator_name, signal_series):
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

    def _support(self, threshold_pct=0.01, lookback=11):
        """
        Combine swing lows, Fibonacci levels, and pivot points for support detection
        Returns: Boolean Series where True indicates price is near support
        """
        # Swing Low Support
        swing_lows = (self.Low < self.Low.shift(1)) & (self.Low < self.Low.shift(-1))
        swing_vals = self.Low.where(swing_lows)
        swing_support = swing_vals.rolling(lookback, min_periods=1).min().ffill()
        
        # Fibonacci Support Levels
        recent_high = self.High.rolling(lookback).max()
        recent_low = self.Low.rolling(lookback).min()
        swing_range = recent_high - recent_low
        fib_382 = recent_high - swing_range * 0.382
        fib_500 = recent_high - swing_range * 0.5
        fib_618 = recent_high - swing_range * 0.618
        
        # Pivot Point Support Levels
        prev_high = self.High.shift(1)
        prev_low = self.Low.shift(1)
        prev_close = self.AVGPRICE.shift(1)
        PP = (prev_high + prev_low + prev_close) / 3
        S1 = 2 * PP - prev_high
        S2 = PP - (prev_high - prev_low)
        
        # Combine all support conditions
        near_swing = (self.AVGPRICE <= swing_support * (1 + threshold_pct)) & \
                    (self.AVGPRICE >= swing_support * (1 - threshold_pct))
        
        near_fibo = ((abs(self.AVGPRICE - fib_382) < fib_382 * threshold_pct) |
                    (abs(self.AVGPRICE - fib_500) < fib_500 * threshold_pct) |
                    (abs(self.AVGPRICE - fib_618) < fib_618 * threshold_pct))
        
        near_pivot = ((abs(self.AVGPRICE - S1) < S1 * threshold_pct) |
                    (abs(self.AVGPRICE - S2) < S2 * threshold_pct))
        
        return near_swing | near_fibo | near_pivot

    def _resistance(self, threshold_pct=0.01, lookback=11):
        """
        Combine swing highs, Fibonacci levels, and pivot points for resistance detection
        Returns: Boolean Series where True indicates price is near resistance
        """
        # Swing High Resistance
        swing_highs = (self.High > self.High.shift(1)) & (self.High > self.High.shift(-1))
        swing_vals = self.High.where(swing_highs)
        swing_resistance = swing_vals.rolling(lookback, min_periods=1).min().ffill()
        
        # Fibonacci Resistance Levels
        recent_high = self.High.rolling(lookback).max()
        recent_low = self.Low.rolling(lookback).min()
        swing_range = recent_high - recent_low
        fib_382 = recent_low + swing_range * 0.382
        fib_500 = recent_low + swing_range * 0.5
        fib_618 = recent_low + swing_range * 0.618
        
        # Pivot Point Resistance Levels
        prev_high = self.High.shift(1)
        prev_low = self.Low.shift(1)
        prev_close = self.AVGPRICE.shift(1)
        PP = (prev_high + prev_low + prev_close) / 3
        R1 = 2 * PP - prev_low
        R2 = PP + (prev_high - prev_low)
        
        # Combine all resistance conditions
        near_swing = (self.AVGPRICE <= swing_resistance * (1 + threshold_pct)) & \
                    (self.AVGPRICE >= swing_resistance * (1 - threshold_pct))
        
        near_fibo = ((abs(self.AVGPRICE - fib_382) < fib_382 * threshold_pct) |
                    (abs(self.AVGPRICE - fib_500) < fib_500 * threshold_pct) |
                    (abs(self.AVGPRICE - fib_618) < fib_618 * threshold_pct))
        
        near_pivot = ((abs(self.AVGPRICE - R1) < R1 * threshold_pct) |
                    (abs(self.AVGPRICE - R2) < R2 * threshold_pct))
        
        return near_swing | near_fibo | near_pivot

    def _mid_channel(self, lookback=11, threshold=0.3):
        """
        Improved mid-channel detection that considers:
        - Price position within recent range
        - Distance from nearest support/resistance
        """
        # Basic channel position
        recent_high = self.High.rolling(lookback).max()
        recent_low = self.Low.rolling(lookback).min()
        position = (self.AVGPRICE - recent_low) / (recent_high - recent_low)
        
        # Check distance from nearest support/resistance
        support_dist = abs(self.AVGPRICE - recent_low) / recent_low
        resist_dist = abs(self.AVGPRICE - recent_high) / recent_high
        min_dist = numpy.minimum(support_dist, resist_dist)
        
        return (position > threshold) & (position < (1 - threshold)) & (min_dist > 0.02)

    def Patterns(self):
        
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
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (self.RSI_c < 30),  # Bullish Engulfing + Oversold RSI
                (numpy.char.find(Pattern_Results, "CDLMORNINGSTAR-Bull") >= 0) & (MACD > MACD_signal),  # Morning Star + MACD Crossover
                (numpy.char.find(Pattern_Results, "CDLHAMMER-Bull") >= 0) & (self.AVGPRICE < Lower_BBand),  # Hammer + Bollinger Lower Band
                (numpy.char.find(Pattern_Results, "CDLPIERCING-Bull") >= 0) & (self.AVGPRICE > EMA),  # Piercing Line + Above EMA
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (self.RSI_c > 70),  # Bearish Engulfing + Overbought RSI
                (numpy.char.find(Pattern_Results, "CDLEVENINGSTAR-Bear") >= 0) & (MACD < MACD_signal),  # Evening Star + MACD Bearish Crossover
                (numpy.char.find(Pattern_Results, "CDLSHOOTINGSTAR-Bear") >= 0) & (self.AVGPRICE > Upper_BBand),  # Shooting Star + Bollinger Upper Band
                (numpy.char.find(Pattern_Results, "CDLDARKCLOUDCOVER-Bear") >= 0) & (self.AVGPRICE < EMA),  # Dark Cloud Cover + Below EMA
                (numpy.char.find(Pattern_Results, "CDLRISING3METHODS-Bull") >= 0),  # Rising Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bull") >= 0),  # Bullish Marubozu (Strong Uptrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bull") >= 0),  # Upside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLFALLING3METHODS-Bear") >= 0),  # Falling Three Methods
                (numpy.char.find(Pattern_Results, "CDLMARUBOZU-Bear") >= 0),  # Bearish Marubozu (Strong Downtrend)
                (numpy.char.find(Pattern_Results, "CDLTASUKIGAP-Bear") >= 0),  # Downside Tasuki Gap
                (numpy.char.find(Pattern_Results, "CDLDOJI") >= 0) & (ADX > 25),  # Doji with High ADX (Breakout Signal)
                (numpy.char.find(Pattern_Results, "CDLLONGLEGGEDDOJI") >= 0) & (ADX > 30),  # Long-Legged Doji with High ADX
                (numpy.char.find(Pattern_Results, "CDLSPINNINGTOP") >= 0) & (self.Volume > self.VOL_MA),  # Spinning Top with High Volume
                (numpy.char.find(Pattern_Results, "CDLHIGHWAVE") >= 0) & (self.Volume > self.VOL_MA),  # High-Wave Pattern with High Volume
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bull") >= 0) & (self.AVGPRICE < Lower_BBand),  # Bullish Engulfing at Support
                (numpy.char.find(Pattern_Results, "CDLENGULFING-Bear") >= 0) & (self.AVGPRICE > Upper_BBand)   # Bearish Engulfing at Resistance
            ],
            [1, 1, 1, 1,  # Bullish Reversals
            -1, -1, -1, -1,  # Bearish Reversals
            1, 1, 1,  # Bullish Continuation
            -1, -1, -1,  # Bearish Continuation
            1, 1, 1, 1,  # Breakout Patterns
            1, -1  # Support & Resistance Trades
            ],
            default=0
        )
        self.final_list.append(pandas.DataFrame(Pattern_Results, columns=["pattern"]))
        return {'pattern_dir': pattern_dir}

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
        
        diffs = pandas.concat([diffs, self.df[round1]], axis=1, ignore_index=False)
        exceed_100 = [col for col in exceed_100 if col in diffs.columns]
        diffs[exceed_100] = diffs[exceed_100] / 10

        color_df = pandas.concat([diffs, self.df[color]], axis=1, ignore_index=False)
        self._assign_color_labels(df=color_df, columns=color_df.columns)

        # -------------------------------//////////////////////Time Calculating for Entry the Trade//////////////////////-------------------------------
        row_sum = abs(diffs.sum(axis=1))
        row_count = diffs.shape[1]
        row_mean = row_sum / row_count
        
        safe_row_sum = row_sum.clip(lower=1)  # Scale logic using log10 and floor, handling small values
        scale = (10 ** (numpy.floor(numpy.log10(safe_row_sum)))).astype(int)
        scale.replace([numpy.inf, -numpy.inf], 1, inplace=True)
        scale.fillna(1, inplace=True)
        adjusted = numpy.where(row_mean < 100, row_mean, row_sum / numpy.ceil(scale))  # Apply adjustment
        row_mean = ((adjusted / 100) * (self.duration / 4)) + 14.5 # duration is half the time of the candle

        diffs = diffs.round(1)

        self.final_list.append(diffs)
        self.final_list.append(pandas.DataFrame(row_mean.round(2), columns=["Timing"]))
        return {}

    def MACD(self):
        # 104-109. MACDEXT/MACDFIX variants
        dic = {}
        for macd_type in ['MACD', 'MACDEXT', 'MACDFIX']:
            macd_line = f"{macd_type}_0"
            signal_line = f"{macd_type}_1"
            histogram = f"{macd_type}_2"
            if all(col in self.df.columns for col in [macd_line, signal_line, histogram]):
                macd_line = self.df[macd_line]
                signal_line = self.df[signal_line]
                histogram = self.df[histogram]

                # Divergence (you may need to calculate LL/HL logic separately using rolling or shift windows)
                bullish_divergence = (self.Low < self.Low.shift(1)) & (macd_line > macd_line.shift(1))  # Lower low in price, higher low in MACD
                bearish_divergence = (self.High > self.High.shift(1)) & (macd_line < macd_line.shift(1))  # Higher high in price, lower high in MACD

                macd_cross_up = (macd_line > signal_line) & (macd_line.shift(1) < signal_line.shift(1))
                macd_cross_down = (macd_line < signal_line) & (macd_line.shift(1) > signal_line.shift(1))

                histogram_green = (histogram > 0) & (histogram.shift(1) < 0) & (histogram > histogram.shift(1))
                histogram_red = (histogram < 0) & (histogram.shift(1) > 0) & (histogram < histogram.shift(1))

                close_above_mid = self.Close > ((self.Open + self.Close) / 2)
                close_below_mid = self.Close < ((self.Open + self.Close) / 2)

                Zero_Crossover = (macd_line > 0) & (macd_line.shift(1) <= 0)
                Zero_Crossbelow = (macd_line < 0) & (macd_line.shift(1) >= 0)
                Uptrend_Confirmation = (macd_line > macd_line.shift(1)) & (signal_line > signal_line.shift(1))
                Downtrend_Confirmation = (macd_line < macd_line.shift(1)) & (signal_line < signal_line.shift(1))

                # Define conditions for each entry type
                call_conditions = [
                    # Full combination
                    (bullish_divergence & macd_cross_up & histogram_green & close_above_mid & Zero_Crossover & Uptrend_Confirmation & self.support & self.price_above_ema),
                    # Crossover + histogram + candle
                    (macd_cross_up & histogram_green & self.support & self.price_above_ema),
                    # Divergence + support/oversold
                    (bullish_divergence & self.support)
                ]
                
                put_conditions = [
                    # Full combination
                    (bearish_divergence & macd_cross_down & histogram_red & close_below_mid & Zero_Crossbelow & Downtrend_Confirmation & self.resistance & self.price_below_ema),
                    # Crossover + histogram + candle
                    (close_below_mid & histogram_red & self.resistance & self.price_below_ema),
                    # Divergence + resistance/overbought
                    (bearish_divergence & self.resistance)
                ]
                
                # Combine conditions with OR logic
                call_condition = numpy.logical_or.reduce(call_conditions)
                put_condition = numpy.logical_or.reduce(put_conditions)
                
                # Apply filters to remove false signals
                valid_call = call_condition & ~self.mid_channel
                valid_put = put_condition & ~self.mid_channel
                
                # Create signals using numpy.select
                signals = numpy.select(
                    condlist=[valid_call, valid_put],
                    choicelist=[1, -1],
                    default=0
                )

                dic[macd_type] = signals
        return dic

    def RSI(self):
        EMA_RSI = talib.EMA(self.RSI_c, timeperiod=11)
        rsi_cross_above_30 = (self.RSI_c > 30) & (self.RSI_c.shift(1) <= 30)
        rsi_cross_below_70 = (self.RSI_c < 70) & (self.RSI_c.shift(1) >= 70)
        RSI_above_EMA = (self.RSI_c < 30) & (self.RSI_c > EMA_RSI)
        RSI_below_EMA = (self.RSI_c > 70) & (self.RSI_c < EMA_RSI)
        Bullish_divergence = (self.AVGPRICE < self.AVGPRICE.shift(1)) & (self.RSI_c > self.RSI_c.shift(1))
        Bearish_divergence = (self.AVGPRICE > self.AVGPRICE.shift(1)) & (self.RSI_c < self.RSI_c.shift(1))
        uptrend = (self.RSI_c > 50) & (self.RSI_c > self.RSI_c.shift(1))
        downtrend = (self.RSI_c < 50) & (self.RSI_c < self.RSI_c.shift(1))
        RSI_moving_up = (self.RSI_c > 40) & (self.RSI_c < 60) & (self.RSI_c > self.RSI_c.shift(1))
        RSI_moving_dwn= (self.RSI_c > 40) & (self.RSI_c < 60) & (self.RSI_c < self.RSI_c.shift(1))
        RSI_bouncing = (self.RSI_c.round(0) == 30) & (self.RSI_c > self.RSI_c.shift(1))
        RSI_reversing = (self.RSI_c.round(0) == 70) & (self.RSI_c < self.RSI_c.shift(1))
                
        call_conditions = [
            (rsi_cross_above_30 & uptrend & RSI_moving_up & RSI_bouncing & Bullish_divergence & RSI_above_EMA & self.bullish_candle & self.price_above_ema),
            (rsi_cross_above_30 & uptrend & RSI_moving_up & Bullish_divergence & RSI_above_EMA & self.bullish_candle & self.price_above_ema),
            (rsi_cross_above_30 & Bullish_divergence & RSI_above_EMA & self.bullish_candle & self.price_above_ema),
            (rsi_cross_above_30 & self.bullish_candle & self.price_above_ema)
        ]
        put_conditions = [
            (rsi_cross_below_70 & downtrend & RSI_moving_dwn & RSI_reversing & Bearish_divergence & RSI_below_EMA & self.bearish_candle & self.price_below_ema),
            (rsi_cross_below_70 & downtrend & RSI_moving_dwn & Bearish_divergence & RSI_below_EMA & self.bearish_candle & self.price_below_ema),
            (rsi_cross_below_70 & Bearish_divergence & RSI_below_EMA & self.bearish_candle & self.price_below_ema),
            (rsi_cross_below_70 & self.bearish_candle & self.price_below_ema)
        ]
        
        # Combine conditions with OR in case you add alternative entry conditions later
        call_condition = numpy.logical_or.reduce(call_conditions)
        put_condition = numpy.logical_or.reduce(put_conditions)
        
        # Create signals using numpy.select
        signals = numpy.select(
            condlist=[call_condition, put_condition],
            choicelist=[1, -1],
            default=0
        )
        return {'RSI': signals}

    def BOP(self):
        # 6. BOP (Balance of Power)
        bop_cross_above = (self.BOP_c > 0) & (self.BOP_c.shift(1) <= 0)
        bop_cross_below = (self.BOP_c < 0) & (self.BOP_c.shift(1) >= 0)
        # Create signals using numpy.select
        signals = numpy.select(
            condlist=[
                (bop_cross_above & self.bullish_candle & self.volume_spike),
                (bop_cross_below & self.bearish_candle & self.volume_spike)
            ],
            choicelist=[1, -1],  # 1 for Call, -1 for Put
            default=0             # 0 for no signal
        )
        return {'BOP': signals}

    def Wicks(self):
        # 86. Wick analysis
        if all(col in self.df.columns for col in ['wick_up', 'wick_low']):
            wick_low = self.df['wick_low'] / 100
            wick_up = self.df['wick_up']  / 100

            # Wick rejection conditions
            lower_wick_rejection = (wick_low >= (1.5 * self.BOP_c))
            upper_wick_rejection = (wick_up >= (1.5 * self.BOP_c))

            # Confirmation candles 
            next_open_above = self.Open > self.Close.shift(1)
            next_open_below = self.Open < self.Close.shift(1)

            # Generate signals
            signals = numpy.select(
                condlist=[
                    (lower_wick_rejection & self.support & next_open_above & self.volume_spike),
                    (upper_wick_rejection & self.resistance & next_open_below & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'wicks': signals}

    def BBANDS(self):
        # 6-8. Bollinger Bands (BBANDS_0, BBANDS_1, BBANDS_2)
        if all(col in self.df.columns for col in ['BBANDS_0', 'BBANDS_1', 'BBANDS_2']):
            bbands_0 = self.df['BBANDS_0']
            bbands_1 = self.df['BBANDS_1']
            bbands_2 = self.df['BBANDS_2']
            bandwidth = bbands_0 - bbands_2
            bandwidth_EMA = talib.EMA(bandwidth, timeperiod=11) * 0.5
            touches_lower = self.AVGPRICE <= bbands_2
            touches_upper = self.AVGPRICE >= bbands_0
            reversal_up = self.AVGPRICE > bbands_1
            reversal_down = self.AVGPRICE < bbands_1
            uptrend = self.AVGPRICE > self.EMA_c
            downtrend = self.AVGPRICE < self.EMA_c
            Breakout = (bandwidth > bandwidth_EMA)
            Breakdown = (bandwidth < bandwidth_EMA)
            Fibonacci_lower = (self.AVGPRICE <= (bbands_2 * 0.618))
            Fibonacci_upper = (self.AVGPRICE >= (bbands_0 * 0.382))

            # BUY (Call) Conditions
            call_conditions = [
                (touches_lower.shift(1) & reversal_up & Fibonacci_lower & self.volume_spike & uptrend),
                (touches_lower.shift(1) & reversal_up & Breakout & self.volume_spike & uptrend),
                (touches_lower.shift(1) & reversal_up & self.volume_spike & uptrend)
            ]
            
            # SELL (Put) Conditions
            put_conditions = [
                (touches_upper.shift(1) & reversal_down & Fibonacci_upper & self.volume_spike & downtrend),
                (touches_upper.shift(1) & reversal_down & Breakdown & self.volume_spike & downtrend),
                (touches_upper.shift(1) & reversal_down & self.volume_spike & downtrend)
            ]
            
            # Generate signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],  # 1 for Call, -1 for Put
                default=0             # 0 for no signal
            )
            return {'BBANDS': signals}

    def channels(self):
        # 79-81. Envelope, Keltner Channels
        dic = {}
        for channel in ['donchian', 'envelope', 'keltner']:
            lower = f'{channel}_lower'
            upper = f'{channel}_upper'
            if all(col in self.df.columns for col in [lower, upper]):
                lower_values = self.df[lower]
                upper_values = self.df[upper]
                if channel == 'envelope':
                    # Signal conditions
                    touches_lower = self.AVGPRICE <= lower_values
                    touches_upper = self.AVGPRICE >= upper_values
                    
                    # Reversal confirmation (next candle)
                    next_open_above_lower = self.Open.shift(-1) > lower_values.shift(-1)
                    next_close_above_lower = self.Close.shift(-1) > lower_values.shift(-1)
                    
                    next_open_below_upper = self.Open.shift(-1) < upper_values.shift(-1)
                    next_close_below_upper = self.Close.shift(-1) < upper_values.shift(-1)
                    
                    # Generate raw signals
                    signals = numpy.select(
                            condlist=[
                                (touches_lower & next_open_above_lower & next_close_above_lower & self.volume_spike),
                                (touches_upper & next_open_below_upper & next_close_below_upper & self.volume_spike)
                            ],
                            choicelist=[1, -1],
                            default=0
                        )

                else:
                    
                    channel_name = f'{channel}_channel'
                    if channel_name in self.df.columns:
                        channel_width = self.df[f'{channel}_channel']
                    else:
                        channel_width = pandas.Series(0, index=lower_values.index)
                    
                    # Breakout conditions
                    bullish_break = self.AVGPRICE > upper_values
                    bearish_break = self.AVGPRICE < lower_values
                    
                    # Continuation confirmation
                    next_open_up = self.Open > self.Close.shift(1)
                    next_open_down = self.Open < self.Close.shift(1)

                    Breakout = (channel_width < numpy.percentile(channel_width, 20)) & (channel_width > numpy.percentile(channel_width, 80))

                    # BUY (Call) Conditions
                    call_conditions = [
                        (bullish_break & next_open_up & Breakout & self.volume_spike),
                        (bullish_break & next_open_up & self.volume_spike)
                    ]
                    
                    # SELL (Put) Conditions
                    put_conditions = [
                        (bearish_break & next_open_down & Breakout & self.volume_spike),
                        (bearish_break & next_open_down & self.volume_spike)
                    ]
                
                    # Generate raw signals
                    signals = numpy.select(
                            condlist=[
                                numpy.logical_or.reduce(call_conditions),
                                numpy.logical_or.reduce(put_conditions)
                            ],
                            choicelist=[1, -1],
                            default=0
                        )
                
                dic[channel] = signals
        return dic

    def SAR(self):
        # 9. Parabolic SAR (Stop and Reverse)
        dic = {}
        for indic in ['SAR', 'SAREXT']:
            if indic in self.df.columns:
                SAR = self.df[indic]
                psar_below = SAR < self.AVGPRICE  # Bullish condition
                psar_above = SAR > self.AVGPRICE  # Bearish condition
                
                # Detect PSAR flips (change in direction)
                psar_flip_up = (psar_below & (SAR.shift(1) >= self.AVGPRICE.shift(1)))
                psar_flip_down = (psar_above & (SAR.shift(1) <= self.AVGPRICE.shift(1)))

                EMA_crosses_above = (self.EMA_c > self.EMA_c.shift(1)) & (self.EMA_c < self.EMA_c.shift(1))
                EMA_crosses_below = (self.EMA_c < self.EMA_c.shift(1)) & (self.EMA_c > self.EMA_c.shift(1))

                # BUY (Call) Conditions
                call_conditions = [
                    # PSAR flip up + trend + volume
                    (psar_flip_up & EMA_crosses_above & self.price_above_ema & self.volume_spike),
                    (psar_flip_up & self.price_above_ema & self.volume_spike)
                ]
                
                # SELL (Put) Conditions
                put_conditions = [
                    # PSAR flip down + trend + volume
                    (psar_flip_down & EMA_crosses_below & self.price_below_ema & self.volume_spike),
                    (psar_flip_down & self.price_below_ema & self.volume_spike)
                ]
                
                # Generate signals
                signals = numpy.select(
                    condlist=[
                        numpy.logical_or.reduce(call_conditions),
                        numpy.logical_or.reduce(put_conditions)
                    ],
                    choicelist=[1, -1],  # 1 for Call, -1 for Put
                    default=0
                )
                dic[indic] = signals
        return dic

    def APO(self):
        # 3. APO (Absolute Price Oscillator)
        if 'APO' in self.df.columns:
            APO = self.df['APO']
            Signal_Line = talib.EMA(APO, timeperiod=11)
            
            # Signal Conditions
            apo_above_signal = APO > Signal_Line
            apo_below_signal = APO < Signal_Line
            
            apo_positive = APO > 0
            apo_negative = APO < 0
            
            # Cross conditions (for exact crossover points)
            apo_cross_up = apo_above_signal & (~apo_above_signal.shift(1).astype(bool))
            apo_cross_down = apo_below_signal & (~apo_below_signal.shift(1).astype(bool))

            # Generate signals
            signals = numpy.select(
                condlist=[
                    (apo_cross_up & apo_positive & self.price_above_ema),
                    (apo_cross_down & apo_negative & self.price_below_ema)
                ],
                choicelist=[1, -1],  # 1 for Call, -1 for Put
                default=0
            )
            return {'APO': signals}

    def AROON(self):
        # 3. AROON (Aroon Indicator)
        if all(col in self.df.columns for col in ['AROON_0', 'AROON_1']):
            aroon_up = self.df['AROON_1']
            aroon_down = self.df['AROON_0']
            # Signal Conditions
            aroon_cross_up = (aroon_up > aroon_down) & (aroon_up.shift(1) <= aroon_down.shift(1))
            aroon_cross_down = (aroon_down > aroon_up) & (aroon_down.shift(1) <= aroon_up.shift(1))
            
            aroon_strong_up = aroon_up > 50
            aroon_strong_down = aroon_down > 50
            
            # Generate signals
            signals = numpy.select(
                condlist=[
                    (aroon_cross_up & aroon_strong_up & self.price_above_ema),
                    (aroon_cross_down & aroon_strong_down & self.price_below_ema)
                ],
                choicelist=[1, -1],  # 1 for Call, -1 for Put
                default=0
            )
            return {'AROON': signals}

    def AROONOSC(self):
        # 4. AROONOSC (Aroon Oscillator)
        if 'AROONOSC' in self.df.columns:
            Aroon_Osc = self.df['AROONOSC']
            # Signal Conditions
            cross_above_zero = (Aroon_Osc > 0) & (Aroon_Osc.shift(1) <= 0)
            cross_below_zero = (Aroon_Osc < 0) & (Aroon_Osc.shift(1) >= 0)
            
            was_oversold = Aroon_Osc.shift(1) < self.support
            was_overbought = Aroon_Osc.shift(1) > self.resistance
            
            # Strong Trend Zones (NEW)
            strong_uptrend = (Aroon_Osc >= 50) & (Aroon_Osc <= 100)  # 50-100
            strong_downtrend = (Aroon_Osc <= -50) & (Aroon_Osc >= -100)  # -50 to -100

            strong_up = Aroon_Osc > strong_uptrend
            strong_down = Aroon_Osc < strong_downtrend
            
            # BUY (Call) Conditions
            call_conditions = [
                (cross_above_zero & was_oversold & self.price_above_ema),
                (strong_up & self.price_above_ema)
            ]
            # SELL (Put) Conditions
            put_conditions = [
                (cross_below_zero & was_overbought & self.price_below_ema),
                (strong_down & self.price_below_ema)
            ]
            
            # Generate signals
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],  # 1 for Call, -1 for Put
                default=0
            )
            return {'AROONOSC': signals}

    def CCI(self):
        # 7. CCI (Commodity Channel Index)
        if 'CCI' in self.df.columns:
            CCI = self.df['CCI']
            # Signal conditions
            cci_cross_above_neg100 = (CCI > -100) & (CCI.shift(1) <= -100)
            cci_cross_below_pos100 = (CCI < 100) & (CCI.shift(1) >= 100)
            
            cci_in_range = (CCI < 200) & (CCI > -200)  # Avoid extreme readings
            
            # Generate signals
            signals = numpy.select(
                condlist=[
                    (cci_cross_above_neg100 & cci_in_range & self.price_above_ema & self.volume_spike),
                    (cci_cross_below_pos100 & cci_in_range & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],  # 1=Call, -1=Put
                default=0
            )
            return {'CCI': signals}

    def CMO(self):
        # 8. CMO (Chande Momentum Oscillator)
        if 'CMO' in self.df.columns:
            CMO = self.df['CMO']
            # Call conditions
            call_cmo_cross = (CMO.shift(1) < -60) & (CMO > -60)
            # Put conditions
            put_cmo_cross = (CMO.shift(1) > 60) & (CMO < 60)
            # Generate signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (call_cmo_cross & self.price_above_ema & self.volume_spike),
                    (put_cmo_cross & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],  # 1=Call, -1=Put
                default=0  # 0 means no signal
            )
            return {'CMO': signals}

    def MOM(self):
        # 39. MOM (Momentum)
        dic = {}
        for x in ['MOM', 'PPO', 'TRIX', 'DEMA', 'EMA', 'TEMA', 'T3', 'KAMA', 'MA', 'TRIMA', 'MIDPOINT', 'MIDPRICE', 'TYPPRICE', 'WCLPRICE', 'WMA', 'AVGPRICE']:
            if x in self.df.columns:
                MOM = self.df[x]
                signal_line = talib.EMA(MOM, timeperiod=11)
                MOM_hist = MOM - signal_line
                # Define crossover logic using .shift(1)
                momentum_cross_above = (MOM > signal_line) & (MOM.shift(1) <= signal_line.shift(1))
                momentum_cross_below = (MOM < signal_line) & (MOM.shift(1) >= signal_line.shift(1))
                # --- Histogram Flip ---
                hist_flip_up = (MOM_hist > 0) & (MOM_hist.shift(1) <= 0)
                hist_flip_down = (MOM_hist < 0) & (MOM_hist.shift(1) >= 0)
                # --- PPO Position ---
                MOM_positive = MOM > 0
                MOM_negative = MOM < 0

                # Final signal array using numpy.select
                signals = numpy.select(
                    condlist=[
                        (momentum_cross_above & hist_flip_up & MOM_positive & self.price_above_ema & self.volume_spike),
                        (momentum_cross_below & hist_flip_down & MOM_negative & self.price_below_ema & self.volume_spike)
                    ],
                    choicelist=[1, -1],
                    default=0  # No signal
                )
                dic[x] = signals
        return dic

    def ADX(self):
        # 2. ADX (Average Directional Index)
        dic = {}
        for x in ['ADX', 'ADXR']:
            if all(col in self.df.columns for col in [x, 'PLUS_DI', 'MINUS_DI']):
                adx = self.df[x]
                plus_di = self.df['PLUS_DI']
                minus_di = self.df['MINUS_DI']
                adx_prev = adx.shift(1)
                # --- Trend Conditions ---
                adx_strong = adx > 25
                adx_rising = adx > adx_prev
                # --- Direction ---
                uptrend = plus_di > minus_di
                downtrend = minus_di > plus_di

                bullish_crossover = (plus_di > minus_di) & (plus_di.shift(1) < minus_di.shift(1))
                bearish_crossover = (minus_di > plus_di) & (minus_di.shift(1) < plus_di.shift(1))
                bullish_fakeout = (plus_di > minus_di) & (plus_di.shift(1) < minus_di.shift(1)) & (adx < adx.shift(1))
                bearish_fakeout = (minus_di > plus_di) & (minus_di.shift(1) < plus_di.shift(1)) & (adx < adx.shift(1))
                bullish_divergence = (self.AVGPRICE > self.AVGPRICE.shift(1)) & (adx < adx.shift(1))
                bearish_divergence = (self.AVGPRICE < self.AVGPRICE.shift(1)) & (adx < adx.shift(1))
                bullish_pullback = (plus_di > minus_di) & (adx > 25) & (self.AVGPRICE < self.AVGPRICE.shift(1))
                bearish_pullback = (minus_di > plus_di) & (adx > 25) & (self.AVGPRICE > self.AVGPRICE.shift(1))

                call_conditions = [
                    (adx_strong & adx_rising & uptrend & self.price_above_ema & self.volume_spike & bullish_crossover & bullish_divergence & bullish_pullback & bearish_fakeout),
                    (adx_strong & adx_rising & uptrend & self.price_above_ema & self.volume_spike & bullish_crossover & bullish_divergence),
                    (adx_strong & adx_rising & uptrend & self.price_above_ema & self.volume_spike)
                ]

                put_conditions = [
                    (adx_strong & adx_rising & downtrend & self.price_below_ema & self.volume_spike & bearish_crossover & bearish_divergence & bearish_pullback & bullish_fakeout),
                    (adx_strong & adx_rising & downtrend & self.price_below_ema & self.volume_spike & bearish_crossover & bearish_divergence),
                    (adx_strong & adx_rising & downtrend & self.price_below_ema & self.volume_spike)
                ]

                signals = numpy.select(
                    condlist=[
                        numpy.logical_or.reduce(call_conditions),
                        numpy.logical_or.reduce(put_conditions)
                    ],
                    choicelist=[1, -1],
                    default=0
                )
                dic [x] = signals
        return dic

    def DX(self):
        if all(col in self.df.columns for col in ['DX', 'PLUS_DM', 'MINUS_DM']):
            DX = self.df['DX']
            plus_dm = self.df['PLUS_DM']
            minus_dm = self.df['MINUS_DM']
            DX_prev = DX.shift(1)
            # --- Trend Conditions ---
            DX_strong = DX > 25
            DX_rising = DX > DX_prev
            # --- Direction ---
            uptrend = plus_dm > minus_dm
            downtrend = minus_dm > plus_dm
            signals = numpy.select(
                condlist=[
                    (DX_strong & DX_rising & uptrend & self.price_above_ema & self.volume_spike),
                    (DX_strong & DX_rising & downtrend & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'DX': signals}

    def Stochastic(self):
        # 51-56. Stochastic variants
        dic = {}
        for stoch_0, stoch_1 in [('STOCHF_0', 'STOCHF_1'), ('STOCHRSI_0', 'STOCHRSI_1'), ('STOCH_0', 'STOCH_1')]:
            if all(col in self.df.columns for col in [stoch_0, stoch_1]):
                _k = self.df[stoch_0]
                _d = self.df[stoch_1]
                # Previous values
                _k_prev = _k.shift(1)
                _d_prev = _d.shift(1)
                # Crossovers
                bullish_cross = (_k > _d) & (_k_prev <= _d_prev)
                bearish_cross = (_k < _d) & (_k_prev >= _d_prev)
                # Oversold/Overbought before the signal
                was_oversold = _k_prev < 20
                was_overbought = _k_prev > 80
                # Confirmation that %D exits overbought/oversold zone
                d_exits_oversold = _d_prev < 20
                d_exits_overbought = _d_prev > 80
                # K/D too close before crossover
                min_kd_diff = 2  # points
                cross_strength = abs(_k_prev - _d_prev) > min_kd_diff

                signals = numpy.select(
                    condlist=[
                        (bullish_cross & was_oversold & self.price_above_ema & self.volume_spike & self.bullish_candle & d_exits_oversold & cross_strength),
                        (bearish_cross & was_overbought & self.price_below_ema & self.volume_spike & self.bearish_candle & d_exits_overbought & cross_strength)
                    ],
                    choicelist=[1, -1],
                    default=0
                )
                dic[stoch_0.rstrip("_0")] = signals
        return dic

    def ULTOSC(self):
        # 68. ULTOSC (Ultimate Oscillator)
        if 'ULTOSC' in self.df.columns:
            ultosc = self.df['ULTOSC']
            uo_prev = ultosc.shift(1)

            # Crossover signals
            uo_cross_above_30 = (ultosc > 30) & (uo_prev <= 30)
            uo_cross_below_70 = (ultosc < 70) & (uo_prev >= 70)

            # Price lower low & UO higher low
            price_low_prev = self.Low.shift(1)
            uo_higher_low = ultosc > uo_prev
            price_lower_low = self.Low < price_low_prev
            bullish_divergence = price_lower_low & uo_higher_low

            # Price higher high & UO lower high
            price_high_prev = self.High.shift(1)
            uo_lower_high = ultosc < uo_prev
            price_higher_high = self.High > price_high_prev
            bearish_divergence = price_higher_high & uo_lower_high

            call_conditions = [
                (uo_cross_above_30 & self.price_above_ema & self.volume_spike & self.bullish_candle),
                (bullish_divergence & self.price_above_ema & self.volume_spike),
                (uo_cross_above_30 & self.price_above_ema & self.volume_spike)
            ]

            put_conditions = [
                (uo_cross_below_70 & self.price_below_ema & self.volume_spike & self.bearish_candle),
                (bearish_divergence & self.price_below_ema & self.volume_spike),
                (uo_cross_below_70 & self.price_below_ema & self.volume_spike)
            ]

            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'ULTOSC': signals}

    def WILLR(self):
        # 70. WILLR (Williams %R)
        if 'WILLR' in self.df.columns:
            willr = self.df['WILLR']
            # Lagged Williams %R for crossover detection
            wr_prev = willr.shift(1)

            # Cross signals
            wr_cross_above_neg80 = (willr > -80) & (wr_prev <= -80)
            wr_cross_below_neg20 = (willr < -20) & (wr_prev >= -20)

            # Price lower low & UO higher low
            price_low_prev = self.Low.shift(1)
            wi_higher_low = willr > wr_prev
            price_lower_low = self.Low < price_low_prev
            bullish_divergence = price_lower_low & wi_higher_low

            # Price higher high & UO lower high
            price_high_prev = self.High.shift(1)
            wi_lower_high = willr < wr_prev
            price_higher_high = self.High > price_high_prev
            bearish_divergence = price_higher_high & wi_lower_high

            call_conditions = [
                (wr_cross_above_neg80 & self.price_above_ema & self.volume_spike & self.bullish_candle),
                (bullish_divergence & self.price_above_ema & self.volume_spike),
                (wr_cross_above_neg80 & self.price_above_ema & self.volume_spike)
            ]

            put_conditions = [
                (wr_cross_below_neg20 & self.price_below_ema & self.volume_spike & self.bearish_candle),
                (bearish_divergence & self.price_below_ema & self.volume_spike),
                (wr_cross_below_neg20 & self.price_below_ema & self.volume_spike)
            ]

            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'WILLR': signals}

    def MFI(self):
        # 32. MFI (Money Flow Index)
        if 'MFI' in self.df.columns:
            MFI = self.df['MFI']
            mfi_prev = MFI.shift(1)

            # Cross detection
            mfi_cross_above_20 = (MFI > 20) & (mfi_prev <= 20)
            mfi_cross_below_80 = (MFI < 80) & (mfi_prev >= 80)
            call_conditions = [
                (mfi_cross_above_20 &  self.price_above_ema &  self.volume_spike),
                ((MFI > 20) &  self.price_above_ema &  self.volume_spike)
            ]

            put_conditions = [
                (mfi_cross_below_80 &  self.price_below_ema &  self.volume_spike),
                ((MFI < 80) &  self.price_below_ema &  self.volume_spike)
            ]

            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'MFI': signals}

    def ADOSC(self):
        # 1. ADOSC (Accumulation/Distribution Oscillator)
        if 'ADOSC' in self.df.columns:
            ADOSC = self.df['ADOSC']
            ADOSC_prev = ADOSC.shift(1)
            chaikin_cross_up = (ADOSC > 0) & (ADOSC_prev <= 0)
            chaikin_cross_down = (ADOSC < 0) & (ADOSC_prev >= 0)
            AVG_diver_up = (self.AVGPRICE < self.AVGPRICE.shift(periods=1)) & (ADOSC > ADOSC.shift(periods=1))
            AVG_diver_dwn = (self.AVGPRICE > self.AVGPRICE.shift(periods=1)) & (ADOSC < ADOSC.shift(periods=1))
            Bullish_Divergence = (self.Low < self.Low.shift(periods=1)) & (ADOSC > ADOSC.shift(periods=1))
            Bearish_Divergence = (self.High > self.High.shift(periods=1)) & (ADOSC < ADOSC.shift(periods=1))

            call_conditions = [
                (chaikin_cross_up & self.price_above_ema & self.volume_spike & AVG_diver_up & Bullish_Divergence),
                (chaikin_cross_up & self.price_above_ema & self.volume_spike)
            ]

            put_conditions = [
                (chaikin_cross_down & self.price_below_ema & self.volume_spike & AVG_diver_dwn & Bearish_Divergence),
                (chaikin_cross_down & self.price_below_ema & self.volume_spike)
            ]

            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'ADOSC': signals}

    def OBV(self):
        # 41-43. OBV variants
        if self.df is not None and all(col in self.df.columns for col in ['OBV', 'OBV_high', 'OBV_low']):
            OBV = self.df['OBV']
            OBV_high = self.df['OBV_high']
            OBV_low = self.df['OBV_low']
            crossover_low = (OBV.shift(1) < OBV_low.shift(1)) & (OBV > OBV_low.shift(1))
            crossover_high = (OBV.shift(1) > OBV_high.shift(1)) & (OBV < OBV_high.shift(1))
            Bullish_Confirmation = (self.AVGPRICE > self.AVGPRICE.shift(periods=1)) & (OBV > OBV.shift(periods=1))
            Bearish_Confirmation = (self.AVGPRICE < self.AVGPRICE.shift(periods=1)) & (OBV < OBV.shift(periods=1))
            Bullish_Divergence = (self.Low < self.Low.shift(periods=1)) & (OBV > OBV.shift(periods=1))
            Bearish_Divergence = (self.High > self.High.shift(periods=1)) & (OBV < OBV.shift(periods=1))
            Support = (OBV > OBV_high.shift(1))
            Resistance = (OBV < OBV_low.shift(1))
            
            call_conditions = [
                (crossover_low & self.price_above_ema & self.volume_spike & Support & Bullish_Confirmation & Bullish_Divergence),
                (crossover_low & self.price_above_ema & self.volume_spike & Support),
                (crossover_low & self.price_above_ema & self.volume_spike)
            ]
            put_conditions = [
                (crossover_high & self.price_below_ema & self.volume_spike & Resistance & Bearish_Confirmation & Bearish_Divergence),
                (crossover_high & self.price_below_ema & self.volume_spike & Resistance),
                (crossover_high & self.price_below_ema & self.volume_spike)
            ]

            signals = numpy.select(
                [
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'OBV': signals}

    def HT_DCPERIOD(self):
        # 93-98. Hilbert Transform indicators
        if 'HT_DCPERIOD' in self.df.columns:
            ht_dcperiod = self.df['HT_DCPERIOD']
            # Rolling mean to detect upward slope
            ht_slope = ht_dcperiod.diff()
            Bullish = (ht_dcperiod > ht_dcperiod.shift(1))
            Bearish = (ht_dcperiod < ht_dcperiod.shift(1))
            Cycle_Shift_Buy = ((ht_dcperiod - ht_dcperiod.shift(1)) > 3)
            Cycle_Shift_Sell = ((ht_dcperiod.shift(1) - ht_dcperiod) > 3)

            # Bullish condition
            call_conditions = [
                ((ht_slope > 0) & Bullish & Cycle_Shift_Buy & self.price_above_ema & self.volume_spike),
                ((ht_slope > 0) & self.price_above_ema & self.volume_spike)
            ]
            # Bearish condition
            put_conditions = [
                ((ht_slope > 0) & Bearish & Cycle_Shift_Sell & self.price_below_ema & self.volume_spike),
                ((ht_slope > 0) & self.price_below_ema & self.volume_spike)
            ]
            # Generate signal
            signals = numpy.select(
                [
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                [1, -1],
                default=0
            )
            return {'HT_DCPERIOD': signals}

    def HT_DCPHASE(self):
        if 'HT_DCPHASE' in self.df.columns:
            ht_dcphase = self.df['HT_DCPHASE']
            # Crossover conditions: Detect crossing above and below zero
            ht_cross_above_zero = (ht_dcphase > 0) & (ht_dcphase.shift(1) <= 0)  # Cross above zero (Call Signal)
            ht_cross_below_zero = (ht_dcphase < 0) & (ht_dcphase.shift(1) >= 0)  # Cross below zero (Put Signal)
            # Call (Buy) Conditions: HT_DCPHASE crosses above 0 (upward cycle)

            call_conditions = [
                (ht_cross_above_zero & self.price_above_ema & self.volume_spike),
                ((ht_dcphase > 0) & self.price_above_ema & self.volume_spike)
            ]
            # Put (Sell) Conditions: HT_DCPHASE crosses below 0 (downward cycle)
            put_conditions = [
                (ht_cross_below_zero & self.price_below_ema & self.volume_spike),
                ((ht_dcphase < 0) & self.price_below_ema & self.volume_spike)
            ]
            # Generate signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],  # 1=Call, -1=Put
                default=0                    # No signal
            )
            return {'HT_DCPHASE': signals}

    def HT_TRENDMODE(self):
        if 'HT_TRENDMODE' in self.df.columns:
            ht_trendmode = self.df['HT_TRENDMODE']
            CMF = (2 * self.AVGPRICE - self.High - self.Low) / (self.High - self.Low) * self.Volume
            CMF = CMF.rolling(11).sum() / self.Volume.rolling(11).sum()
            # Generate signals using numpy.select
            signals = numpy.select(
                condlist=[
                    ((ht_trendmode > 0) & (CMF > 0) & self.price_above_ema & self.volume_spike),
                    ((ht_trendmode < 0) & (CMF < 0) & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'HT_TRENDMODE': signals}

    def HT_PHASOR(self):
        if all(col in self.df.columns for col in ['HT_PHASOR_0', 'HT_PHASOR_1']):
            inphase = self.df['HT_PHASOR_0']
            quadrature = self.df['HT_PHASOR_1']
            Cycle_Phase = numpy.degrees(numpy.arctan2(quadrature, inphase))
            Phasor_Magnitude = numpy.sqrt(inphase**2 + quadrature**2)
            phasor_threshold = numpy.nanpercentile(Phasor_Magnitude, 60)
            # Calculate Cycle Turning Points
            phase_diff = numpy.diff(Cycle_Phase, prepend=Cycle_Phase[0])
            turning_up = (phase_diff > 0) & (Cycle_Phase < 180)       # Trough to rise
            turning_down = (phase_diff < 0) & (Cycle_Phase > 180)     # Peak to fall
            # Apply Magnitude Filter
            phasor_strong = Phasor_Magnitude > phasor_threshold

            Strength_up = (Phasor_Magnitude.shift(1) < Phasor_Magnitude)
            Strength_dwn = (Phasor_Magnitude.shift(1) > Phasor_Magnitude)
            Bullish_Reversal = (Cycle_Phase.shift(1) < 0) & (Cycle_Phase > 0)
            Bearish_Reversal = (Cycle_Phase.shift(1) > 0) & (Cycle_Phase < 0)
            Bullish_Divergence = (self.AVGPRICE < self.AVGPRICE.shift(1)) & (Cycle_Phase > Cycle_Phase.shift(1))
            Bearish_Divergence = (self.AVGPRICE > self.AVGPRICE.shift(1)) & (Cycle_Phase < Cycle_Phase.shift(1))
            Uptrend = (inphase.shift(1) > inphase) & (quadrature.shift(1) < quadrature)
            Downtrend = (inphase.shift(1) < inphase) & (quadrature.shift(1) > quadrature)

            # Define Entry Conditions
            call_conditions = [
                (turning_up & phasor_strong & Uptrend & Strength_up & Bullish_Reversal & Bullish_Divergence & self.price_above_ema & self.volume_spike),
                (turning_up & phasor_strong & Uptrend & Strength_up & self.price_above_ema & self.volume_spike),
                (turning_up & phasor_strong & Uptrend & self.price_above_ema & self.volume_spike)
            ]
            put_conditions = [
                (turning_down & phasor_strong & Downtrend & Strength_dwn & Bearish_Reversal & Bearish_Divergence & self.price_below_ema & self.volume_spike),
                (turning_down & phasor_strong & Downtrend & Strength_dwn & self.price_below_ema & self.volume_spike),
                (turning_down & phasor_strong & Downtrend & self.price_below_ema & self.volume_spike)
            ]

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'HT_PHASOR': signals}

    def HT_SINE(self):
        if all(col in self.df.columns for col in ['HT_SINE_0', 'HT_SINE_1']):
            SINE = self.df['HT_SINE_0']
            LEADSINE = self.df['HT_SINE_1']
            # Detect Crossovers
            sine_cross_above = (SINE > LEADSINE) & (numpy.roll(SINE <= LEADSINE, 1))
            sine_cross_below = (SINE < LEADSINE) & (numpy.roll(SINE >= LEADSINE, 1))
            non_comfirm = (abs(SINE - SINE.shift(1)) < 0.05) & (abs(LEADSINE - LEADSINE.shift(1)) < 0.05)

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (sine_cross_above & self.price_above_ema & self.volume_spike & ~non_comfirm),
                    (sine_cross_below & self.price_below_ema & self.volume_spike & ~non_comfirm)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'HT_SINE': signals}

    def ATR(self):
        # 3. ATR (Average True Range)
        dic = {}
        for x in ['ATR', 'NATR']:
            if x in self.df.columns:
                ATR = self.df[x]
                atr_slope = ATR - ATR.shift(1)
                atr_rising = atr_slope > 0
                Bullish_Breakout = (self.AVGPRICE > self.AVGPRICE.shift(1) + (2 * ATR))
                Bearish_Breakdwn = (self.AVGPRICE < self.AVGPRICE.shift(1) - (2 * ATR))

                # Entry conditions
                call_conditions = [
                    (Bullish_Breakout & self.price_above_ema & atr_rising & self.volume_spike),
                    (self.price_above_ema & atr_rising & self.volume_spike)
                ]
                put_conditions = [
                    (Bearish_Breakdwn & self.price_below_ema & atr_rising & self.volume_spike),
                    (self.price_below_ema & atr_rising & self.volume_spike)
                ]
                # Generate Signals using numpy.select
                signals = numpy.select(
                    condlist=[
                        numpy.logical_or.reduce(call_conditions),
                        numpy.logical_or.reduce(put_conditions)
                    ],
                    choicelist=[1, -1],
                    default=0
                )
                dic[x] = signals
        return dic

    def TRANGE(self):
        # 61. TRANGE (True Range)
        if 'TRANGE' in self.df.columns:
            trange = self.df['TRANGE']
            avg_tr = talib.EMA(trange, timeperiod=11)
            # --- Conditions ---
            tr_spike = trange > 2 * avg_tr
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (tr_spike & self.price_above_ema & self.volume_spike),
                    (tr_spike & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'TRANGE': signals}

    def Houlihan(self):
        # 91. HPR (Highest Price Range)
        if all(col in self.df.columns for col in ['HPR', 'HSI', 'HMA']):
            HPR = self.df['HPR']
            HMA = self.df['HMA']
            HSI = self.df['HSI']
            hpr_cross_up = (HPR > HMA) & (HPR.shift() <= HMA.shift())
            hpr_cross_down = (HPR < HMA) & (HPR.shift() >= HMA.shift())
            call_conditions = [
                (hpr_cross_up & (HSI > 60) & self.price_above_ema & self.volume_spike),
                ((HSI > 60) & self.price_above_ema & self.volume_spike)
            ]
            put_conditions  = [
                (hpr_cross_down & (HSI < 40) & self.price_below_ema & self.volume_spike),
                ((HSI < 40) & self.price_below_ema & self.volume_spike)
                ]
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'HPR': signals}

    def MAD(self):
        # 26-28. MAD variants
        if all(col in self.df.columns for col in ['MAD', 'MAD_lower', 'MAD_upper']):
            MAD = self.df['MAD']
            MAD_upper = self.df['MAD_upper']
            MAD_lower = self.df['MAD_lower']
            call_conditions = [
                ((MAD > MAD_lower) & self.price_above_ema & self.volume_spike)
            ]
            put_conditions = [
                ((MAD < MAD_upper) & self.price_below_ema & self.volume_spike)
            ]
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'MAD': signals}

    def Alligator(self):
        # 87-89. Gator indicators
        if all(col in self.df.columns for col in ['Gator_JAW', 'Gator_TEETH', 'Gator_LIPS', 'Gator_UPPER', 'Gator_LOWER']):
            jaw = self.df['Gator_JAW']
            teeth = self.df['Gator_TEETH']
            lips = self.df['Gator_LIPS']
            Gator_UPPER = self.df['Gator_UPPER']
            Gator_LOWER = self.df['Gator_LOWER']
            # Calculate Gator Oscillator (Difference between components)
            gator_oscillator = (teeth - jaw) + (lips - teeth)
            # Define BUY (Call) Condition
            call_conditions = [
                ((lips > teeth) & (teeth > jaw) & (gator_oscillator > 0) & (Gator_UPPER > 0.1) & (Gator_LOWER > 0.1))
            ]
            # Define SELL (Put) Condition
            put_conditions = [
                ((lips < teeth) & (teeth < jaw) & (gator_oscillator < 0) & (Gator_UPPER > 0.1) & (Gator_LOWER > 0.1))
            ]
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'Alligator': signals}

    def ERI(self):
        # 9. Bear Power
        if all(col in self.df.columns for col in ['Bull_Power', 'Bear_Power']):
            Bull_Power = self.df['Bull_Power']
            Bear_Power = self.df['Bear_Power']

            Bull_Strength = (Bull_Power > 0) & (Bull_Power > Bull_Power.shift(1))
            Bear_Strength = (Bear_Power < 0) & (Bear_Power < Bear_Power.shift(1))

            # Buy (Call) Condition
            call_conditions = [
                (Bull_Strength & (Bull_Power > 0) & (Bear_Power < 0) & (Bull_Power > Bear_Power)),
                ((Bull_Power > 0) & (Bear_Power < 0) & (Bull_Power > Bear_Power))
            ]
            
            # Sell (Put) Condition
            put_conditions = [
                (Bear_Strength & (Bear_Power > 0) & (Bull_Power < 0) & (Bear_Power > Bull_Power)),
                ((Bear_Power > 0) & (Bull_Power < 0) & (Bear_Power > Bull_Power))
            ]
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'ERI': signals}

    def ACO(self):
        # 5. AWO (Awesome Oscillator)
        if all(col in self.df.columns for col in ['AWO', 'ACO']):
            AWO = self.df['AWO']
            ACO = self.df['ACO']
            # AWO and ACO Signals
            ao_up = (AWO > 0) & (AWO > AWO.shift(1))
            ao_down = (AWO < 0) & (AWO < AWO.shift(1))
            ac_up = (ACO > 0) & (ACO > ACO.shift(1)) & (ACO.shift(1) > ACO.shift(2))
            ac_down = (ACO < 0) & (ACO < ACO.shift(1)) & (ACO.shift(1) < ACO.shift(2))
            Bullish_Confirmation = (ACO > 0) & (AWO > 0)
            Bearish_Confirmation = (ACO < 0) & (AWO < 0)
            Bullish_Twin_Peaks = (AWO.shift(2) > AWO.shift(1)) & (AWO.shift(1) < AWO) & (AWO > 0)
            Bearish_Twin_Peaks = (AWO.shift(2) < AWO.shift(1)) & (AWO.shift(1) > AWO) & (AWO < 0)
            Bullish_Saucer = (AWO > 0) & (AWO.shift(2) > AWO.shift(1)) & (AWO.shift(1) < AWO)
            Bearish_Saucer = (AWO < 0) & (AWO.shift(2) < AWO.shift(1)) & (AWO.shift(1) > AWO)
            Bullish_Crossover = (AWO > 0) & (AWO.shift(1) < 0)
            Bearish_Crossover = (AWO < 0) & (AWO.shift(1) > 0)

            # Final Conditions
            call_conditions = [
                (Bullish_Saucer & Bullish_Crossover & Bullish_Twin_Peaks & Bullish_Confirmation & ao_up & ac_up & self.price_above_ema & self.volume_spike),
                (Bullish_Crossover & Bullish_Twin_Peaks & Bullish_Confirmation & ao_up & ac_up & self.price_above_ema & self.volume_spike),
                (Bullish_Twin_Peaks & Bullish_Confirmation & ao_up & ac_up & self.price_above_ema & self.volume_spike),
                (Bullish_Confirmation & ao_up & ac_up & self.price_above_ema & self.volume_spike)
            ]
            put_conditions = [
                (Bearish_Saucer & Bearish_Crossover & Bearish_Twin_Peaks & Bearish_Confirmation & ao_down & ac_down & self.price_below_ema & self.volume_spike),
                (Bearish_Crossover & Bearish_Twin_Peaks & Bearish_Confirmation & ao_down & ac_down & self.price_below_ema & self.volume_spike),
                (Bearish_Twin_Peaks & Bearish_Confirmation & ao_down & ac_down & self.price_below_ema & self.volume_spike),
                (Bearish_Confirmation & ao_down & ac_down & self.price_below_ema & self.volume_spike)
            ]
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    numpy.logical_or.reduce(call_conditions),
                    numpy.logical_or.reduce(put_conditions)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'ACO': signals}

    def Chaikin_Oscillator(self):
        # 11-13. Chaikin Oscillator (CO, CO_Fast, CO_Slow)
        if self.df is not None and all(col in self.df.columns for col in ['CO', 'CO_Fast', 'CO_Slow']):
            CO = self.df['CO']
            CO_Fast = self.df['CO_Fast']
            CO_Slow = self.df['CO_Slow']
            # Indicators
            CO_above_zero = CO > 0
            CO_below_zero = CO < 0
            # Crossovers
            co_crossover_up = (CO_Fast > CO_Slow) & (CO_Fast.shift(1) <= CO_Slow.shift(1))
            co_crossover_down = (CO_Fast < CO_Slow) & (CO_Fast.shift(1) >= CO_Slow.shift(1))
            # Strength confirmation
            co_rising = CO > CO.shift(1)
            co_falling = CO < CO.shift(1)
            # logging.error(f'Chaikin_Oscillator {self.volume_spike}, {self.price_below_ema}.')
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (co_crossover_up & CO_above_zero & co_rising & self.price_above_ema & self.volume_spike),
                    (co_crossover_down & CO_below_zero & co_falling & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'CO': signals}

    def Historical_Volatility(self):
        # 99. HV (Historical Volatility)
        if 'HV' in self.df.columns:
            HV = self.df['HV']
            hv_rising = HV > HV.shift(1)
            high_vol = HV > HV.median()
            low_vol = HV < HV.quantile(0.3)  # No-trade zone
            recent_high = self.AVGPRICE.rolling(window=20).max()
            price_breakout_up = self.AVGPRICE > recent_high.shift(1)
            recent_low = self.AVGPRICE.rolling(window=20).min()
            price_breakout_down = self.AVGPRICE < recent_low.shift(1)
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (hv_rising & high_vol & price_breakout_up & (self.RSI_c > 50) & ~low_vol),
                    (hv_rising & high_vol & price_breakout_down & (self.RSI_c < 50) & ~low_vol)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'HV': signals}

    def Coppock_Curve(self):
        # 15-16. Coppock Curve and Coppock Raw
        if all(col in self.df.columns for col in ['Coppock_Curve', 'Coppock_Raw']):
            Coppock_Curve = self.df['Coppock_Curve']
            Coppock_Raw = self.df['Coppock_Raw']
            coppock_Cu_cross_up = (Coppock_Curve > 0) & (Coppock_Curve.shift(1) < 0)
            coppock_RA_cross_up = (Coppock_Raw > 0) & (Coppock_Raw.shift(1) < 0)
            coppock_Cu_rising = Coppock_Curve > Coppock_Curve.shift(1)
            coppock_Cu_cross_down = (Coppock_Curve < 0) & (Coppock_Curve.shift(1) > 0)
            coppock_Ra_cross_down = (Coppock_Raw < 0) & (Coppock_Raw.shift(1) > 0)
            coppock_Cu_falling = Coppock_Curve < Coppock_Curve.shift(1)
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (coppock_Cu_cross_up & coppock_RA_cross_up & coppock_Cu_rising & self.price_above_ema & self.volume_spike),
                    (coppock_Cu_cross_down & coppock_Ra_cross_down & coppock_Cu_falling & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'Coppock_Curve': signals}

    def TSI(self):
        # 64-65. TSI
        if all(col in self.df.columns for col in ['TSI', 'TSI_signal']):
            TSI = self.df['TSI']
            TSI_Signal = self.df['TSI_signal']
            crosses_above = (TSI > TSI_Signal) & (TSI.shift(1) < TSI_Signal.shift(1))
            crosses_below = (TSI < TSI_Signal) & (TSI.shift(1) > TSI_Signal.shift(1))

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (crosses_above & (TSI > 0) & self.price_above_ema & self.volume_spike & (TSI < -30) & (TSI > TSI.shift(1))),
                    (crosses_below & (TSI < 0) & self.price_below_ema & self.volume_spike & (TSI > 30) & (TSI < TSI.shift(1)))
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'TSI': signals}

    def WRSI(self):
        # 72-75. WRSI variants
        if all(col in self.df.columns for col in ['WRSI', 'WRSI_MA', 'WRSI_Overbought', 'WRSI_Oversold']):
            WRSI = self.df['WRSI']
            WRSI_MA = self.df['WRSI_MA']
            WRSI_Overbought = self.df['WRSI_Overbought']
            WRSI_Oversold = self.df['WRSI_Oversold']
            wrsi_rising = WRSI > WRSI.shift(1)
            wrsi_falling = WRSI < WRSI.shift(1)
            WRSI_MA_up = WRSI > WRSI_MA
            WRSI_MA_dwn = WRSI < WRSI_MA
            crosses_above_OS = (WRSI > WRSI_Oversold) & (WRSI.shift(1) < WRSI_Oversold.shift(1))
            crosses_below_OB = (WRSI < WRSI_Overbought) & (WRSI.shift(1) > WRSI_Overbought.shift(1))
            wrsi_cross_above_30 = (WRSI > 30) & (WRSI.shift(1) <= 30)
            wrsi_cross_below_70 = (WRSI < 70) & (WRSI.shift(1) >= 70)
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (wrsi_cross_above_30 & wrsi_rising & WRSI_MA_up & crosses_above_OS & self.price_above_ema & self.volume_spike),
                    (wrsi_cross_below_70 & wrsi_falling & WRSI_MA_dwn & crosses_below_OB & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'WRSI': signals}

    def KST(self):
        # 101. KST (Know Sure Thing)
        if all(col in self.df.columns for col in ['KST', 'KST_Signal']):
            KST = self.df['KST']
            KST_Signal = self.df['KST_Signal']
            cross_above_signal = (KST > KST_Signal) & (KST.shift(1) < KST_Signal.shift(1))
            cross_below_signal = (KST < KST_Signal) & (KST.shift(1) > KST_Signal.shift(1))
            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (cross_above_signal & (KST > 0) & self.price_above_ema & self.volume_spike),
                    (cross_below_signal & (KST < 0) & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'KST': signals}

    def Ichimoku_Cloud(self):
        # 14. Ichimoku Cloud (Chimoku)
        if self.df is not None and all(col in self.df.columns for col in ['Tenkan', 'Kijun', 'Chikou', 'Senkou_A', 'Senkou_B', 'combined_senkou_Max', 'combined_senkou_Min']):
            Tenkan = self.df['Tenkan']
            Kijun = self.df['Kijun']
            Chikou = self.df['Chikou']
            Senkou_A = self.df['Senkou_A']
            Senkou_B = self.df['Senkou_B']
            combined_senkou_Max = self.df['combined_senkou_Max']
            combined_senkou_Min = self.df['combined_senkou_Min']
            price_above_cloud = self.AVGPRICE > combined_senkou_Max
            price_below_cloud = self.AVGPRICE < combined_senkou_Min
            bullish_crossover = (Tenkan > Kijun) & (Tenkan.shift(1) < Kijun.shift(1))
            bearish_crossover = (Tenkan < Kijun) & (Tenkan.shift(1) > Kijun.shift(1))
            lagging_bullish = Chikou > self.AVGPRICE.shift(11)
            lagging_bearish = Chikou < self.AVGPRICE.shift(11)
            cloud_bullish = Senkou_A > Senkou_B
            cloud_bearish = Senkou_A < Senkou_B

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (price_above_cloud & bullish_crossover & lagging_bullish & cloud_bullish & self.price_above_ema & self.volume_spike),
                    (price_below_cloud & bearish_crossover & lagging_bearish & cloud_bearish & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'Ichimoku': signals}

    def Force_Index(self):
        # 20-22. Force Index variants
        dic = {}
        for fi in ['Force_Index', 'Force_Index_MA', 'Force_Index_max_min']:
            if fi in self.df.columns:
                Force_Index = self.df[fi]
                Force_Index_EMA = talib.EMA(Force_Index, timeperiod=11)
                fi_positive = Force_Index > 0
                fi_ema_rising = Force_Index_EMA > Force_Index_EMA.shift(1)
                fi_negative = Force_Index < 0
                fi_ema_falling = Force_Index_EMA < Force_Index_EMA.shift(1)

                # Generate Signals using numpy.select
                signals = numpy.select(
                    condlist=[
                        (fi_positive & fi_ema_rising & self.price_above_ema & self.volume_spike),
                        (fi_negative & fi_ema_falling & self.price_below_ema & self.volume_spike)
                    ],
                    choicelist=[1, -1],
                    default=0
                )
                dic[fi] = signals
        return dic

    def Rainbow_Oscillator(self):
        if all(col in self.df.columns for col in ['rb', 'rbo', 'rb_slope']):
            rbo = self.df['rbo']
            rb = self.df['rb']
            rb_slope = self.df['rb_slope']
            rb_EMA = talib.EMA(rb, timeperiod=11)
            rb_slope_positive = rb_slope > 0
            rb_slope_negative = rb_slope < 0
            rbo_cross_above_0 = (rbo > 0) & (rbo.shift(1) <= 0)
            rbo_cross_below_0 = (rbo < 0) & (rbo.shift(1) >= 0)

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (rbo_cross_above_0 & rb_slope_positive & (rb > rb_EMA) & (rbo > 10)),
                    (rbo_cross_below_0 & rb_slope_negative & (rb > rb_EMA) & (rbo < -10))
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'Rain': signals}

    def ADL(self):
        # 2. ADL (Accumulation/Distribution Line)
        dic = {}
        for x in ['ADL', 'AD']:
            if x in self.df.columns:
                AD = self.df[x]
                # Calculate the slope of the A/D Line (rate of change)
                AD_slope = AD.diff()
                # Divergence check: Price makes lower low, A/D makes higher low
                price_lower_low = self.AVGPRICE < self.AVGPRICE.shift(1)
                AD_higher_low = AD > AD.shift(1)
                # Divergence check: Price makes higher high, A/D makes lower high
                price_higher_high = self.AVGPRICE > self.AVGPRICE.shift(1)
                AD_lower_high = AD < AD.shift(1)

                # Generate Signals using numpy.select
                signals = numpy.select(
                    condlist=[
                        ((AD_slope > 0) & price_lower_low & AD_higher_low & self.volume_spike & self.price_above_ema),
                        ((AD_slope < 0) & price_higher_high & AD_lower_high & self.volume_spike & self.price_below_ema)
                    ],
                    choicelist=[1, -1],
                    default=0
                )
                dic[x] = signals
        return dic

    def MAMA(self):
        # 29-31. MAMA variants
        if all(col in self.df.columns for col in ['MAMA_0', 'MAMA_1']):
            MAMA = self.df['MAMA_0']
            FAMA = self.df['MAMA_1']
            mama_above_fama = MAMA > FAMA
            mama_below_fama = MAMA < FAMA
            crossover = ((self.AVGPRICE > MAMA) & (self.AVGPRICE > FAMA))
            crossbelow = ((self.AVGPRICE < MAMA) & (self.AVGPRICE < FAMA))

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (mama_above_fama & crossover & self.volume_spike & self.price_below_ema),
                    (mama_below_fama & crossbelow & self.volume_spike & self.price_below_ema)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'MAMA': signals}

    def ROCP(self):
        # 47-49. ROC variants
        if all(col in self.df.columns for col in ['ROC', 'ROCP', 'ROCR100']):
            ROC = self.df['ROC']
            ROCP = self.df['ROCP']
            ROCR100 = self.df['ROCR100']
            roc_positive = ROC > 0  # Positive momentum (ROC > 0)
            roc_negative = ROC < 0  # Negative momentum (ROC < 0)
            rocp_positive = ROCP > 0  # Positive percentage change (ROCP > 0)
            rocp_negative = ROCP < 0  # Negative percentage change (ROCP < 0)
            rocr100_positive = ROCR100 > 1  # Price has increased by more than 1% (ROCR100 > 1)
            rocr100_negative = ROCR100 < 1  # Price has decreased by more than 1% (ROCR100 < 1)

            # Generate Signals using numpy.select
            signals = numpy.select(
                condlist=[
                    (roc_positive & rocp_positive & rocr100_positive & self.price_above_ema & self.volume_spike),
                    (roc_negative & rocp_negative & rocr100_negative & self.price_below_ema & self.volume_spike)
                ],
                choicelist=[1, -1],
                default=0
            )
            return {'ROC': signals}
