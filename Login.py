import API_Data, threading, subprocess, gc, requests, time, sys, logging
import pandas as pd

## logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

money = API_Data.Money_Heist.API_starter(API_Data.Email, API_Data.Password).connect()
start = API_Data.Money_Heist.money_heist.get_server_timestamp()
print(money)
print(API_Data.Money_Heist.money_heist.check_connect())
print(API_Data.Money_Heist.money_heist.get_ALL_Binary_ACTIVES_OPCODE())
## assets
assets = [x for x, y in API_Data.Money_Heist.money_heist.get_all_open_time()[API_Data.Instruments].items() if y['open'] == True]
## ----------------------------------------------
candle = pd.DataFrame(API_Data.Money_Heist.money_heist.get_candles('EURUSD', 60, 1050, API_Data.Money_Heist.money_heist.get_server_timestamp())[::-1]).drop('at', axis=1)
### --- change timestamp to datetime //// candle2['from'] = pd.to_datetime(candle2['from'], unit='s')
print(API_Data.Money_Heist.money_heist.get_server_timestamp() - start)
print()




####candle = pd.DataFrame
####for asset in assets:
####    pd.concat([candle, pd.DataFrame(API_Data.Money_Heist.money_heist.get_candles(asset, 60, 1050, API_Data.Money_Heist.money_heist.get_server_timestamp())[::-1])], axis=0, ignore_index=True)