import ta
import pandas as pd
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
from itertools import product
import pymongo
import time
import schedule
from sanbox import *
import logging
# from flask import Flask
# app = Flask(__name__)

client = pymongo.MongoClient(port=27017)
db=client.backtest_trades
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
# print(serverStatusResult)





def get_stock_backtest_data():
    df = pd.read_csv (r'/Users/campeao/trading/coinbase_bot/timeseries_mod/data/BYBIT_BTCUSD_1.csv')
    df['time'] = pd.to_datetime(df['time'], utc=True, unit='s')
    df = df.set_index('time')
    return df

class StockBacktestData:
  def __init__(self, ticker, start_date, end_date):
    self._ticker = ticker
    self._backtest_start_buffer_days = 365
    self._buffer_days = 90
    # init_start_date, init_end_date = self._get_buffer_start_end_dates(start_date, end_date)
    self._data = self._download_stock_backtest_data()

  
#   def _get_buffer_start_end_dates(self, start_date, end_date):
#     date_fmt = '%Y-%m-%d'
#     init_start_date = datetime.strptime(start_date, date_fmt) - timedelta(
#         days=(self._backtest_start_buffer_days + self._buffer_days)
#         )
    
#     init_start_date = init_start_date.strftime(date_fmt)

#     init_end_date = datetime.strptime(end_date, date_fmt) + timedelta(days=self._buffer_days)

#     if init_end_date > datetime.today():
#       init_end_date = datetime.today()

#     init_end_date = init_end_date.strftime(date_fmt)

#     return init_start_date, init_end_date


#   def _get_backtest_start_date(self, start_date):
#     date_fmt = '%Y-%m-%d'
#     start_date_buffer = datetime.strptime(start_date, date_fmt) - timedelta(
#         days=self._backtest_start_buffer_days
#         )
    
#     start_date_buffer = start_date_buffer.strftime(date_fmt)
#     return start_date_buffer


  def _download_stock_backtest_data(self, ticker, start_date, end_date):
    df = pd.read_csv (r'/Users/campeao/trading/coinbase_bot/timeseries_mod/data/BYBIT_BTCUSD_1.csv')
    df['time'] = pd.to_datetime(df['time'], utc=True, unit='s')
    return df


  def get_stock_backtest_data(self, start_date, end_date):
    # start_date_buffer = self._get_backtest_start_date(start_date)
    # df = self._data[(self._data.index >= start_date_buffer) & (self._data.index <= end_date)]
    df = self._data
    return df.copy()


def strategy_KeltnerChannel_origin(df, **kwargs):
  n = kwargs.get('n', 10)
  data = df.copy()

  k_band = ta.volatility.KeltnerChannel(data.high, data.low, data.close, n)

  data['K_BAND_UB'] = k_band.keltner_channel_hband().round(4)
  data['K_BAND_LB'] = k_band.keltner_channel_lband().round(4)

  data['CLOSE_PREV'] = data.close.shift(1)
  
  data['LONG'] = (data.close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)
  data['EXIT_LONG'] = (data.close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)

  data['SHORT'] = (data.close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)
  data['EXIT_SHORT'] = (data.close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_KeltnerChannel_origin_long(df, **kwargs):
  n = kwargs.get('n', 10)
  data = df.copy()

  k_band = ta.volatility.KeltnerChannel(data.high, data.low, data.close, n)

  data['K_BAND_UB'] = k_band.keltner_channel_hband().round(4)
  data['K_BAND_LB'] = k_band.keltner_channel_lband().round(4)

  data['CLOSE_PREV'] = data.close.shift(1)
  
  data['LONG'] = (data.close <= data.K_BAND_LB) & (data.CLOSE_PREV > data.K_BAND_LB)
  data['EXIT_LONG'] = (data.close >= data.K_BAND_UB) & (data.CLOSE_PREV < data.K_BAND_UB)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_BollingerBands(df, **kwargs):
  n = kwargs.get('n', 10)
  n_rng = kwargs.get('n_rng', 2)
  data = df.copy()

  boll = ta.volatility.BollingerBands(data.close, n, n_rng)

  data['BOLL_LBAND_INDI'] = boll.bollinger_lband_indicator()
  data['BOLL_UBAND_INDI'] = boll.bollinger_hband_indicator()

  data['CLOSE_PREV'] = data.close.shift(1)

  data['LONG'] = data.BOLL_LBAND_INDI == 1
  data['EXIT_LONG'] = data.BOLL_UBAND_INDI == 1

  data['SHORT'] = data.BOLL_UBAND_INDI == 1
  data['EXIT_SHORT'] = data.BOLL_LBAND_INDI == 1

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_BollingerBands_long(df, **kwargs):
  n = kwargs.get('n', 10)
  n_rng = kwargs.get('n_rng', 2)
  data = df.copy()
  
  boll = ta.volatility.BollingerBands(data.close, n, n_rng)

  data['BOLL_LBAND_INDI'] = boll.bollinger_lband_indicator()
  data['BOLL_UBAND_INDI'] = boll.bollinger_hband_indicator()

  data['CLOSE_PREV'] = data.close.shift(1)

  data['LONG'] = data.BOLL_LBAND_INDI == 1
  data['EXIT_LONG'] = data.BOLL_UBAND_INDI == 1

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_MA(df, **kwargs):
  n = kwargs.get('n', 50)
  ma_type = kwargs.get('ma_type', 'sma')
  ma_type = ma_type.strip().lower()
  data = df.copy()
  
  if ma_type == 'sma':
    sma = ta.trend.SMAIndicator(data.close, n)
    data['MA'] = sma.sma_indicator().round(4)
  elif ma_type == 'ema':
    ema = ta.trend.EMAIndicator(data.close, n)
    data['MA'] = ema.ema_indicator().round(4)

  data['CLOSE_PREV'] = data.close.shift(1)

  data['LONG'] = (data.close > data.MA) & (data.CLOSE_PREV <= data.MA)
  data['EXIT_LONG'] = (data.close < data.MA) & (data.CLOSE_PREV >= data.MA)

  data['SHORT'] = (data.close < data.MA) & (data.CLOSE_PREV >= data.MA)
  data['EXIT_SHORT'] = (data.close > data.MA) & (data.CLOSE_PREV <= data.MA)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_MA_long(df, **kwargs):
  n = kwargs.get('n', 50)
  ma_type = kwargs.get('ma_type', 'sma')
  ma_type = ma_type.strip().lower()
  data = df.copy()
  
  if ma_type == 'sma':
    sma = ta.trend.SMAIndicator(data.close, n)
    data['MA'] = sma.sma_indicator().round(4)
  elif ma_type == 'ema':
    ema = ta.trend.EMAIndicator(data.close, n)
    data['MA'] = ema.ema_indicator().round(4)

  data['CLOSE_PREV'] = data.close.shift(1)

  data['LONG'] = (data.close > data.MA) & (data.CLOSE_PREV <= data.MA)
  data['EXIT_LONG'] = (data.close < data.MA) & (data.CLOSE_PREV >= data.MA)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

def strategy_MACD(df, **kwargs):
  n_slow = kwargs.get('n_slow', 26)
  n_fast = kwargs.get('n_fast', 12)
  n_sign = kwargs.get('n_sign', 9)
  data = df.copy()

  macd = ta.trend.MACD(data.close, n_slow, n_fast, n_sign)

  data['MACD_DIFF'] = macd.macd_diff().round(4)
  data['MACD_DIFF_PREV'] = data.MACD_DIFF.shift(1)

  data['LONG'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)

  data['SHORT'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_MACD_long(df, **kwargs):
  n_slow = kwargs.get('n_slow', 26)
  n_fast = kwargs.get('n_fast', 12)
  n_sign = kwargs.get('n_sign', 9)
  data = df.copy()

  macd = ta.trend.MACD(data.close, n_slow, n_fast, n_sign)

  data['MACD_DIFF'] = macd.macd_diff().round(4)
  data['MACD_DIFF_PREV'] = data.MACD_DIFF.shift(1)

  data['LONG'] = (data.MACD_DIFF > 0) & (data.MACD_DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.MACD_DIFF < 0) & (data.MACD_DIFF_PREV >= 0)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_RSI(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  rsi = ta.momentum.RSIIndicator(data.close, n)

  data['RSI'] = rsi.rsi().round(4)
  data['RSI_PREV'] = data.RSI.shift(1)

  data['LONG'] = (data.RSI > 30) & (data.RSI_PREV <= 30)
  data['EXIT_LONG'] = (data.RSI < 70) & (data.RSI_PREV >= 70)

  data['SHORT'] = (data.RSI < 70) & (data.RSI_PREV >= 70)
  data['EXIT_SHORT'] = (data.RSI > 30) & (data.RSI_PREV <= 30)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_RSI_long(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  rsi = ta.momentum.RSIIndicator(data.close, n)

  data['RSI'] = rsi.rsi().round(4)
  data['RSI_PREV'] = data.RSI.shift(1)

  data['LONG'] = (data.RSI > 30) & (data.RSI_PREV <= 30)
  data['EXIT_LONG'] = (data.RSI < 70) & (data.RSI_PREV >= 70)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data



def strategy_WR(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  wr = ta.momentum.WilliamsRIndicator(data.high, data.low, data.close, n)

  data['WR'] = wr.williams_r().round(4)
  data['WR_PREV'] = data.WR.shift(1)

  data['LONG'] = (data.WR > -80) & (data.WR_PREV <= -80)
  data['EXIT_LONG'] = (data.WR < -20) & (data.WR_PREV >= -20)

  data['SHORT'] = (data.WR < -20) & (data.WR_PREV >= -20)
  data['EXIT_SHORT'] = (data.WR > -80) & (data.WR_PREV <= -80)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)
  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_WR_long(df, **kwargs):
  n = kwargs.get('n', 14)
  data = df.copy()

  wr = ta.momentum.WilliamsRIndicator(data.high, data.low, data.close, n)

  data['WR'] = wr.williams_r().round(4)
  data['WR_PREV'] = data.WR.shift(1)

  data['LONG'] = (data.WR > -80) & (data.WR_PREV <= -80)
  data['EXIT_LONG'] = (data.WR < -20) & (data.WR_PREV >= -20)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

def strategy_Stochastic_fast(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.high, data.low, data.close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  data['DIFF'] = data['K'] - data['D']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_Stochastic_fast_long(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.high, data.low, data.close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  data['DIFF'] = data['K'] - data['D']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_Stochastic_slow(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  dd = kwargs.get('dd', 3)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.high, data.low, data.close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  
  ma = ta.trend.SMAIndicator(data.D, dd)
  data['DD'] = ma.sma_indicator().round(4)

  data['DIFF'] = data['D'] - data['DD']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_Stochastic_slow_long(df, **kwargs):
  k = kwargs.get('k', 20)
  d = kwargs.get('d', 5)
  dd = kwargs.get('dd', 3)
  data = df.copy()

  sto = ta.momentum.StochasticOscillator(data.high, data.low, data.close, k, d)

  data['K'] = sto.stoch().round(4)
  data['D'] = sto.stoch_signal().round(4)
  
  ma = ta.trend.SMAIndicator(data.D, dd)
  data['DD'] = ma.sma_indicator().round(4)

  data['DIFF'] = data['D'] - data['DD']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data('ISF.L', '2019-01-01', '2019-12-31')
# strategy_Stochastic_slow(df, k=20, d=5, dd=3)

def strategy_Ichmoku(df, **kwargs):
  n_conv = kwargs.get('n_conv', 9)
  n_base = kwargs.get('n_base', 26)
  n_span_b = kwargs.get('n_span_b', 26)
  data = df.copy()

  ichmoku = ta.trend.IchimokuIndicator(data.high, data.low, n_conv, n_base, n_span_b)

  data['BASE'] = ichmoku.ichimoku_base_line().round(4)
  data['CONV'] = ichmoku.ichimoku_conversion_line().round(4)

  data['DIFF'] = data['CONV'] - data['BASE']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)
  data['EXIT_SHORT'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data


def strategy_Ichmoku_long(df, **kwargs):
  n_conv = kwargs.get('n_conv', 9)
  n_base = kwargs.get('n_base', 26)
  n_span_b = kwargs.get('n_span_b', 26)
  data = df.copy()

  ichmoku = ta.trend.IchimokuIndicator(data.high, data.low, n_conv, n_base, n_span_b)

  data['BASE'] = ichmoku.ichimoku_base_line().round(4)
  data['CONV'] = ichmoku.ichimoku_conversion_line().round(4)

  data['DIFF'] = data['CONV'] - data['BASE']
  data['DIFF_PREV'] = data.DIFF.shift(1)
  
  data['LONG'] = (data.DIFF > 0) & (data.DIFF_PREV <= 0)
  data['EXIT_LONG'] = (data.DIFF < 0) & (data.DIFF_PREV >= 0)

  data['SHORT'] = False
  data['EXIT_SHORT'] = False

  data.LONG = data.LONG.shift(1)
  data.EXIT_LONG = data.EXIT_LONG.shift(1)

  data.SHORT = data.SHORT.shift(1)
  data.EXIT_SHORT = data.EXIT_SHORT.shift(1)

  return data

# df = get_stock_backtest_data('ISF.L', '2019-01-01', '2019-12-31')
# strategy_Ichmoku(df, n_conv=9, n_base=26, n_span_b=26)





 


def prepare_stock_ta_backtest_data(df, strategy, **strategy_params):
  df_strategy = strategy(df, **strategy_params)
  bt_df = df_strategy
  return bt_df




def run_stock_ta_backtest(bt_df, stop_loss_lvl=None):
    balance = 1000

    starting_balance = 1000
    pnl = 0
    position = 0

    bt_df =bt_df.tail(1)
    # print(bt_df)

    stop_loss_lvl = -2

    last_signal = 'hold'

    last_price = 0
    c = 0

    trade_date_start = []
    trade_date_end = []
    trade_days = []
    trade_side = []
    trade_pnl = []
    trade_ret = []

    mongo_id = 1

    cum_value = []
    trades = {}

    for index, row in bt_df.iterrows():
        # check and close any positions
        trade_data = db.trades.find().sort([('timestamp', -1)])
        logging.warning(trade_data.count())
        logging.warning(row)
        trading = {}
        if trade_data.count() > 0:
            
            for trade in trade_data:
                trading = trade
            logging.warning(trading)
            position = trading['position']
            last_signal = trading['last_signal']
            last_price = trading['last_price']
            pnl = trading['pnl']
            balance = trading['balance']
            c = trading['c']
        else:
            trades = {
                'status': "current",
                'position' : 0,
                'last_signal' : 'hold',
                'last_price' : 0,
                'pnl' : 0,
                'balance' : 1000,
                'timestamp': datetime.now(),
                'c' : 0
            }
            result=db.trades.insert_one(trades)

        # print(row)

        if row.EXIT_LONG and last_signal == 'long':
            trade_date_end.append(row.name)
            trade_days.append(c)

            pnl = (row.open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((row.open / last_price - 1) * 100)
            
            balance = balance + row.open * position
            
            position = 0
            last_signal = 'hold'
            c = 0




            # print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
            
        elif row.EXIT_SHORT and last_signal == 'short':
            trade_date_end.append(row.name)
            trade_days.append(c)
            
            pnl = (row.open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((last_price / row.open - 1) * 100)

            balance = balance + pnl

            position = 0
            last_signal = 'hold'

            c = 0

            # trades = {
            #     'status': "current",
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # db.trades.update_one(
            #     { 'status': "current"},
            #     { "$set": trades }
            # )
            # trades = {
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # result=db.trades.insert_one(trades)


            

        # check signal and enter any possible position
        if row.LONG and last_signal != 'long':
            last_signal = 'long'
            last_price = row.open
            trade_date_start.append(row.name)
            trade_side.append('long')

            position = float(balance / row.open)
            cost = position * row.open
            balance = balance - cost

            c = 0

            # trades = {
            #     'status': "current",
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # db.trades.update_one(
            #     { 'status': "current" },
            #     { "$set": trades }
            # )
            # trades = {
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # result=db.trades.insert_one(trades)

        elif row.SHORT and last_signal != 'short':
            last_signal = 'short'
            last_price = row.open
            trade_date_start.append(row.name)
            trade_side.append('short')

            position = float(balance / row.open) * -1
            
            c = 0

            # trades = {
            #     'status': "current",
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # db.trades.update_one(
            #     { 'status': "current" },
            #     { "$set": trades }
            # )

            # trades = {
            #     'position' : position,
            #     'last_signal' : last_signal,
            #     'last_price' : last_price,
            #     'pnl' : pnl,
            #     'balance' : balance,
            #     'timestamp': datetime.now(),
            #     'c' : c
            # }
            # result=db.trades.insert_one(trades)

        # check stop loss
        if stop_loss_lvl:
            # check stop loss
            if last_signal == 'long' and (row.low / last_price - 1) * 100 <= stop_loss_lvl:
                c = c + 1

                trade_date_end.append(row.name)
                trade_days.append(c)

                stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)

                pnl = (stop_loss_price - last_price) * position
                trade_pnl.append(pnl)
                trade_ret.append((stop_loss_price / last_price - 1) * 100)
                
                balance = balance + stop_loss_price * position
                
                position = 0
                last_signal = 'hold'

                c = 0

                # trades = {
                #     'status': "current",
                #     'position' : position,
                #     'last_signal' : last_signal,
                #     'last_price' : last_price,
                #     'pnl' : pnl,
                #     'balance' : balance,
                #     'timestamp': datetime.now(),
                #     'c' : c
                # }
                # db.trades.update_one(
                #     { 'status': "current" },
                #     { "$set": trades }
                # )

                # trades = {
                #     'position' : position,
                #     'last_signal' : last_signal,
                #     'last_price' : last_price,
                #     'pnl' : pnl,
                #     'balance' : balance,
                #     'timestamp': datetime.now(),
                #     'c' : c
                # }
                # result=db.trades.insert_one(trades)

            elif last_signal == 'short' and (last_price / row.high - 1) * 100 <= stop_loss_lvl:
                c = c + 1

                trade_date_end.append(row.name)
                trade_days.append(c)
                
                stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

                pnl = (stop_loss_price - last_price) * position
                trade_pnl.append(pnl)
                trade_ret.append((last_price / stop_loss_price - 1) * 100)

                balance = balance + pnl

                position = 0
                last_signal = 'hold'

                c = 0

                # trades = {
                #     'status': "current",
                #     'position' : position,
                #     'last_signal' : last_signal,
                #     'last_price' : last_price,
                #     'pnl' : pnl,
                #     'balance' : balance,
                #     'timestamp': datetime.now(),
                #     'c' : c
                # }
                # db.trades.update_one(
                #     { 'status': "current" },
                #     { "$set": trades }
                # )

                # trades = {
                #     'position' : position,
                #     'last_signal' : last_signal,
                #     'last_price' : last_price,
                #     'pnl' : pnl,
                #     'balance' : balance,
                #     'timestamp': datetime.now(),
                #     'c' : c
                # }
                # result=db.trades.insert_one(trades)

        
        # compute market value and count days for any possible poisition
        if last_signal == 'hold':
            market_value = balance
        elif last_signal == 'long':
            c = c + 1
            market_value = position * row.close + balance
        else: 
            c = c + 1
            market_value = (row.close - last_price) * position + balance

        logging.warning("Balance is {} and Market Value is {} last_signal is {}".format(balance, market_value, last_signal))
        cum_value.append(market_value)
        
        trades = {
            'status': "current",
            'position' : position,
            'last_signal' : last_signal,
            'last_price' : last_price,
            'pnl' : pnl,
            'balance' : balance,
            'timestamp': datetime.now(),
            'c' : c
        }
        db.trades.update_one(
            { 'status' : "current" },
            { "$set": trades }
        )
        trade_data = db.trades.find().sort([('timestamp', -1)])
        logging.warning(trade_data.count())
        # if trade_data.count() > 0:
        #     trading = {}
        #     for trade in trade_data:
        #         trading = trade
            # print(trading)


    cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
    cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / starting_balance - 1) * 100
    # print(cum_ret_df['CUM_RET'])
    cum_ret_df['BUY_HOLD'] = (bt_df.close / bt_df.open.iloc[0] - 1) * 100
    cum_ret_df['ZERO'] = 0
    cum_ret_df.plot(figsize=(15, 5))
    # plt.show()
    cum_ret_df.iloc[[-1]].round(2)


    size = min(len(trade_date_start), len(trade_date_end))

    tarde_dict = {
        'START': trade_date_start[:size],
        'END': trade_date_end[:size],
        'SIDE': trade_side[:size],
        'DAYS': trade_days[:size],
        'PNL': trade_pnl[:size],
        'RET': trade_ret[:size]
    }

    trade_df = pd.DataFrame(tarde_dict)
    trade_df.head()


    num_trades = trade_df.groupby('SIDE').count()[['START']]
    num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]

    avg_days = trade_df.groupby('SIDE').mean()[['DAYS']]

    avg_ret = trade_df.groupby('SIDE').mean()[['RET']]
    avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean()[['RET']]
    avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean()[['RET']]

    std_ret = trade_df.groupby('SIDE').std()[['RET']]

    detail_df = pd.concat([
                        num_trades, num_trades_win, avg_days,
                        avg_ret, avg_ret_win, avg_ret_loss, std_ret
                        ], axis=1, sort=False)

    detail_df.columns = [
                        'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                        'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                        ]

    detail_df.round(2)

    mv_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['MV'])
    mv_df.head()

    # print(mv_df.head())

    days = len(mv_df)

    roll_max = mv_df.MV.rolling(window=days, min_periods=1).max()
    drawdown_val = mv_df.MV - roll_max
    drawdown_pct = (mv_df.MV / roll_max - 1) * 100

    return {
      'cum_ret_df': cum_ret_df,
      'max_drawdown': {
          'value': round(drawdown_val.min(), 0), 
          'pct': round(drawdown_pct.min(), 2)
          },
      'trade_stats': detail_df
    }



def pick_top_strategy(strategies, df):
    # df = get_stock_backtest_data()

    stop_loss_lvl = [-i for i in range(2, 6, 1)]
    stop_loss_lvl.append(None)

    result_dict = {
        'strategy': [],
        'param': [],
        'stoploss': [],
        'return': [],
        'max_drawdown': []
    }

    for s in strategies:
        func = s['func']
        param = s['param']

        strategy_name = str(func).split(' ')[1]

        param_name = []
        param_list = []

    for k in param:
        param_name.append(k)
        param_list.append(param[k])

    param_dict_list = [dict(zip(param_name, param)) for param in list(product(*param_list))]
    total_param_dict = len(param_dict_list)

    c = 0

    for param_dict in param_dict_list:
        c = c + 1
        print('Running backtest for {} - ({}/{})'.format(strategy_name, c, total_param_dict))

        for l in stop_loss_lvl:
            bt_df = prepare_stock_ta_backtest_data(
                df, 
                func, **param_dict)

            result = run_stock_ta_backtest(bt_df, stop_loss_lvl=l)

            result_dict['strategy'].append(strategy_name)
            result_dict['param'].append(str(param_dict))
            result_dict['stoploss'].append(l)
            result_dict['return'].append(result['cum_ret_df'].iloc[-1, 0])
            result_dict['max_drawdown'].append(result['max_drawdown']['pct'])
    
    # print(len(param_dict_list))


    df = pd.DataFrame(result_dict)
    # print(df.head())
    df = df[df['return'] > 0]
    top_df = df.sort_values(['return', 'max_drawdown'], ascending=[False, False]).head(1).iloc[0]

    if len(top_df):
        return {
            'strategy': eval(top_df['strategy']), 
            'param': eval(top_df['param']), 
            'stoploss': top_df['stoploss']
        }
    else:
        return None

def batch_analysis(bt_df, stop_loss_lvl=None):
    # df2 = df.iloc[[0, -1]]
    # df2 = bt_df.tail(1)
    df2 = bt_df
    # data = get_position()
    # data[""]
    # data[""]
    # data["entry_price"]
    # data["wallet_balance"]
    # pnl = data["cum_realised_pnl"]
    # last_signal = data["side"]
    balance = 1000
    pnl = 0
    position = 0
    mongo_id = 1

    # stop_loss_lvl = -2

    last_signal = 'hold'

    last_price = 0
    c = 0

    trade_date_start = []
    trade_date_end = []
    trade_days = []
    trade_side = []
    trade_pnl = []
    trade_ret = []

    cum_value = []
    for index, row in df2.iterrows():
        # check and close any positions
        # trade_data = db.trades.find().sort([('timestamp', -1)]).limit(1)
        # print(trade_data.count())
        # if trade_data.count() > 0:
        #     trading = {}
        #     for trade in trade_data:
        #         trading = trade
        #     print(trading)
            # position = trading['position']
            # last_signal = trading['last_signal']
            # last_price = trading['last_price']
            # pnl = trading['pnl']
            # balance = trading['balance']
            # c = trading['c']
        if row.EXIT_LONG and last_signal == 'long':
            trade_date_end.append(row.name)
            trade_days.append(c)

            pnl = (row.open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((row.open / last_price - 1) * 100)
            
            balance = balance + row.open * position
            
            position = 0
            last_signal = 'hold'
            c = 0
            trades = {
                'position' : position,
                'last_signal' : last_signal,
                'last_price' : last_price,
                'pnl' : pnl,
                'balance' : balance,
                'timestamp': datetime.now(),
                'c' : c
            }
            db.trades.update_one(
                { '_id' : mongo_id },
                { "$set": trades }
            )


            # print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
            
        elif row.EXIT_SHORT and last_signal == 'short':
            trade_date_end.append(row.name)
            trade_days.append(c)
            
            pnl = (row.open - last_price) * position
            trade_pnl.append(pnl)
            trade_ret.append((last_price / row.open - 1) * 100)

            balance = balance + pnl

            position = 0
            last_signal = 'hold'

            c = 0
            trades = {
                'position' : position,
                'last_signal' : last_signal,
                'last_price' : last_price,
                'pnl' : pnl,
                'balance' : balance,
                'timestamp': datetime.now(),
                'c' : c
            }
            result=db.trades.update_one(
                { '_id' : mongo_id  },
                { "$set": trades }
            )


            

        # check signal and enter any possible position
        if row.LONG and last_signal != 'long':
            last_signal = 'long'
            last_price = row.open
            trade_date_start.append(row.name)
            trade_side.append('long')

            position = float(balance / row.open)
            cost = position * row.open
            balance = balance - cost

            c = 0

            trades = {
                'position' : position,
                'last_signal' : last_signal,
                'last_price' : last_price,
                'pnl' : pnl,
                'balance' : balance,
                'timestamp': datetime.now(),
                'c' : c
            }
            result=db.trades.update_one(
                { '_id' : mongo_id },
                { "$set": trades }
            )

        elif row.SHORT and last_signal != 'short':
            last_signal = 'short'
            last_price = row.open
            trade_date_start.append(row.name)
            trade_side.append('short')

            position = float(balance / row.open) * -1
            
            c = 0

            trades = {
                'position' : position,
                'last_signal' : last_signal,
                'last_price' : last_price,
                'pnl' : pnl,
                'balance' : balance,
                'timestamp': datetime.now(),
                'c' : c
            }
            result=db.trades.update_one(
                { '_id' : mongo_id  },
                { "$set": trades }
            )

        # check stop loss
        if stop_loss_lvl:
            # check stop loss
            if last_signal == 'long' and (row.low / last_price - 1) * 100 <= stop_loss_lvl:
                c = c + 1

                trade_date_end.append(row.name)
                trade_days.append(c)

                stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)

                pnl = (stop_loss_price - last_price) * position
                trade_pnl.append(pnl)
                trade_ret.append((stop_loss_price / last_price - 1) * 100)
                
                balance = balance + stop_loss_price * position
                
                position = 0
                last_signal = 'hold'

                c = 0

                trades = {
                    'position' : position,
                    'last_signal' : last_signal,
                    'last_price' : last_price,
                    'pnl' : pnl,
                    'balance' : balance,
                    'timestamp': datetime.now(),
                    'c' : c
                }
                result=db.trades.update_one(
                    { '_id' : mongo_id  },
                    { "$set": trades }
                )

            elif last_signal == 'short' and (last_price / row.high - 1) * 100 <= stop_loss_lvl:
                c = c + 1

                trade_date_end.append(row.name)
                trade_days.append(c)
                
                stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

                pnl = (stop_loss_price - last_price) * position
                trade_pnl.append(pnl)
                trade_ret.append((last_price / stop_loss_price - 1) * 100)

                balance = balance + pnl

                position = 0
                last_signal = 'hold'

                c = 0

                trades = {
                    'position' : position,
                    'last_signal' : last_signal,
                    'last_price' : last_price,
                    'pnl' : pnl,
                    'balance' : balance,
                    'timestamp': datetime.now(),
                    'c' : c
                }
                result=db.trades.update_one(
                    { '_id' : mongo_id  },
                    { "$set": trades }
                )

        
        # compute market value and count days for any possible poisition
        if last_signal == 'hold':
            market_value = balance
        elif last_signal == 'long':
            c = c + 1
            market_value = position * row.close + balance
        else: 
            c = c + 1
            market_value = (row.close - last_price) * position + balance
            

        cum_value.append(market_value)


    cum_ret_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['CUM_RET'])
    cum_ret_df['CUM_RET'] = (cum_ret_df.CUM_RET / 1000000 - 1) * 100
    cum_ret_df['BUY_HOLD'] = (bt_df.close / bt_df.open.iloc[0] - 1) * 100
    cum_ret_df['ZERO'] = 0
    cum_ret_df.plot(figsize=(15, 5))
    # plt.show()
    cum_ret_df.iloc[[-1]].round(2)


    size = min(len(trade_date_start), len(trade_date_end))

    tarde_dict = {
        'START': trade_date_start[:size],
        'END': trade_date_end[:size],
        'SIDE': trade_side[:size],
        'DAYS': trade_days[:size],
        'PNL': trade_pnl[:size],
        'RET': trade_ret[:size]
    }

    trade_df = pd.DataFrame(tarde_dict)
    trade_df.head()


    num_trades = trade_df.groupby('SIDE').count()[['START']]
    num_trades_win = trade_df[trade_df.PNL > 0].groupby('SIDE').count()[['START']]

    avg_days = trade_df.groupby('SIDE').mean()[['DAYS']]

    avg_ret = trade_df.groupby('SIDE').mean()[['RET']]
    avg_ret_win = trade_df[trade_df.PNL > 0].groupby('SIDE').mean()[['RET']]
    avg_ret_loss = trade_df[trade_df.PNL < 0].groupby('SIDE').mean()[['RET']]

    std_ret = trade_df.groupby('SIDE').std()[['RET']]

    detail_df = pd.concat([
                        num_trades, num_trades_win, avg_days,
                        avg_ret, avg_ret_win, avg_ret_loss, std_ret
                        ], axis=1, sort=False)

    detail_df.columns = [
                        'NUM_TRADES', 'NUM_TRADES_WIN', 'AVG_DAYS', 
                        'AVG_RET', 'AVG_RET_WIN', 'AVG_RET_LOSS', 'STD_RET'
                        ]

    detail_df.round(2)

    mv_df = pd.DataFrame(cum_value, index=bt_df.index, columns=['MV'])
    mv_df.head()

    # print(mv_df.head())

    days = len(mv_df)

    roll_max = mv_df.MV.rolling(window=days, min_periods=1).max()
    drawdown_val = mv_df.MV - roll_max
    drawdown_pct = (mv_df.MV / roll_max - 1) * 100

    return {
      'cum_ret_df': cum_ret_df,
      'max_drawdown': {
          'value': round(drawdown_val.min(), 0), 
          'pct': round(drawdown_pct.min(), 2)
          },
      'trade_stats': detail_df
    }

        # return market_value

# def stream_analysis(bt_df):
#     for index, row in bt_df.iterrows():
#         # check and close any positions
#         trade_data = db.trades.find().sort([('timestamp', -1)]).limit(1)
#         print(trade_data.count())
#         if trade_data.count() > 0:
#             trading = {}
#             for trade in trade_data:
#                 trading = trade
#             print(trading)
#             position = trading['position']
#             last_signal = trading['last_signal']
#             last_price = trading['last_price']
#             pnl = trading['pnl']
#             balance = trading['balance']
#             c = trading['c']
#         if row.EXIT_LONG and last_signal == 'long':
#             trade_date_end.append(row.name)
#             trade_days.append(c)

#             pnl = (row.open - last_price) * position
#             trade_pnl.append(pnl)
#             trade_ret.append((row.open / last_price - 1) * 100)
            
#             balance = balance + row.open * position
            
#             position = 0
#             last_signal = 'hold'
#             c = 0
#             trades = {
#                 'position' : position,
#                 'last_signal' : last_signal,
#                 'last_price' : last_price,
#                 'pnl' : pnl,
#                 'balance' : balance,
#                 'timestamp': datetime.now(),
#                 'c' : c
#             }
#             result=db.trades.insert_one(trades)


#             # print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
            
#         elif row.EXIT_SHORT and last_signal == 'short':
#             trade_date_end.append(row.name)
#             trade_days.append(c)
            
#             pnl = (row.open - last_price) * position
#             trade_pnl.append(pnl)
#             trade_ret.append((last_price / row.open - 1) * 100)

#             balance = balance + pnl

#             position = 0
#             last_signal = 'hold'

#             c = 0
#             trades = {
#                 'position' : position,
#                 'last_signal' : last_signal,
#                 'last_price' : last_price,
#                 'pnl' : pnl,
#                 'balance' : balance,
#                 'timestamp': datetime.now(),
#                 'c' : c
#             }
#             result=db.trades.insert_one(trades)


            

#         # check signal and enter any possible position
#         if row.LONG and last_signal != 'long':
#             last_signal = 'long'
#             last_price = row.open
#             trade_date_start.append(row.name)
#             trade_side.append('long')

#             position = int(balance / row.open)
#             cost = position * row.open
#             balance = balance - cost

#             c = 0

#             trades = {
#                 'position' : position,
#                 'last_signal' : last_signal,
#                 'last_price' : last_price,
#                 'pnl' : pnl,
#                 'balance' : balance,
#                 'timestamp': datetime.now(),
#                 'c' : c
#             }
#             result=db.trades.insert_one(trades)

#         elif row.SHORT and last_signal != 'short':
#             last_signal = 'short'
#             last_price = row.open
#             trade_date_start.append(row.name)
#             trade_side.append('short')

#             position = int(balance / row.open) * -1
            
#             c = 0

#             trades = {
#                 'position' : position,
#                 'last_signal' : last_signal,
#                 'last_price' : last_price,
#                 'pnl' : pnl,
#                 'balance' : balance,
#                 'timestamp': datetime.now(),
#                 'c' : c
#             }
#             result=db.trades.insert_one(trades)

#         # check stop loss
#         if stop_loss_lvl:
#             # check stop loss
#             if last_signal == 'long' and (row.low / last_price - 1) * 100 <= stop_loss_lvl:
#                 c = c + 1

#                 trade_date_end.append(row.name)
#                 trade_days.append(c)

#                 stop_loss_price = last_price + round(last_price * (stop_loss_lvl / 100), 4)

#                 pnl = (stop_loss_price - last_price) * position
#                 trade_pnl.append(pnl)
#                 trade_ret.append((stop_loss_price / last_price - 1) * 100)
                
#                 balance = balance + stop_loss_price * position
                
#                 position = 0
#                 last_signal = 'hold'

#                 c = 0

#                 trades = {
#                     'position' : position,
#                     'last_signal' : last_signal,
#                     'last_price' : last_price,
#                     'pnl' : pnl,
#                     'balance' : balance,
#                     'timestamp': datetime.now(),
#                     'c' : c
#                 }
#                 result=db.trades.insert_one(trades)

#             elif last_signal == 'short' and (last_price / row.high - 1) * 100 <= stop_loss_lvl:
#                 c = c + 1

#                 trade_date_end.append(row.name)
#                 trade_days.append(c)
                
#                 stop_loss_price = last_price - round(last_price * (stop_loss_lvl / 100), 4)

#                 pnl = (stop_loss_price - last_price) * position
#                 trade_pnl.append(pnl)
#                 trade_ret.append((last_price / stop_loss_price - 1) * 100)

#                 balance = balance + pnl

#                 position = 0
#                 last_signal = 'hold'

#                 c = 0

#                 trades = {
#                     'position' : position,
#                     'last_signal' : last_signal,
#                     'last_price' : last_price,
#                     'pnl' : pnl,
#                     'balance' : balance,
#                     'timestamp': datetime.now(),
#                     'c' : c
#                 }
#                 result=db.trades.insert_one(trades)

        
#         # compute market value and count days for any possible poisition
#         if last_signal == 'hold':
#             market_value = balance
#         elif last_signal == 'long':
#             c = c + 1
#             market_value = position * row.close + balance
#         else: 
#             c = c + 1
#             market_value = (row.close - last_price) * position + balance
            
#         cum_value.append(market_value)


def execute_strategy(strategy, strategy_param, stop_loss):
  df = get_stock_backtest_data()

  bt_df = run_stock_ta_backtest(
      df, 
      strategy, **strategy_param)

  result = run_stock_ta_backtest(bt_df, stop_loss_lvl=l)

  return result





strategies = [
  {
    'func': strategy_KeltnerChannel_origin,
    'param': {
      'n': [i for i in range(10, 35, 5)]
    }
  },

  {
    'func': strategy_BollingerBands,
    'param': {
      'n': [i for i in range(10, 35, 5)],
      'n_rng': [1, 2]
    }
  },

  {
    'func': strategy_MA,
    'param': {
      'n': [i for i in range(10, 110, 10)],
      'ma_type': ['sma', 'ema']
    }
  },

  {
    'func': strategy_MACD,
    'param': {
      'n_slow': [i for i in range(10, 16)],
      'n_fast': [i for i in range(20, 26)],
      'n_sign': [i for i in range(5, 11)]
    }
  },

  {
    'func': strategy_RSI,
    'param': {
      'n': [i for i in range(5, 21)]
    }
  },

  {
    'func': strategy_WR,
    'param': {
      'n': [i for i in range(5, 21)]
    }
  },

  {
    'func': strategy_Stochastic_fast,
    'param': {
      'k': [i for i in range(15, 26)],
      'd': [i for i in range(5, 11)]
    }
  },

  {
    'func': strategy_Stochastic_slow,
    'param': {
      'k': [i for i in range(15, 26)],
      'd': [i for i in range(5, 11)],
      'dd': [i for i in range(1, 6)]
    }
  },

  {
    'func': strategy_Ichmoku,
    'param': {
      'n_conv': [i for i in range(5, 16)],
      'n_base': [i for i in range(20, 36)],
      'n_span_b': [26]
    }
  },
]

def find_best_strategy(df):
    top_strategy = pick_top_strategy(strategies, df)
    result = execute_strategy(
        top_strategy['strategy'], top_strategy['param'], top_strategy['stoploss']
    )
    # print(result)

def do_a_fake_trade():
    # df = get_stock_backtest_data()
    # days_to_subtract = 60
    hours_to_subtract = 16.6666666666667
    # raw_start_time = 
    # start_time = int(round(time.time()))
    # start_time = 
    end_date = datetime.today() - timedelta(days=130)
    # print(end_date.timestamp() * 1000)
    end_time = int(round(end_date.timestamp()))
    # print(end_time)
    # df = get_bybit_bars("BTCUSD","240",end_time,start_time)
    # print(df.dtypes)
    df_list = []
    # last_datetime = dt.datetime(2018, 1, 1)
    count = 0
    while True:
        # print(end_date)
        #5 minute intervals are a bit better
        new_df = get_bybit_bars("BTCUSD", "15", end_time, end_time)
        # print(new_df.head())
        # if new_df is None:
        #     break
        if end_date.date() == datetime.today().date():
            break
        df_list.append(new_df)
        # print(max(new_df.index))
        end_date = max(new_df.index)
        # print('End time is {}'.format(end_time))
        
        start_date = end_date + timedelta(hours = hours_to_subtract)
        # print(start_date)
        start_time = int(round(start_date.timestamp()))
        # end_date = start_date- timedelta(hours=hours_to_subtract)
        end_time = int(round(end_date.timestamp()))
        # print(end_date)
        # print(end_date.timestamp() * 1000)
        # end_time = int(round(end_date.timestamp()))
        # print(max(new_df.index))
        count += 1
        # delta = (start_time - end_time)/(3600*24)
        # print('Start time is {} - End time is {} and delta = {}'.format(start_time, end_time, 0))
        # time.sleep(10)
    
    # df = pd.concat(df_list)
    df = pd.concat(df_list)
    compression_opts = dict(method='zip',
                        archive_name='out.csv')  
    df.to_csv('out.zip', index=False,
            compression=compression_opts)  
    # find_best_strategy(df)

    # print(len(df))

    # strategy_Ichmoku(df, n_conv=9, n_base=26, n_span_b=26)

    # strategy_Ichmoku(df, n_conv=9, n_base=26, n_span_b=26)

    # strategy_Stochastic_slow(df, k=20, d=5, dd=3) no

    # strategy_Stochastic_fast(df, k=20, d=5) no

    # strategy_WR(df, n_slow=26, n_fast=12, n_sign=9) -25 to 250

    # strategy_RSI(df, n_slow=26, n_fast=12, n_sign=9) -30

    # strategy_MACD(df, n_slow=26, n_fast=12, n_sign=9) -80

    # strategy_MA(df, n=10, ma_type='ema') -50

    # strategy_BollingerBands(df, n=10, n_rng=2)
    bt_df = prepare_stock_ta_backtest_data(
                df, 
                strategy_BollingerBands, n=10, n_rng=2
            )

    # bt_df = prepare_stock_ta_backtest_data(
    #     df, 
    #     strategy_KeltnerChannel_origin, n=10
    #     )
    # print(bt_df.head())

    run_stock_ta_backtest(bt_df, stop_loss_lvl=-2)
    # pwrint(result)
    # return result

if __name__ == "__main__":
    # find_best_strategy()
    # app.run()
    x = db.trades.delete_many({})
    schedule.every(5).minutes.do(do_a_fake_trade)
    while True:
        schedule.run_pending()
        time.sleep(1)
    # df = get_stock_backtest_data()


    # bt_df = prepare_stock_ta_backtest_data(
    #     df, 
    #     strategy_KeltnerChannel_origin, n=10
    #     )

    # result = run_stock_ta_backtest(bt_df)
    # do_a_fake_trade()
    # result['cum_ret_df'].plot(figsize=(15, 5))
    # print('Max Drawdown:', result['max_drawdown']['pct'], '%')
    # result['trade_stats']



## for 5 mins interval = 12 requests / hr * 16.66666667 hrs/ day 