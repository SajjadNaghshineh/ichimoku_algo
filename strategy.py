from utils import format_number

def find_price_position(df):
    price = df.iloc[-1]["close"]
    span_a = df.iloc[-1]["ISA_9"]
    span_b = df.iloc[-1]["ISB_26"]
    
    if price < span_a and price < span_b:
        price_position = "Below the cloud"
    elif price > span_a and price > span_b:
        price_position = "Above the cloud"
    else:
        price_position = "None"
        
    return price_position

def last_values(df):
    price = df.iloc[-1]["close"]
    max_value = df.iloc[-1][["ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]].max()
    min_value = df.iloc[-1][["ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]].min()
    
    return price, max_value, min_value

def shadow_condition(df, price_position, price):
    idx = df[df["close"] == price].index.values[-1]
    
    if price_position == "Below the cloud":
        shadows = []
        for i in range(8, 0, -1):
            df_part = df.iloc[idx-i][["high", "close", "ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]]
            max_value = df_part[["ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]].max()
            
            if df_part["high"] > max_value and df_part["close"] < max_value:
                shadows.append(df_part["high"])
                
        if len(shadows) != 0 and price < max(shadows):
            allowed = False
        else:
            allowed = True
            
    elif price_position == "Above the cloud":
        shadows = []
        for i in range(8, 0, -1):
            df_part = df.iloc[idx-i][["low", "close", "ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]]
            min_value = df_part[["ISA_9", "ISB_26", "ema_21", "ema_50", "ema_100"]].min()
            
            if df_part["low"] < min_value and df_part["close"] > min_value:
                shadows.append(df_part["low"])
                
        if len(shadows) != 0 and price > min(shadows):
            allowed = False
        else:
            allowed = True
            
    return allowed

def moving_condition(df):
    last_candle = df.iloc[-1]
    
    if (last_candle["high"] >= last_candle["ema_21"] >= last_candle["low"]) or (last_candle["high"] >= last_candle["ema_50"] >= last_candle["low"]) or (last_candle["high"] >= last_candle["ema_100"] >= last_candle["low"]):
        allowed = False
    else:
        allowed = True
        
    return allowed

def ema_21_condition(df, price_position):
    last_candle = df.iloc[-1]
    
    if price_position == "Below the cloud":
        if last_candle["ema_21"] > last_candle["ema_50"] and last_candle["ema_21"] > last_candle["ema_100"]:
            allowed = True
        else:
            allowed = False
            
    elif price_position == "Above the cloud":
        if last_candle["ema_21"] < last_candle["ema_50"] and last_candle["ema_21"] < last_candle["ema_100"]:
            allowed = True
        else:
            allowed = False
            
    return allowed

def stop_loss_condition(df, price_position):
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
    
    if abs(sl) > 13.5:
        allowed = False
    else:
        allowed = True
        
    return allowed

def sl_tp_calculation(df, price_position):
    last_candle = df.iloc[-1]
    last_close = last_candle["close"]
    
    if price_position == "Below the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].min()
        
        sl = last_moving
        tp = abs(last_close - last_moving)
        tp = last_close + tp
        
    elif price_position == "Above the cloud":
        last_moving = last_candle[["ema_21", "ema_50", "ema_100"]].max()
        
        sl = last_moving
        tp = abs(last_moving - last_close)
        tp = last_close - tp
        
    return sl, tp

def cloud_area():
    df = retreive_data()
    
    lower = df.iloc[-1][["ISA_9", "ISB_26"]].min()
    upper = df.iloc[-1][["ISA_9", "ISB_26"]].max()
    last_close = df.iloc[-1]["close"]
    
    return lower, upper, last_close
