from collections import OrderedDict, Counter, deque
from random import randint, seed, choice
from queue import Queue
import json
import struct as 結構


import PySimpleGUI as sg
from 語音模組 import *
from 聲音模組 import *
from 序列模組 import *


class Data:pass

def init():
    Data.font = '標楷體 32 normal'
    Data.font_small = '標楷體 20 normal'
    Data.title_color = '#484d54'
    Data.theme_background_color = sg.theme_background_color()
    Data.highlight_color = 'red'
    Data.readonly_color = 'PaleGreen1'   
    Data.window_main = make_window_main()
    Data.window_callnum = None
    Data.default_names = '陳怡君\n林雅婷\n張承恩\n王采潔\n陳志明\n楊淑惠'
    
    Data.filename = 'data'
    
    Data.apikey_lowbound = 10000
    Data.apikey_upbound = 32767
    Data.client_code = 32  # 取號代碼
    Data.callnum_code = 64 # 叫號代碼
    Data.counter_max = 30 # 櫃台最大值
    Data.apikey_dict = OrderedDict()
    
    #Data.callnum_type = 'Server'  # 'ServerAndClient'
    
    Data.client_max = 30
    Data.client_queue = deque(maxlen=Data.client_max)
    
    Data.msg_max = 30
    Data.msg_queqe = deque(maxlen=Data.msg_max)
    Data.client_counter = 0
    
    Data.msg_show_num = 8
    Data.msg_called_list = []
    
    Data.tts_start = False
    
    Data.序列連線 = None

    load_data()

def make_window_main():
    
    tab_setup_layout = [
            [sg.Text('設定名單與apikey')],
            [sg.Text('-'*20)],
            [sg.Text('請在左方輸入名單，產生apikey(限30筆)\napikey產生有固定亂數順序')],
            [sg.Multiline('',key='-INPUT_NAMES-', size=(10, 15)),
               sg.Button('====>\n產生apikey\n(取代原有)', key='-MAKE_APIKEY-' ,size=(10,4)),
             sg.Multiline('',key='-APIKEY_RESULT-', size=(18, 15), disabled=True, background_color=Data.readonly_color),
             ],
            [sg.Button('範例名單')],
            [sg.Text('')],
        ]
    
    
    tab_callnum_layout = [
            [sg.Text('')],
            [sg.Text('')],
            [sg.Button('開始取號叫號模擬',key='-START_CALLNUM-')]
        ]
    
    tab_group_layout = [[sg.Tab('設定', tab_setup_layout),
                     sg.Tab('無線叫號', tab_callnum_layout),                     
                     ]]
    
    layout=[
                [ sg.Text('microbit與無線通訊 伺服端程式')],
                [ sg.TabGroup(tab_group_layout)],                
            ]
    
    return sg.Window('主視窗', layout, finalize=True,
                     #enable_close_attempted_event=True,
                     )

def make_window_callnum():
    top_layout = [[ sg.Text('Micro:bit取號叫號模擬',
                            font=Data.font,
                            #justification='center',
                            text_color='yellow',
                            ),
                    sg.Button('取號'),
                    sg.Button('叫號'),
                    sg.Button('read_microbit'),
                    ]]
    top_column = sg.Column(
        top_layout,
        size=(1200,100),
        justification='center',
        #background_color='yellow'
        )

    client_format = f"h:key h:{Data.client_code} h:0"
    callnum_format = f'h:key h:{Data.callnum_code} h:1~{Data.counter_max}'
    bottom_layout = [
            [ sg.Text('取號格式',font=Data.font_small,background_color=Data.title_color) , sg.Text(client_format,font=Data.font),
              sg.Text('叫號格式',font=Data.font_small,background_color=Data.title_color) ,sg.Text(callnum_format,font=Data.font) ],
        
        ]
    bottom_column = sg.Column(
        bottom_layout,
        size=(1200,100), 
        )



    right_layout = [
                     [sg.Text('叫號資訊',font=Data.font,
                     #expand_x=True,
                     #justification='center',
                     background_color=Data.title_color)]
                ]
    #left_layout += [[sg.Text(f'(小明) 來賓00{i}號請至{i}號櫃台',
    right_layout += [[sg.Text('',
                             key = f'-MSG{i}-',
                             font=Data.font,
                             #visible=False
                             )] for i in range(Data.msg_show_num)]

    right_col = sg.Column(
        right_layout,
        size=(900, 600),
        )

    
    left_col = sg.Column(
        [[sg.Text('等待0人',key='-WAIT_TITLE-',font=Data.font,background_color=Data.title_color)],
         [sg.Multiline('',key='-CLIENT_QUEUE-',font=Data.font_small, size=(18, 15), disabled=True,background_color=Data.readonly_color)],
         ],
        size=(350, 600),expand_x=True,
        )


    layout = [
            [top_column],
            [sg.Text('- '*100)] ,
            [left_col,  right_col],
            [sg.Text('- '*100)] ,
            [bottom_column],
        
        ]


    return sg.Window(' test ', layout,
                       resizable=True,
                       finalize=True,
                       #size=(1200,800),
                       
                       )


    return sg.Window('叫號功能', layout, finalize=True,
                     
                     )



def init_callnum():
    
    # prepare call sound
    設定語音音量(100)
    設定語音速度(1)

    音源e = 正弦波(659)
    音源c = 正弦波(523)
    
    聲音e = 音源e.轉成聲音(持續時間=300, 音量=-15.0)
    聲音c = 音源c.轉成聲音(持續時間=500, 音量=-15.0)
    聲音c = 聲音c.淡出(50)

    Data.叫號聲 = 聲音e.串接(聲音c, 交叉淡化=50)

    音源g = 正弦波(392)
    音源b = 正弦波(493)
    音源d = 正弦波(587)

    聲音g = 音源g.轉成聲音(持續時間=300, 音量=-10.0)
    聲音b = 音源b.轉成聲音(持續時間=300, 音量=-10.0)
    聲音d = 音源d.轉成聲音(持續時間=500, 音量=-10.0)
    聲音d = 聲音d.淡出(50)
    
    temp = 聲音g.串接(聲音b, 交叉淡化=50)
    Data.叫號聲2 = temp.串接(聲音d, 交叉淡化=50)

    # init elements
    update_client_ui()
    update_msg_called_ui()
    
    # microbit connect
    Data.序列連線 = 連接microbit(例外錯誤=False, 讀取等待=0)
    
def update_client_ui():
    result = ''
    for num, name in Data.client_queue:
        if name:
            result += f'{num}號來賓({name})\n'
        else:
            result += f'{num}號來賓\n'
    Data.window_callnum['-CLIENT_QUEUE-'].update(result)
    
    wait_num = len(Data.client_queue)
    Data.window_callnum['-WAIT_TITLE-'].update(f'等待{wait_num}人')

def update_msg_called_ui():
    total_called_num = len(Data.msg_called_list)
    if total_called_num == 0 :
        for i in range(Data.msg_show_num):
            Data.window_callnum[f'-MSG{i}-'].update('')
    elif total_called_num <= Data.msg_show_num:
        for i in range(Data.msg_show_num):
            Data.window_callnum[f'-MSG{i}-'].update('')
            
        for i, msg in enumerate(reversed(Data.msg_called_list)):
            Data.window_callnum[f'-MSG{i}-'].update(msg)
    else: # more than show_num
        newer_list = reversed(Data.msg_called_list[-Data.msg_show_num:])
        for i, msg in enumerate(newer_list):
            Data.window_callnum[f'-MSG{i}-'].update(msg)

def make_apikey(values):
    names_str = values['-INPUT_NAMES-']
    if not names_str:
        sg.popup_error('需先輸入名單才能產生apikey')
    else:
        # generate apikey
        Data.apikey_dict = OrderedDict()
        seed(1)
        name_list = names_str.split('\n')
        for n in name_list:
            name = n.strip()
            # find apikey
            found = False
            while not found:
                key = randint(Data.apikey_lowbound, Data.apikey_upbound)
                if not key in Data.apikey_dict:
                    found = True
            Data.apikey_dict[key] = name
        save_data()
        #print(Data.apikey_dict)
        # show in multiline
        show_apikey()
        
def show_apikey():
    result = '名稱 (apikey)\n ==========\n'
    for key, name in Data.apikey_dict.items():
        result += f'{name} (key:{key})\n'
    Data.window_main['-APIKEY_RESULT-'].update(result)
    Data.window_main['-INPUT_NAMES-'].update('')

def save_data():
    with open(Data.filename, 'w', encoding='utf-8') as f:
                json.dump(Data.apikey_dict, f)
    print('資料存檔')

def load_data():
    try:
        with open(Data.filename, 'r', encoding='utf-8') as f:
                Data.apikey_dict = json.load(f)
        print('資料載入')
        show_apikey()
    except FileNotFoundError:
        print('無資料檔')
        return
            
            

def add_client(name=None):
    if len(Data.client_queue) >= Data.client_max:
        print(f'超過等待人數上限{Data.client_max}人')
        return           
    
    Data.client_counter += 1
    Data.client_queue.append((Data.client_counter, name))
    播放聲音(Data.叫號聲)

def handle_msg_and_client():
    # update client queue
    update_client_ui()
    
    #check voice
    if Data.tts_start:
        if not 語音說完了嗎():
            return
        else:
            Data.window_callnum['-MSG0-'].update(background_color=Data.theme_background_color)
            Data.tts_start = False
    #check queue
    if len(Data.msg_queqe) == 0:
        return
    else:
        # got msg
        #print('len: ',len(Data.msg_queqe))
        apikey, code,  value = Data.msg_queqe.popleft()
        
        if code == Data.callnum_code :     
            if len(Data.client_queue) == 0:
                print('沒有客人')
                return
            else:
                # got client
                guest_num, _ = Data.client_queue.popleft()
                name = Data.apikey_dict[apikey]
                name_txt = f'({name})'
                sound_txt = f'來賓{guest_num}號請至{value}號櫃台' 
            
                Data.msg_called_list.append(sound_txt + name_txt)
                
                update_msg_called_ui()
            
                Data.window_callnum['-MSG0-'].update(background_color=Data.highlight_color)
                Data.tts_start = True
                播放聲音(Data.叫號聲2)
                語音合成(sound_txt, 等待=False)
        elif code == Data.client_code :
            name = Data.apikey_dict[apikey]
            add_client(name)
        


def event_loop():
    while True:
        window, event, values = sg.read_all_windows(timeout=200)
              
        # window_main event---------------------------------------
        
        if event == sg.WIN_CLOSED and window == Data.window_main:
            print(window)
            break

        if event == '-START_CALLNUM-' and not Data.window_callnum:
            if len(Data.apikey_dict) == 0 :
                sg.popup_error('需先產生apikey')
            
            else:
                Data.window_main.hide()
                Data.window_callnum = make_window_callnum()
                init_callnum()
            
        if window == Data.window_main and event == '範例名單':
            Data.window_main['-INPUT_NAMES-'].update(Data.default_names)
            
        if window == Data.window_main and event == '-MAKE_APIKEY-':
            make_apikey(values)        
            
        
        # window_callnum event---------------------------------------
        
        if Data.window_callnum and event == '__TIMEOUT__':
            handle_msg_and_client()
        
        if window == Data.window_callnum and (event == sg.WIN_CLOSED) and sg.popup_yes_no('要離開叫號功能嗎?') == 'Yes':
            Data.window_callnum.close()
            Data.window_callnum = None
            Data.window_main.un_hide()
            
        if window == Data.window_callnum and event == '取號':
            key = choice(list(Data.apikey_dict.keys()))
            Data.msg_queqe.append((key, Data.client_code, 0))
        if window == Data.window_callnum and event == '叫號':
            key = choice(list(Data.apikey_dict.keys()))
            num = randint(1,20)
            Data.msg_queqe.append((key, Data.callnum_code, num))
        if window == Data.window_callnum and event == 'read_microbit':
            位元組資料 = Data.序列連線.接收(位元組=6)
            if 位元組資料:
                清單 = 結構.unpack('hhh',位元組資料)
                print(清單)

            
    Data.window_main.close()

def main():
    init()
    event_loop()

if __name__ == '__main__':
    main()