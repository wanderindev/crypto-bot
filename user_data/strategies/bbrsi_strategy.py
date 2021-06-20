# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from functools import reduce

from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# Strategy based on Bollinger Bands (BB) and Relative Strength Index (RSI)
class BBRSIStrategy(IStrategy):
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "0": 0.319,
        "116": 0.121,
        "285": 0.051,
        "483": 0
    }

    # Optimal stoploss designed for the strategy.
    stoploss = -0.207

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.038
    trailing_stop_positive_offset = 0.138
    trailing_only_offset_is_reached = True

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=10, high=50, default=30,
                           space='buy', optimize=True, load=True)
    buy_rsi_enabled = CategoricalParameter([True, False],
                                           default=True,
                                           space='buy')
    buy_trigger = CategoricalParameter(['bb_lower_1',
                                        'bb_lower_2',
                                        'bb_lower_3'],
                                       default='bb_lower_2', space='buy')
    sell_rsi = IntParameter(low=50, high=90, default=70,
                            space='sell', optimize=True, load=True)
    sell_rsi_enabled = CategoricalParameter([True, False],
                                           default=True,
                                           space='sell')
    sell_trigger = CategoricalParameter(['bb_middle_1',
                                         'bb_upper_1',
                                         'bb_upper_2',
                                         'bb_upper_3',],
                                        default='bb_upper_2', space='sell')

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': True,
        'stoploss_on_exchange_limit_ratio': 0.99
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            "MACD": {
                'macd': {'color': 'blue'},
                'macdsignal': {'color': 'orange'},
            },
            "RSI": {
                'rsi': {'color': 'red'},
            }
        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        # Bollinger bands 1 standard deviation
        bb_1std = ta.BBANDS(dataframe, timeperiod=20, nbdevup=1.0, nbdevdn=1.0)
        dataframe['bb_lowerband_1'] = bb_1std['lowerband']
        dataframe['bb_middleband_1'] = bb_1std['middleband']
        dataframe['bb_upperband_1'] = bb_1std['upperband']

        # Bollinger bands 2 standard deviations
        bb_2std = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband_2'] = bb_2std['lowerband']
        dataframe['bb_upperband_2'] = bb_2std['upperband']

        # Bollinger bands 3 standard deviations
        bb_3std = ta.BBANDS(dataframe, timeperiod=20, nbdevup=3.0, nbdevdn=3.0)
        dataframe['bb_lowerband_3'] = bb_3std['lowerband']
        dataframe['bb_upperband_3'] = bb_3std['upperband']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given
        dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        conditions = []

        # Guards and trends
        if self.buy_rsi_enabled.value:
            conditions.append(dataframe['rsi'] <= self.buy_rsi.value)

        # Triggers
        if self.buy_trigger.value == 'bb_lower_1':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_1'])
        elif self.buy_trigger.value == 'bb_lower_2':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_2'])
        elif self.buy_trigger.value == 'bb_lower_3':
            conditions.append(dataframe['close'] < dataframe['bb_lowerband_3'])

        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given
        dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with sell column
        """
        conditions = []

        # Guards and trends
        if self.sell_rsi_enabled.value:
            conditions.append(dataframe['rsi'] > self.sell_rsi.value)

        # Triggers
        if self.sell_trigger.value == 'bb_middle_1':
            conditions.append(dataframe['close'] > dataframe['bb_middleband_1'])
        elif self.sell_trigger.value == 'bb_upper_1':
            conditions.append(dataframe['close'] > dataframe['bb_upperband_1'])
        elif self.sell_trigger.value == 'bb_upper_2':
            conditions.append(dataframe['close'] > dataframe['bb_upperband_2'])
        elif self.sell_trigger.value == 'bb_upper_3':
            conditions.append(dataframe['close'] > dataframe['bb_upperband_3'])

        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'] = 1
