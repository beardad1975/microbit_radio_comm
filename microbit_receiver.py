import radio as 無線廣播
import utime as 時間
from microbit import uart as 序列
from microbit import display as 燈光, Image as 圖示

序列.init(115200)

無線廣播.on()

while True :
    接收位元組 = 無線廣播.receive_bytes()
    if 接收位元組:
        序列.write(接收位元組)
        燈光.show('.')
        
    時間.sleep_ms(50)
    燈光.clear()
    
