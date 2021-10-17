from collections import OrderedDict
from random import randint

import PySimpleGUI as sg
from 語音模組 import *
from 聲音模組 import *

class Data:pass

def init():
    Data.font = '標楷體 32 normal'
    Data.font_small = '標楷體 20 normal'
    Data.title_color = 'SlateBlue1'
    Data.theme_background_color = sg.theme_background_color()
    Data.highlight_color = 'red'
    Data.readonly_color = 'PaleGreen1'   
    Data.window_main = make_window_main()
    Data.window_callnum = None
    Data.default_names = '陳怡君\n林雅婷\n張承恩\n王采潔\n陳志明\n楊淑惠'
    
    Data.apikey_lowbound = 10000
    Data.apikey_upbound = 32767
    Data.apikey_dict = OrderedDict()

def make_window_main():
    
    tab_setup_layout = [
            [sg.Text('設定名單與apikey')],
            [sg.Text('-'*20)],
            [sg.Text('請在左方輸入名單，產生apikey')],
            [sg.Multiline('',key='-INPUT_NAMES-', size=(10, 15)),
               sg.Button('====>\n產生apikey', key='-MAKE_APIKEY-' ,size=(10,3)),
             sg.Multiline('',key='-APIKEY_RESULT-', size=(18, 15), disabled=True, background_color=Data.readonly_color),
             ],
            [sg.Button('範例名單'),sg.Button('輸出apikey(csv)'),sg.Button('清空apikey')],
            [sg.Text('')],
        ]
    
    
    tab_callnum_layout = [[sg.Button('開始microbit叫號',key='-START_CALLNUM-')]]
    
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
    top_layout = [[ sg.Text('建國自造教育與科技中心microbit叫號',
                            font=Data.font,
                            #justification='center',
                            text_color='yellow',
                            ),
                    sg.Button('改傳送'),
                    sg.Button('改叫號'),
                    ]]
    top_column = sg.Column(
        top_layout,
        size=(1200,100),
        justification='center',
        #background_color='yellow'
        )


    bottom_layout = [
            [ sg.Text('格式',font=Data.font,background_color=Data.title_color) , sg.Text("'hh' 4位元組",font=Data.font),
              sg.Text('佇列',font=Data.font,background_color=Data.title_color) ,sg.Text('5項等待中',font=Data.font) ],
        
        ]
    bottom_column = sg.Column(
        bottom_layout,
        size=(1200,100), 
        )



    left_layout = [
                     [sg.Text('叫號資訊',font=Data.font,
                     #expand_x=True,
                     #justification='center',
                     background_color=Data.title_color)]
                ]
    #left_layout += [[sg.Text(f'(小明) 來賓00{i}號請至{i}號櫃台',
    left_layout += [[sg.Text('',
                             key = f'-CALL{i}-',
                             font=Data.font,
                             #visible=False
                             )] for i in range(7)]

    left_col = sg.Column(
        left_layout,
        size=(900, 600),
        )

    text = '王小明(10次)\n陳小莉(1次)'
    right_col = sg.Column(
        [[sg.Text('已傳送',font=Data.font,background_color=Data.title_color)],
         [sg.Multiline(text,key='-SEND_NAMES-',font=Data.font_small, size=(14, 15), disabled=True,background_color=Data.readonly_color)],
         ],
        size=(300, 600),expand_x=True,
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
    
    設定語音音量(100)
    設定語音速度(1)

    音源e = 正弦波(659)
    音源c = 正弦波(523)

    聲音e = 音源e.轉成聲音(持續時間=400, 音量=-7.0)
    聲音c = 音源c.轉成聲音(持續時間=700, 音量=-5.0)
    聲音c = 聲音c.淡出(100)

    Data.叫號聲 = 聲音e.串接(聲音c, 交叉淡化=100)

def make_apikey(values):
    names_str = values['-INPUT_NAMES-']
    if not names_str:
        sg.popup_error('需先輸入名單才能產生apikey')
    else:
        # generate apikey
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
        print(Data.apikey_dict)    

def event_loop():
    while True:
        window, event, values = sg.read_all_windows()
        
        # window_main event---------------------------------------
        
        if event == sg.WIN_CLOSED and window == Data.window_main:
            print(window)
            break

        if event == '-START_CALLNUM-' and not Data.window_callnum:
            Data.window_main.hide()
            Data.window_callnum = make_window_callnum()
            init_callnum()
            
        if window == Data.window_main and event == '範例名單':
            Data.window_main['-INPUT_NAMES-'].update(Data.default_names)
            
        if window == Data.window_main and event == '-MAKE_APIKEY-':
            make_apikey(values)        
            
        
        # window_callnum event---------------------------------------
        
        if window == Data.window_callnum and (event == sg.WIN_CLOSED) and sg.popup_yes_no('要離開叫號功能嗎?') == 'Yes':
            Data.window_callnum.close()
            Data.window_callnum = None
            Data.window_main.un_hide()
            
        if window == Data.window_callnum and event == '改傳送':
            s = ''
            for i in range(30):
                s += str(i) + '\n'
            Data.window_callnum['-SEND_NAMES-'].update(s)
        
        if window == Data.window_callnum and event == '改叫號':
            Data.window_callnum['-CALL0-'].update('(王小明)來賓002號請至2號櫃台', background_color=Data.highlight_color)
            Data.window_callnum['-CALL2-'].update('(王小明)來賓001號請至1號櫃台', background_color=Data.theme_background_color)
            Data.window_callnum['-CALL1-'].update('', background_color=Data.theme_background_color)
            播放聲音(Data.叫號聲)
            語音合成('來賓002號請至2號櫃台', 等待=False)
            
    Data.window_main.close()

def main():
    init()
    event_loop()

if __name__ == '__main__':
    main()