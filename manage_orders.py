import MetaTrader5 as mt5
import sympy as sp
from utils import format_number

def sl_tp_calculation(df, price_position):
    last_candle = df.iloc[-1]
    last_close = last_candle["close"]
    
    if price_position == "Below the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].min()
        
        sl = last_moving
        tp = abs(last_close - last_moving)
        tp = tp * 1.4
        tp = abs(last_close + tp)
        
        sl = float(sl)
        tp = float(tp)
        
    elif price_position == "Above the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].max()
        
        sl = last_moving
        tp = abs(last_moving - last_close)
        tp = tp * 1.4
        tp = abs(last_close - tp)
        
        sl = float(sl)
        tp = float(tp)
        
    return round(sl, 4), round(tp, 4)

def volume_calculation(df, price_position):
    user_info = mt5.account_info()
    balance = user_info[10]
    balance = int(balance / 100)
    
    last_candle = df.iloc[-1]
    last_close = last_candle["close"]
    last_close = format_number(str(last_close))
    
    if price_position == "Below the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].min()
    elif price_position == "Above the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].max()
        
    last_moving = format_number(str(last_moving))
    
    sl = last_close - last_moving
    sl = sl / 10
    
    x = sp.symbols("x")
    equation = sp.Eq(balance, sl * x)
    solution = sp.solve(equation, x)
    
    lot_size = eval(str(solution[0]))
    lot_size = lot_size / 10
    
    return round(lot_size, 2)

def place_order(symbol, order_type, sl, tp, volume):
    price = mt5.symbol_info_tick(symbol).ask
    
    if order_type == "sell":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
    elif order_type == "buy":
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
    result = mt5.order_send(request)
    order_status = result.retcode
    
    return order_status
