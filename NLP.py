import speech_recognition as sr
import jieba


# 音檔轉文字
def speech_to_text(audio_path):
    import speech_recognition as sr
    r = sr.Recognizer()
    WAV = sr.AudioFile(audio_path)
    with WAV as source:
        audio = r.record(source)
    sentence = r.recognize_google(audio, language="zh-TW")
    return (sentence)


if __name__ == '__main__':
    audio_path = '123.wav'
    sentence = speech_to_text(audio_path)
    print(sentence)


# 關鍵字
def search_keyword(sentence):
    keyword_where = ["哪", "位置", "找"]
    keyword_cheap = ["便宜", "價格低", "價格最低"]
    keyword_expensive = ["貴", "價格最高", "價格高", "高價"]
    keyword_popular = ["推薦", "熱門", "最好的", "熱銷", "不錯的"]
    what_Q = 0

    for i in keyword_where:
        if i in sentence:
            what_Q = 1

    for i in keyword_cheap:
        if i in sentence:
            what_Q = 2

    for i in keyword_expensive:
        if i in sentence:
            what_Q = 3

    for i in keyword_popular:
        if i in sentence:
            what_Q = 4

    return what_Q


def cut_word(sentence):
    # 自定義辭典
    jieba.load_userdict('word.txt')
    seg = jieba.cut(sentence)
    seg_list = list(seg)  # 因是generator格式 需轉list

    # 停用詞設定
    no_word = ["你", "我", "他", "嗎", "在", "的", "是", "知道", "曉得"]

    for i in seg_list:
        if i in no_word:
            seg_list.remove(i)

    return seg_list


if __name__ == '__main__':
    print('/'.join(cut_word(sentence)))
