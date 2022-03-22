import os
import pyaudio
import threading
import wave
import time
from datetime import datetime
from google.cloud import speech, storage

# 需要系統開啟立體聲混音

# 錄音類
class Recorder():
    def __init__(self, chunk=1024, channels=2, rate=48000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

    # 獲取內錄裝置序號,在windows作業系統上測試通過，hostAPI = 0 表明是MME裝置
    # def findInternalRecordingDevice(self, p):
    #     # 要找查的裝置名稱中的關鍵字
    #     target = '立體聲混音'
    #     # 逐一查詢聲音裝置
    #     for i in range(p.get_device_count()):
    #         devInfo = p.get_device_info_by_index(i)
    #         # print(devInfo)
    #         if devInfo['name'].find(target) >= 0 and devInfo['hostApi'] == 0:
    #             # print('已找到內錄裝置,序號是 ',i)
    #             return i
    #     print('無法找到內錄裝置!')
    #     return -1

    # 開始錄音，開啟一個新執行緒進行錄音操作
    def start(self):
        threading._start_new_thread(self.__record, ())

    # 執行錄音的執行緒函數
    def __record(self):
        self._running = True
        self._frames = []

        p = pyaudio.PyAudio()
        # # 查詢內錄裝置
        # dev_idx = self.findInternalRecordingDevice(p)
        # if dev_idx < 0:
        #     return
        # 在開啟輸入流時指定輸入裝置
        # stream = p.open(input_device_index=dev_idx,
        #                 format=self.FORMAT,
        #                 channels=self.CHANNELS,
        #                 rate=self.RATE,
        #                 input=True,
        #                 frames_per_buffer=self.CHUNK)
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        # 迴圈讀取輸入流
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

    # 儲存到檔案
    def save(self, fileName):
        # 建立pyAudio物件
        p = pyaudio.PyAudio()
        # 開啟用於儲存資料的檔案
        wf = wave.open(fileName, 'wb')
        # 設定音訊引數
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        # 寫入資料
        wf.writeframes(b''.join(self._frames))
        # 關閉檔案
        wf.close()
        # 結束pyaudio
        p.terminate()


if __name__ == "__main__":

    # 檢測當前目錄下是否有record子目錄
    if not os.path.exists('record'):
        os.makedirs('record')

    print("npython 錄音機 ....")
    print("提示：按 r 開始錄音")

    i = input('請輸入操作碼:')
    if i == 'r':
        rec = Recorder()
        begin = time.time()

        print("開始錄音ing\n按 s 鍵停止錄音")
        rec.start()

        running = True
        while running:
            i = input("請輸入操作碼:")
            if i == 's':
                running = False
                print("錄音已停止")
                rec.stop()
                t = time.time() - begin
                print('錄音時間為%ds' % t)
                # 以當前時間為關鍵字儲存wav檔案
                rec.save("test.wav")

    YOUR_SERVICE = 'speechtotext.json'
    YOUR_AUDIO = 'test.wav'
    YOUR_BUCKET = 'coral-shift-145404.appspot.com'

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = YOUR_SERVICE

    storage_client = storage.Client()
    speech_client = speech.SpeechClient()

    # upload file to GCS(Google Cloud Storage)
    bucket = storage_client.bucket(YOUR_BUCKET)
    bucket.blob(YOUR_AUDIO).upload_from_filename(YOUR_AUDIO)
    uri = f'gs://{YOUR_BUCKET}/{YOUR_AUDIO}'

    # Transcript the audio
    audio = speech.RecognitionAudio(uri=uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # MP3 is under beta
        sample_rate_hertz=48000,
        audio_channel_count=2,  # take care, default is 1
        language_code="zh-TW"
    )
    response = speech_client.recognize(config=config, audio=audio)

    for r in response.results:
        print(f'{r.alternatives[0].transcript}, {r.alternatives[0].confidence:.3f}')
