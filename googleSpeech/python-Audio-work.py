# _*_ coding: utf-8 _*_

# 錄音機，用於錄製聲卡播放的聲音(內錄)
# 可以錄製鼠標操作，用於在開始錄音時回放原先的鼠標操作

import os
# 導入音頻處理模塊
import pyaudio
import threading
import wave
import time
from datetime import datetime
# 導入控制與監控鍵盤和鼠標的模塊
from pynput import keyboard, mouse


# 錄音類
class Recorder():
    def __init__(self, chunk=1024, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []
        # 錄音開始時間
        self.recBegin = 0
        # 錄音時長
        self.recTime = 0

        # 獲取內錄設備序號,在windows操作系統上測試通過，hostAPI = 0 表明是MME設備

    def findInternalRecordingDevice(self, p):
        # 要找查的設備名稱中的關鍵字
        target = '立體聲混音'
        # 逐一查找聲音設備
        for i in range(p.get_device_count()):
            devInfo = p.get_device_info_by_index(i)
            if devInfo['name'].find(target) >= 0 and devInfo['hostApi'] == 0:
                # print('已找到內錄設備,序號是 ',i)
                return i
        print('無法找到內錄設備!')
        return -1

    # 開始錄音，開啓一個新線程進行錄音操作
    def start(self):
        print("正在錄音...")
        threading._start_new_thread(self.__record, ())

    # 執行錄音的線程函數
    def __record(self):
        self.recBegin = time.time()
        self._running = True
        self._frames = []

        p = pyaudio.PyAudio()
        # 查找內錄設備
        dev_idx = self.findInternalRecordingDevice(p)
        if dev_idx < 0:
            return
        # 在打開輸入流時指定輸入設備
        stream = p.open(input_device_index=dev_idx,
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        # 循環讀取輸入流
        while (self._running):
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        # 停止讀取輸入流
        stream.stop_stream()
        # 關閉輸入流
        stream.close()
        # 結束pyaudio
        p.terminate()
        return

    # 停止錄音
    def stop(self):
        self._running = False
        self.recTime = time.time() - self.recBegin
        print("錄音已停止")
        print('錄音時間爲%ds' % self.recTime)
        # 以當前時間爲關鍵字保存wav文件
        self.save("record/rec_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".wav")

    # 保存到文件
    def save(self, fileName):
        # 創建pyAudio對象
        p = pyaudio.PyAudio()
        # 打開用於保存數據的文件
        wf = wave.open(fileName, 'wb')
        # 設置音頻參數
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        # 寫入數據
        wf.writeframes(b''.join(self._frames))
        # 關閉文件
        wf.close()
        # 結束pyaudio
        p.terminate()


# 鼠標宏 ,目前只記錄與回放click操作
class MouseMacro():
    def __init__(self):
        # 指示是否記錄鼠標事件
        self.enabled = False
        # 模擬鼠標的控制器對象
        self.mouseCtrl = mouse.Controller()
        # 記錄鼠標點擊位置的列表
        self.mouseMacroList = []

    # 開始記錄鼠標宏操作
    def beginMouseMacro(self):
        print('開始記錄鼠標宏')
        self.mouseMacroList = []
        self.enabled = True

    # 記錄鼠標宏操作
    def recordMouse(self, event):
        print('記錄鼠標事件', event)
        self.mouseMacroList.append(event)

        # 停止記錄鼠標宏操作

    def endMouseMacro(self):
        self.enabled = False
        print('停止記錄鼠標宏！')

        # 回放錄製的鼠標宏操作

    def playMouseMacro(self):
        if len(self.mouseMacroList) > 0:
            print('回放鼠標宏:', self.mouseMacroList)
        for pos in self.mouseMacroList:
            self.mouseCtrl.position = pos
            self.mouseCtrl.click(mouse.Button.left, 1)


# 監控按鍵
def on_keyPress(key):
    try:
        # print('key {0} pressed'.format( key.char))

        # 開始錄音
        if key.char == 'a':
            # 錄音前回放鼠標宏
            mouseMacro.playMouseMacro()
            recorder.start()
        # 停止錄音
        if key.char == 's':
            recorder.stop()

            # 開始錄製鼠標事件
        if key.char == '[':
            mouseMacro.beginMouseMacro()
            # 停止錄製鼠標事件
        if key.char == ']':
            mouseMacro.endMouseMacro()
            # 測試回放鼠標宏
        if key.char == 'm':
            mouseMacro.playMouseMacro()

        # 退出程序
        if key.char == 'x':
            # mouse_listener.stop()將停止對鼠標的監聽
            mouse_listener.stop()
            # 返回 False 將使鍵盤對應的lisenter停止監聽
            return False

    except Exception as e:
        print(e)


# 監控鼠標
def on_click(x, y, button, pressed):
    # print('{0} at {1}'.format('Pressed' if pressed else 'Released',(x, y)))

    # 如果正在錄製鼠標宏，記錄鼠標的點擊位置
    if pressed and mouseMacro.enabled:
        mouseMacro.recordMouse((x, y))
    return True


if __name__ == "__main__":

    # 檢測當前目錄下是否有record子目錄
    if not os.path.exists('record'):
        os.makedirs('record')

    print("\npython 錄音機 ....\n")
    print("----------------- 提示 ------------------------------------------\n")
    print("按 a 鍵 開始錄音,     按 s 鍵 停止錄音 ,     按 x 鍵 退出程序 ")
    print("按 [ 鍵 開始記錄鼠標, 按 ] 鍵 停止記錄鼠標 , 按 m 鍵 回放鼠標宏  \n")
    print("-----------------------------------------------------------------\n")

    # 創建錄音機對象
    recorder = Recorder()
    # 創建“鼠標宏”對象
    mouseMacro = MouseMacro()

    # 開始監聽鼠標與鍵盤
    keyboard_listener = keyboard.Listener(on_press=on_keyPress)
    mouse_listener = mouse.Listener(on_click=on_click)
    lst = [keyboard_listener, mouse_listener]
    for t in lst:
        t.start()
    for t in lst:
        t.join()
