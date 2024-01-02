import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
from utils import set_period

def run_server(username, password, server, path):
    first_connection = mt5.initialize(
        path=path,
        login=username,
        password=password,
        server=server
    )

    second_connection = mt5.login(
        login=username,
        password=password,
        server=server
    )
    
    return first_connection, second_connection

def retreive_data(symbol="GBPUSD", timeframe="M5"):
    time_frame = set_period(timeframe)
    candles = mt5.copy_rates_from_pos(symbol, time_frame, 1, 1000)[["time", "open", "high", "low", "close"]]
    df = pd.DataFrame(candles)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    ichimoku = ta.ichimoku(df['high'], df['low'], df['close'])
    df = pd.concat([df, ichimoku[0]], axis=1)

    df['ema_21'] = ta.ema(df['close'], length=21)
    df['ema_50'] = ta.ema(df['close'], length=50)
    df['ema_100'] = ta.ema(df['close'], length=100)
    
    return df
