from iqoptionapi.stable_api import IQ_Option
from iqoptionapi import expiration
import pandas

#df.pivot_table(columns=['values'], aggfunc='size')

global Email, Password, API_connected, Instruments, Durations, Cash_to_Trade, Candles_Count, Asset_Information, Candles_Information

Email:str = "ahmedhasan01@msn.com"

Password:str = "@hmed1992i"

API_connected:bool = False

Instruments:str = 'turbo'

Cash_to_Trade:float = 50

Repeat_the_Trade:int = 0

Candles_Count:int = 111

Durations = 1 if (Instruments == 'turbo') else None

Profile_Information = pandas.DataFrame(
    index= [
        
    ],
    columns=[
        "my_info"
        ]
)

Asset_Information = pandas.DataFrame(columns=['active_name', 'active_id', 'active_profit', 'condition', 'schedule'])

my_index = pandas.MultiIndex(levels=[[],[]],
                             codes=[[],[]],
                             names=[u'asset_name', u'id'])
Candles_Information = pandas.DataFrame(
    index=my_index
)

class Money_Heist:
       
    money_heist = None
    
    @classmethod
    def API_starter(cls, email, password):
        
        cls.money_heist = IQ_Option(email, password)
        cls.money_heist.set_session(header={
            "User-Agent": r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            r"(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}, cookie={})
        return cls.money_heist