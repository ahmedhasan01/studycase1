# [
#     'ACO', 'AD', 'ADL', 'ADOSC', 'ADX', 'ADXR', 'APO', 'AROONOSC', 'AROON_0', 'AROON_1',
#     'ATR', 'AVGPRICE', 'AWO', 'BBANDS_0', 'BBANDS_1', 'BBANDS_2', 'BOP', 'Bear_Power', 'Bull_Power', 
#     'CCI', 'CMO', 'CO', 'CO_Fast', 'CO_Slow', 'Chimoku', 'Coppock_Curve', 'Coppock_Raw', 'DEMA', 'DX', 'EMA', 
#     'Force_Index', 'Force_Index_MA', 'Force_Index_max_min', 
#     'Gator_Expansion', 'Gator_JAW', 'Gator_LIPS', 'Gator_LOWER', 'Gator_TEETH', 'Gator_UPPER', 
#     'HMA', 'HPR', 'HSI', 'HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR_0', 'HT_PHASOR_1', 'HT_SINE_0', 'HT_SINE_1',
#     'HT_TRENDLINE', 'HT_TRENDMODE', 'HV', 'KAMA', 'KST', 'KST_Signal', 'Kijun', 'MA', 
#     'MACDEXT_0', 'MACDEXT_1', 'MACDEXT_2', 'MACDFIX_0', 'MACDFIX_1', 'MACDFIX_2',
#     'MACD_0', 'MACD_1', 'MACD_2', 'MAD', 'MAD_lower', 'MAD_upper', 'MAMA_0', 'MAMA_1', 'MEDPRICE', 
#     'MFI', 'MFM', 'MFV', 'MIDPOINT', 'MIDPRICE', 'MINUS_DI', 'MINUS_DM', 'MOM', 'NATR',
#     'OBV', 'OBV_high', 'OBV_low', 'PLUS_DI', 'PLUS_DM', 'PPO', 'ROC', 'ROCP', 'ROCR100', 'RSI', 'SAR',
#     'SAREXT', 'STOCHF_0', 'STOCHF_1', 'STOCHRSI_0', 'STOCHRSI_1', 'STOCH_0', 'STOCH_1', 'Senkou_A', 'Senkou_B', 'T3', 'TEMA', 
#     'TRANGE', 'TRIMA', 'TRIX', 'TSI', 'TSI_signal', 'TYPPRICE', 'Tenkan', 'ULTOSC', 'WCLPRICE', 'WILLR', 'WMA',
#     'WRSI', 'WRSI_MA', 'WRSI_Overbought', 'WRSI_Oversold', 'combined_senkou_Max', 'combined_senkou_Min',
#     'donchian_channel', 'donchian_lower', 'donchian_middle', 'donchian_upper', 
#     'envelope_lower', 'envelope_middle', 'envelope_upper', 'keltner_lower', 'keltner_upper', 'ketlner_channel',
#     'rb', 'rb_slope', 'rbo', 'wick_low', 'wick_up'
# ]

import numpy, pandas, talib, gc
from MH_strategy_factory import Indicator_Signals
from collections import defaultdict
import inspect


class Indicators:
    def __init__(self, candles: list[dict]):
        self.candles = pandas.DataFrame(candles)
        self.candles.sort_values(by='id', ascending=True, ignore_index=True, inplace=True)
        self._parse_candles()
        self._init_params()
        self.talib_indicators = self._get_talib_indicators()
        

    def run(self):
        
        self.compute_indicators()
        signals = Indicator_Signals(self.candles).run()
        signals['from'] = self.candles['from']
        signals = (signals['final_dir'].iloc[-1], signals['Trade_time'].iloc[-1])

        # Get all attributes set in __init__
        init_attrs = list(self.__dict__.keys())
        # Delete them dynamically
        for attr in init_attrs:
            delattr(self, attr)
        gc.collect()

        return signals

    def compute_indicators(self):
        new_cols = []

        # === TA-Lib Indicators ===
        for name in self.talib_indicators:
            func = getattr(talib, name, None)
            if func is None:
                continue

            sig = inspect.signature(func)
            result = self._compute_indicator(func, name, sig)

            if result is None or not self._is_valid_array(result):
                continue

            if isinstance(result, tuple):
                for i, res in enumerate(result):
                    if self._is_valid_array(res):
                        key = f"{name}_{i}"
                        new_cols.append(pandas.Series(res, name=key))
            elif self._is_valid_array(result):
                new_cols.append(pandas.Series(result, name=name))

        # === Custom Indicators ===
        custom_funcs = [
            getattr(self, name) for name in dir(self)
            if callable(getattr(self, name))
            and name.endswith('_indic')
            and name not in ['compute_indic']
        ]

        for func in custom_funcs:
            name = func.__name__
            sig = inspect.signature(func)
            result = self._compute_indicator(func, name, sig)

            if result is None:
                continue

            if isinstance(result, dict):
                for key, val in result.items():
                    if self._is_valid_array(val):
                        new_cols.append(pandas.Series(val, name=key))
            elif self._is_valid_array(result):
                new_cols.append(pandas.Series(result, name=name))

        # === Combine new columns into candles ===
        if new_cols:
            df_new = pandas.concat(new_cols, axis=1)
            self.candles = pandas.concat([self.candles, df_new], axis=1)

    def wicks_indic(self):  # Wicks - Upper Wicks
        
        return {
            'wick_up': (self.High - self.candles[['open', 'close']].max(axis=1)) * 100,
            'wick_low': (self.candles[['open', 'close']].min(axis=1) - self.Low) * 100
        }

    def donchian_indic(self, timeperiod = 11):  # DONCHAN - Donchian Channels
        
        donchian_upper = talib.MAX(self.High, timeperiod=timeperiod)
        donchian_lower = talib.MIN(self.Low, timeperiod=timeperiod)
        
        return {
            'donchian_upper': donchian_upper,
            'donchian_lower': donchian_lower,
            'donchian_middle': (donchian_upper + donchian_lower) / 2,
            'donchian_channel': donchian_upper - donchian_lower
        }

    def envelope_indic(self, timeperiod = 11):  # ENVELOPE - Envelope
        
        EMA = talib.EMA(self.AVGPRICE, timeperiod=timeperiod)
        
        return {
            'envelope_upper': EMA * (1 + 2 / 100),
            'envelope_middle': EMA,
            'envelope_lower': EMA * (1 - 2 / 100)
        }

    def keltner_indic(self, EMA_period = 11, ATR_period = 14):  # KELCHAN - Keltner Channels
        
        EMA = talib.EMA(self.AVGPRICE, timeperiod=EMA_period)
        ATR = talib.ATR(self.High, self.Low, self.Close, timeperiod=ATR_period)
        
        keltner_upper = EMA + (2 * ATR)
        keltner_lower = EMA - (2 * ATR)
        
        return {
            'keltner_upper': keltner_upper,
            'keltner_lower': keltner_lower,
            'ketlner_channel': (keltner_upper - keltner_lower) / EMA
        }

    def MFI_indic(self, timeperiod = 11):  # MFI - Money Flow Index
        
        return {'MFI': talib.MFI(self.High, self.Low, self.AVGPRICE, self.Volume, timeperiod=timeperiod)}

    def AD_indic(self):  # AD - Chaikin A/D Line
        
        return {'AD': talib.AD(self.High, self.Low, self.AVGPRICE, self.Volume)}

    def ADOSC_indic(self, fastperiod = 5, slowperiod = 11):  # ADOSC - Chaikin A/D Oscillator
        
        return {'ADOSC': talib.ADOSC(self.High, self.Low, self.AVGPRICE, self.Volume, fastperiod=fastperiod, slowperiod=slowperiod)}

    def OBV_indic(self, rolling_period = 11):  # OBV - On Balance Volume
        
        OBV = talib.OBV(self.AVGPRICE, self.Volume)
        
        return {
            'OBV': OBV,
            'OBV_high': OBV.rolling(window=rolling_period).max(),
            'OBV_low': OBV.rolling(window=rolling_period).min()
        }

    def Houlihan_Lokey_Inc_Average_indic(self, timeperiod = 11):  # Houlihan Lokey Inc 
        
        HPR =  talib.DIV(self.High, talib.ADD(self.High, self.Low))
        
        return {
            'HPR': HPR,
            'HMA':  talib.EMA(HPR, timeperiod=timeperiod),
            'HSI': ((self.AVGPRICE- self.Low) / (self.High - self.Low)) * 100
        }

    def Moving_Average_Deviation_indic(self, timeperiod = 11):  # MAD - Moving Average Deviation
        
        
        EMA = talib.EMA(self.AVGPRICE, timeperiod=timeperiod)
        
        MAD = self.AVGPRICE - EMA
        
        return {
            'MAD': MAD,
            'MAD_upper': MAD.rolling(timeperiod).quantile(0.75),
            'MAD_lower': MAD.rolling(timeperiod).quantile(0.25)
        }

    def ALLIGATOR_indic(self, jaw_period = 11, jaw_shift = 6, teeth_period = 6, teeth_shift = 3, lips_period = 3, lips_shift = 1):  # ALLIGATOR - Alligator Indicator
        
        Gator_JAW = talib.WMA(self.AVGPRICE, timeperiod=jaw_period).shift(jaw_shift)
        Gator_TEETH = talib.WMA(self.AVGPRICE, timeperiod=teeth_period).shift(teeth_shift) 
        Gator_LIPS = talib.WMA(self.AVGPRICE, timeperiod=lips_period).shift(lips_shift)
        Gator_UPPER = abs(Gator_JAW - Gator_TEETH )
        Gator_LOWER = abs(Gator_TEETH - Gator_LIPS )

        return {
            'Gator_JAW': Gator_JAW,
            'Gator_TEETH': Gator_TEETH,
            'Gator_LIPS': Gator_LIPS,
            'Gator_UPPER': Gator_UPPER,
            'Gator_LOWER': Gator_LOWER,
            'Gator_Expansion': Gator_UPPER + Gator_LOWER
        }

    def Elder_Ray_Index_indic(self, timeperiod = 11):  # ERI - ELDER RAY INDEX
        
        EMA = talib.EMA(self.AVGPRICE, timeperiod=timeperiod)
        
        return {
            'Bull_Power': self.High - EMA,
            'Bear_Power': self.Low - EMA
        }

    def A_oscillators_indic(self, AWO_period = 5, ACO_period = 11):  # OSCILLATORS - Accelerator Oscillator + Awesome_Osillator
        
        AWO = talib.EMA((self.High + self.Low) / 2, timeperiod=AWO_period) - talib.EMA((self.High + self.Low) / 2, timeperiod=ACO_period)

        return {
            'AWO': AWO,
            'ACO': AWO - talib.EMA(AWO, timeperiod=ACO_period)
        }

    def Chaikin_Oscillator_indic(self, CO_Fast_span = 5, CO_Slow_span = 11):  # CHAIKIN_OSCILLATOR - Chaikin Oscillator
        
        MFM = ((self.AVGPRICE- self.Low) - (self.High - self.AVGPRICE)) / (self.High - self.Low)
        MFV = talib.MULT(MFM, self.Volume)
        ADL = MFV.cumsum()
        CO_Fast = ADL.ewm(span=CO_Fast_span, adjust=False).mean() 
        CO_Slow = ADL.ewm(span=CO_Slow_span, adjust=False).mean()

        return {
            'MFM': MFM,
            'MFV': MFV,
            'ADL': ADL,
            'CO_Fast': CO_Fast,
            'CO_Slow': CO_Slow,
            'CO': CO_Fast - CO_Slow
        }

    def Historical_Volatility_indic(self, timeperiod = 11):  # HISTORICAL_VOLATILITY - Historical Volatility
        
        return {'HV': numpy.log(self.AVGPRICE / self.AVGPRICE.shift(1)).rolling(window=timeperiod).std() * numpy.sqrt(60)}

    def Coppock_Curve_indic(self, timeperiod = 11):  # COPPOCK_CURVE - Coppock Curve
        
        Coppock_Raw = talib.ROCP(self.AVGPRICE, timeperiod=timeperiod) * 100 + talib.ROCP(self.AVGPRICE, timeperiod=timeperiod*2) * 100

        return {
            'Coppock_Raw': Coppock_Raw,
            'Coppock_Curve': talib.WMA(Coppock_Raw, timeperiod=timeperiod)
        }

    def TSI_indic(self, timeperiod1 = 11, timeperiod2 = 5):  # TSI - True Strength Index
        
        TSI = 100 * (talib.EMA(talib.EMA(self.AVGPRICE.diff(), timeperiod=timeperiod1), timeperiod=timeperiod2) /  talib.EMA(talib.EMA(abs(self.AVGPRICE.diff()), timeperiod=timeperiod1), timeperiod=timeperiod2))

        return {
            'TSI': TSI,
            'TSI_signal': talib.EMA(TSI, timeperiod=timeperiod1)
        }

    def WRSI_indic(self, timeperiod = 11):  # CHAIKIN_OSCILLATOR - Chaikin Oscillator
        
        RSI = talib.RSI(self.AVGPRICE, timeperiod=timeperiod)
        
        WRSI = talib.WMA(RSI, timeperiod=timeperiod)

        return {
            'WRSI': WRSI,
            'WRSI_MA': talib.EMA(WRSI, timeperiod=timeperiod),
            'WRSI_Overbought': WRSI.rolling(10).quantile(0.90),
            'WRSI_Oversold': WRSI.rolling(1).quantile(0.10)
        }

    def Know_Sure_Thing_indic(self, timeperiod = 11):  # KST - Know Sure Thing
        
        roc1 = talib.ROC(self.AVGPRICE, timeperiod=timeperiod)
        roc2 = talib.ROC(self.AVGPRICE, timeperiod=timeperiod+5)
        roc3 = talib.ROC(self.AVGPRICE, timeperiod=timeperiod+10)
        roc4 = talib.ROC(self.AVGPRICE, timeperiod=timeperiod+20)
        
        KST = (talib.EMA(roc1, timeperiod=timeperiod) * 1 +
                   talib.EMA(roc2, timeperiod=timeperiod+5) * 2 +
                   talib.EMA(roc3, timeperiod=timeperiod+10) * 3 +
                   talib.EMA(roc4, timeperiod=timeperiod+20) * 4)
        
        return {
            'KST': KST,
            'KST_Signal': talib.EMA(KST, timeperiod=timeperiod)
        }

    def Ichimoku_Cloud_indic(self, Tenkan_period = 5, kijun_period = 11):  # IC - Ichimoku Cloud
        
        Tenkan = (talib.MAX(self.High, timeperiod=Tenkan_period) + talib.MIN(self.Low, timeperiod=Tenkan_period)) / 2
        Kijun = (talib.MAX(self.High, timeperiod=kijun_period) + talib.MIN(self.Low, timeperiod=kijun_period)) / 2
        Senkou_A = (Tenkan + Kijun) / 2
        Senkou_B = (talib.MAX(self.High, timeperiod=kijun_period* 2) + talib.MIN(self.Low, timeperiod=kijun_period* 2)) / 2
        Senkou_A = Senkou_A.shift(10)
        Senkou_B = Senkou_B.shift(10)

        return {
            'Tenkan': Tenkan,
            'Kijun': Kijun,
            'Senkou_A': Senkou_A,
            'Senkou_B': Senkou_B,
            'Chimoku': self.AVGPRICE.shift(-10),
            'combined_senkou_Max': Senkou_A.combine(Senkou_B, max),
            'combined_senkou_Min': Senkou_A.combine(Senkou_B, min)
        }

    def Force_Index_indic(self, timeperiod = 11):  # FORCE_INDEX - Force Index
        
        Force_Index = (self.AVGPRICE - self.AVGPRICE.shift(1)) * self.Volume
        
        return {
            'Force_Index': Force_Index,
            'Force_Index_MA': talib.EMA(Force_Index, timeperiod=timeperiod),
            'Force_Index_max_min': talib.MULT(talib.SUB(self.High.combine(self.Low, max), self.Low.combine(self.High, min)), self.Volume)
        }

    def Rainbow_Oscillator_indic(self, timeperiod = 11):  # RAIN_OSC - Rainbow Oscillator
        
        ma_list = [talib.EMA(self.AVGPRICE, timeperiod=timeperiod)]
        for i in range(0, 10):  # 10 EMAs in total
            ma_list.append(talib.EMA(ma_list[i - 1], timeperiod=timeperiod))
        ma_stack_df = pandas.concat(ma_list, axis=1)  # Stack the EMAs into a DataFrame
        hh, ll = talib.MAX(self.AVGPRICE, timeperiod), talib.MIN(self.AVGPRICE, timeperiod)
        rb = 100 * (ma_stack_df.max(axis=1) - ma_stack_df.min(axis=1)) / (hh - ll)
        
        return {
            'rb': rb,
            'rbo': 100 * (self.AVGPRICE - ma_stack_df.mean(axis=1)) / (hh - ll),
            'rb_slope': rb.diff()
        }

    def _parse_candles(self):
        
        self.Open = self.candles['open'].astype(float)
        self.High = self.candles['max'].astype(float)
        self.Low = self.candles['min'].astype(float)
        self.Close = self.candles['close'].astype(float)
        self.Volume = self.candles['volume'].astype(float)
        self.AVGPRICE = talib.AVGPRICE(self.Open, self.High, self.Low, self.Close)
        self.input_map = {
            'open': self.Open,
            'high': self.High,
            'low': self.Low,
            'close': self.Close,
            'volume': self.Volume,
            'real': self.AVGPRICE
        }

    def _get_talib_indicators(self):
        excluded_groups = ['Math Operators', 'Math Transform', 'Pattern Recognition', 'Statistic Functions']
        excluded_funcs = ['MAVP', 'SMA', 'AD', 'OBV', 'ADOSC', 'MFI']
        valid = []

        for group, funcs in talib.get_function_groups().items():
            if group not in excluded_groups:
                valid += [f for f in funcs if f not in excluded_funcs]
        
        return sorted(valid)

    def _init_params(self):
        self.params = defaultdict(dict, {
            'ADOSC': {'fastperiod': 5, 'slowperiod': 11},
            'ADOSC_indic': {'fastperiod': 5, 'slowperiod': 11},
            'ADX': {'timeperiod': 7},
            'ADXR': {'timeperiod': 7},
            'ATR': {'timeperiod': 14},
            'AROON': {'timeperiod': 5},
            'AROONOSC': {'timeperiod': 5},
            'APO': {'fastperiod': 5, 'slowperiod': 12, 'matype': 2},
            'BBANDS': {'timeperiod': 11, 'nbdevup': 2, 'nbdevdn': 2, 'matype': 2},
            'CCI': {'timeperiod': 6},
            'CMO': {'timeperiod': 5},
            'EMA': {'timeperiod': 11},
            'DEMA': {'timeperiod': 5},
            'DX': {'timeperiod': 7},
            'KAMA': {'timeperiod': 5},
            'MA': {'timeperiod': 5, 'matype': 2},
            'MACD': {'fastperiod': 6, 'slowperiod': 13, 'signalperiod': 5},
            'MACDEXT': {'fastperiod': 6, 'slowperiod': 13, 'signalperiod': 5, 'fastmatype': 1, 'slowmatype': 1, 'signalmatype': 1},
            'MACDFIX': {'signalperiod': 5},
            'MAMA': {'fastlimit': 0.5, 'slowlimit': 0.05},
            'MINUS_DI': {'timeperiod': 6},
            'MINUS_DM': {'timeperiod': 6},
            'MOM': {'timeperiod': 4},
            'NATR': {'timeperiod': 7},
            'PLUS_DI': {'timeperiod': 6},
            'PLUS_DM': {'timeperiod': 6},
            'PPO': {'fastperiod': 6, 'slowperiod': 13, 'matype': 2},
            'RSI': {'timeperiod': 5},
            'ROC': {'timeperiod': 4},
            'ROCP': {'timeperiod': 4},
            'ROCR': {'timeperiod': 4},
            'ROCR100': {'timeperiod': 4},
            'SAR': {'acceleration': 0.02, 'maximum': 0.2},
            'SAREXT': {
                'startvalue': 0.02,
                'offsetonreverse': 0,
                'accelerationinitlong': 0.02,
                'accelerationlong': 0.02,
                'accelerationmaxlong': 0.2,
                'accelerationinitshort': 0.02,
                'accelerationshort': 0.02,
                'accelerationmaxshort': 0.2
            },
            'STOCH': {'fastk_period': 5, 'slowk_period': 3, 'slowk_matype': 1, 'slowd_period': 3, 'slowd_matype': 1},
            'STOCHF': {'fastk_period': 5, 'fastd_period': 3, 'fastd_matype': 1},
            'STOCHRSI': {'fastk_period': 5, 'fastd_period': 3, 'timeperiod': 5, 'fastd_matype': 1},
            'T3': {'timeperiod': 5, 'vfactor': 0.7},
            'TEMA': {'timeperiod': 5},
            'TRIMA': {'timeperiod': 5},
            'TRIX': {'timeperiod': 6},
            'ULTOSC': {'timeperiod1': 7, 'timeperiod2': 14, 'timeperiod3': 28},
            'WILLR': {'timeperiod': 5},
            'WMA': {'timeperiod': 5},
            'donchian_indic': {'timeperiod': 11},
            'envelope_indic': {'timeperiod': 11},
            'keltner_indic': {'EMA_period': 11, 'ATR_period': 14},
            'MFI': {'timeperiod': 11},
            'MFI_indic': {'timeperiod': 11},
            'OBV': {'rolling_period': 11},
            'OBV_indic': {'rolling_period': 11},
            'Houlihan_Lokey_Inc_Average_indic': {'timeperiod': 11},
            'Moving_Average_Deviation_indic': {'timeperiod': 11},
            'ALLIGATOR_indic': {'jaw_period': 11, 'jaw_shift': 6, 'teeth_period': 6, 'teeth_shift': 3, 'lips_period': 3, 'lips_shift': 1},
            'Elder_Ray_Index_indic': {'timeperiod': 11},
            'A_oscillators_indic': {'AWO_period': 5, 'ACO_period': 11},
            'Chaikin_Oscillator_indic': {'CO_Fast_span': 5, 'CO_Slow_span': 11},
            'Coppock_Curve_indic': {'timeperiod': 11},
            'Historical_Volatility_indic': {'timeperiod': 11},
            'TSI_indic': {'timeperiod1': 5, 'timeperiod2': 11},
            'WRSI_indic': {'timeperiod': 11},
            'Know_Sure_Thing_indic': {'timeperiod': 11},
            'Ichimoku_Cloud_indic': {'Tenkan_period': 5, 'kijun_period': 11},
            'Force_Index_indic': {'timeperiod': 11},
            'Rainbow_Oscillator_indic': {'timeperiod': 11},
        })

    def _compute_indicator(self, func, name, sig):
        try:
            kwargs = {}
            for param in sig.parameters.values():
                pname = param.name
                if pname in self.input_map:
                    kwargs[pname] = self.input_map[pname]
                elif name in self.params and pname in self.params[name]:
                    kwargs[pname] = self.params[name][pname]

            return func(**kwargs)
        except Exception as e:
            return None

    def _is_valid_array(self, arr):
        # If it's a pandas Series, convert to numpy array
        if isinstance(arr, pandas.Series):
            arr = arr.values

        # If it's a tuple (like from talib.MACD), validate each item
        if isinstance(arr, tuple):
            return all(self._is_valid_array(sub) for sub in arr)

        # Validate array: must be numpy array and not all NaN or all zero
        return (
            isinstance(arr, numpy.ndarray) and
            arr.size > 0 and
            not numpy.all(numpy.isnan(arr)) and
            not numpy.all(arr == 0.0)
        )
