import radio as 無線廣播
import random as 隨機
import utime as 時間
from microbit import button_a as A鈕, button_b as B鈕
import ustruct as 結構


無線廣播.on()

while True :
    if A鈕.is_pressed() :
        位元組資料 = 結構.pack('hhh',14402, 32, 0)
        無線廣播.send_bytes(位元組資料)
    if B鈕.is_pressed() :
        位元組資料 = 結構.pack('hhh',14402, 64, 7)
        無線廣播.send_bytes(位元組資料)    
    時間.sleep_ms(500)
