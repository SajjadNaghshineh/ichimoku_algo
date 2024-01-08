import os
os.system("cls")
from mt5_lib import *
from strategy import *
from manage_orders import *
import time
import datetime
import pytz
from error_alert import error_sms_alert
import info

check_cloud = ["nutral"]
counter = 0

while True:
    try:
        counter += 1
        
        today = datetime.datetime.today()
        if today.weekday() in [5, 6]:
            raise ValueError("Today market is close")
        
        if len(check_cloud) >= 100:
            check_cloud = list(check_cloud[-1])
            
        if counter >= 100:
            counter = 2
            
        if counter == 1:
            first_connection, second_connection = run_server(info.USERNAME, info.PASSWORD, info.SERVER, info.PATH)
            
            if not first_connection or not second_connection:
                raise ValueError("Couldn't connect to server ...")
            
            df = retreive_data()
            price_position = find_price_position(df)
            
        if price_position == "Below the cloud":
            while True:
                today = datetime.datetime.today()
                if today.weekday() in [5, 6]:
                    raise ValueError("Today market is close")
                
                change_direction = False
                lower, upper, last_close = cloud_area()
                
                if lower < last_close < upper:
                    while True:
                        today = datetime.datetime.today()
                        if today.weekday() in [5, 6]:
                            raise ValueError("Today market is close")
                        
                        new_lower, new_upper, new_last_close = cloud_area()
                        
                        if new_last_close < new_lower:
                            if check_cloud[-1] == "above":
                                price_position = "Above the cloud"
                                check_cloud.append("below")
                                change_direction = True
                                break
                            else:
                                break
                        elif new_last_close > new_upper:
                            check_cloud.append("above")
                            break
                        
                        time.sleep(5 * 60)
                        
                elif last_close > upper:
                    check_cloud.append("above")
                elif last_close < lower:
                    if check_cloud[-1] == "above":
                        price_position = "Above the cloud"
                        check_cloud.append("below")
                        change_direction = True
                    else:
                        pass
                    
                if change_direction:
                    break
                
                new_df = retreive_data()
                price, max_value, min_value = last_values(new_df)
                
                if price > max_value:
                    allow_one = shadow_condition(new_df, price_position, price)
                    allow_two = moving_condition(new_df)
                    allow_three = ema_21_condition(new_df, price_position)
                    allow_four = stop_loss_condition(new_df, price_position)
                    
                    if allow_one and allow_two and allow_three and allow_four:
                        sl, tp = sl_tp_calculation(new_df, price_position)
                        volume = volume_calculation(new_df, price_position)
                        
                        order_status = place_order("GBPUSD", "buy", sl, tp, volume)
                        
                        if order_status != mt5.TRADE_RETCODE_DONE:
                            raise ValueError("Trade couldn't be done!")
                        
                        price_position = "Above the cloud"
                        break
                    
                time.sleep(5 * 60)
                
        elif price_position == "Above the cloud":
            while True:
                today = datetime.datetime.today()
                if today.weekday() in [5, 6]:
                    raise ValueError("Today market is close")
                
                change_direction = False
                lower, upper, last_close = cloud_area()
                
                if lower < last_close < upper:
                    while True:
                        today = datetime.datetime.today()
                        if today.weekday() in [5, 6]:
                            raise ValueError("Today market is close")
                        
                        new_lower, new_upper, new_last_close = cloud_area()
                        
                        if new_last_close < new_lower:
                            check_cloud.append("below")
                            break
                        elif new_last_close > new_upper:
                            if check_cloud[-1] == "below":
                                price_position = "below the cloud"
                                check_cloud.append("above")
                                change_direction = True
                                break
                            else:
                                break
                        
                        time.sleep(5 * 60)
                        
                elif last_close < lower:
                    check_cloud.append("below")
                elif last_close > upper:
                    if check_cloud[-1] == "below":
                        price_position = "below the cloud"
                        check_cloud.append("above")
                        change_direction = True
                    else:
                        pass
                    
                if change_direction:
                    break
                
                new_df = retreive_data()
                price, max_value, min_value = last_values(new_df)
                
                if price < min_value:
                    allow_one = shadow_condition(new_df, price_position, price)
                    allow_two = moving_condition(new_df)
                    allow_three = ema_21_condition(new_df, price_position)
                    allow_four = stop_loss_condition(new_df, price_position)
                    
                    if allow_one and allow_two and allow_three and allow_four:
                        sl, tp = sl_tp_calculation(new_df, price_position)
                        volume = volume_calculation(new_df, price_position)
                        
                        order_status = place_order("GBPUSD", "sell", sl, tp, volume)
                        
                        if order_status != mt5.TRADE_RETCODE_DONE:
                            raise ValueError("Trade couldn't be done!")
                        
                        price_position = "Below the cloud"
                        break
                    
                time.sleep(5 * 60)
                
    except Exception as e:
        tz = pytz.timezone("Asia/Tehran")
        now = datetime.datetime.now(tz)
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Error: {e} at {now}")
        
        message = f"در ساعت {now} مشکلی برای ربات پیش اومده"
        response = error_sms_alert(info.API_KEY, message)
        print("Error alert sent.")
        break
    else:
        time.sleep(5 * 60)
        