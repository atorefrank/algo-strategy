import numpy as np
import requests 
import json 
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from datetime import date, timedelta, datetime
# import qgrid
import time
import bybit
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
# from pprint import pprint
import schedule
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
# client = MongoClient(port=27017)
# db=client.trades
# # Issue the serverStatus command and print the results
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)
pyClient = MongoClient(port=27017)
db=pyClient.backtest_trades
# 1581231260
client = bybit.bybit(test=True, api_key="CVmySp8ZhRZCmSJotq", api_secret="LaY0F7Y76op0L2GLXf1HJpb7SHLXqj4IMtdg")
# 1620606766623
# def get_bybit_bars(symbol, interval, startTime, endTime):
 
#     url = "https://api.bybit.com/v2/public/kline/list"
 
    # startTime = str(startTime)
    # endTime   = str(endTime)
 
#     req_params = {"symbol" : symbol, 'interval' : interval, 'from' : startTime, 'to' : endTime}
 
#     df = pd.DataFrame(json.loads(requests.get(url, params = req_params).text)['result'])
 
#     if (len(df.index) == 0):
#         return None
     
#     df.index = [dt.datetime.fromtimestamp(x) for x in df.open_time]
#     df.open = df.open.astype(float)
#     df.low = df.low.astype(float)
#     df.high = df.high.astype(float)
#     df.close = df.close.astype(float)
#     df.volume = df.volume.astype(int)
#     df.turnover = df.turnover.astype(float)
 
    # return df
def get_bybit_bars(symbol, interval, startTime, endTime):
    result = client.Kline.Kline_get(symbol=symbol, interval=interval, **{'from':endTime}).result()[0]['result']
    # print(result)
    df = pd.DataFrame(result)
    # print(df.head())
 
    if (len(df.index) == 0):
        return None
     
    df.index = [dt.datetime.fromtimestamp(x) for x in df.open_time]
    df.open = df.open.astype(float)
    df.low = df.low.astype(float)
    df.high = df.high.astype(float)
    df.close = df.close.astype(float)
    df.volume = df.volume.astype(int)
    df.turnover = df.turnover.astype(float)
 
    return df

# def place_order(side,symbol,order_type,qty,time_in_force):
#     result = client.Order.Order_new(side=side, symbol=symbol,order_type=order_type,qty=qty,time_in_force=time_in_force).result()
#     return result

# def get_position():
#     position = client.Positions.Positions_myPosition(symbol="BTCUSD").result()
#     return position


def initialize_trade_metrics():
    x = db.trades.delete_many({})
    trades = {
        'position' : 0,
        'last_signal' : 'hold',
        'last_price' : 0,
        'pnl' : 0,
        'balance' : 1000,
        'timestamp': dt.datetime.now(),
        'c' : 0,
        '_id': 1
    }
    # print(x.count_documents())
    result=db.trades.insert_one(trades)
    for item in db.trades.find():
        print(item)
        
    # trades = {
    #     'position' : 0,
    #     'last_signal' : 'hold',
    #     'last_price' : 0,
    #     'pnl' : 0,
    #     'balance' : 1000,
    #     'timestamp': dt.datetime.now(),
    #     'c' : 0,
    #     '_id': 1
    # }
    # try :
    #     result = db.trades.update_one(
    #         { '_id' : 1 },
    #         { "$set": trades }
    #     )
    #     for item in db.trades.find():
    #         print(item)
    # except:
    #     pass
    



if __name__ == "__main__":
    # initialize_trade_metrics()
    days_to_subtract = 30
    start_time = round(time.time() * 1000)
    end_date = datetime.today() - timedelta(days=days_to_subtract)
    print(end_date.timestamp() * 1000)
    end_time = end_date.timestamp() * 1000
    df = get_bybit_bars("BTCUSD","m",start_time,int(end_time))

    # print(df.head())
    print(df.dtypes)