import wave
from pyaudio import PyAudio, paInt16

CHUNK = 1024  # wav文件是由若干個CHUNK組成的，CHUNK我們就理解成數據包或者數據片段。
FORMAT = paInt16  # 表示我們使用量化位數 16位來進行錄音
CHANNELS = 2  # 代表的是聲道，1是單聲道，2是雙聲道。
RATE = 44100  # 採樣率 一秒內對聲音信號的採集次數，常用的有8kHz, 16kHz, 32kHz, 48kHz,
# 11.025kHz, 22.05kHz, 44.1kHz。
RECORD_SECONDS = 45  # 錄製時間這裏設定了5秒


def save_wave_file(pa, filename, data):
    '''save the date to the wavfile'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    # wf.setsampwidth(sampwidth)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(data))
    wf.close()


def get_audio(filepath):
    isstart = str(input("是否開始錄音？ （是/否）"))  # 輸出提示文本，input接收一個值,轉爲str，賦值給aa
    if isstart == str("是"):
        pa = PyAudio()
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK)
        print("*" * 10, "開始錄音：請在5秒內輸入語音")
        frames = []  # 定義一個列表
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):  # 循環，採樣率 44100 / 1024 * 5
            data = stream.read(CHUNK)  # 讀取chunk個字節 保存到data中
            frames.append(data)  # 向列表frames中添加數據data
        print(frames)
        print("*" * 10, "錄音結束\n")

        stream.stop_stream()
        stream.close()  # 關閉
        pa.terminate()  # 終結

        save_wave_file(pa, filepath, frames)
    elif isstart == str("否"):
        exit()
    else:
        print("無效輸入，請重新選擇")
        get_audio(filepath)


def play():
    wf = wave.open(r"01.wav", 'rb')
    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=
    wf.getnchannels(), rate=wf.getframerate(), output=True)

    # 讀數據
    data = wf.readframes(CHUNK)

    # 播放流
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()  # 暫停播放/錄製
    stream.close()  # 終止播放

    p.terminate()  # 終止portaudio會話


if __name__ == '__main__':
    filepath = '01.wav'
    get_audio(filepath)
    print('Over!')
    play()
