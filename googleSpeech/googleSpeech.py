import os
from google.cloud import speech, storage

YOUR_SERVICE = 'speechtotext.json'
YOUR_AUDIO = '30.flac'
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
    encoding=speech.RecognitionConfig.AudioEncoding.FLAC,  # MP3 is under beta
    sample_rate_hertz=48000,
    audio_channel_count=2,  # take care, default is 1
    language_code="zh-TW"
)
response = speech_client.recognize(config=config, audio=audio)

for r in response.results:
    print(f'{r.alternatives[0].transcript}, {r.alternatives[0].confidence:.3f}')
