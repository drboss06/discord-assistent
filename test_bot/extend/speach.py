import speech_recognition as sr
from subprocess import Popen
import vosk
import wave
import json

file_path = "test_bot/recordings/331453981782048768-1716297355316.ogg"
file_path2 = "test_bot/recordings/331453981782048768-1716297355316.wav"

def ogg_to_wav(file):
        args = ['ffmpeg','-i', file, file_path2]
        process = Popen(args)
        process.wait()

# r = sr.Recognizer()
# #ogg_to_wav(file_path)

# with sr.AudioFile(file_path2) as source:
#     audio = r.record(source)  # read the entire audio file
#     text  = r.recognize_google(audio)
#     print(text)

model = vosk.Model("test_bot/extend/vosk-model-small-ru-0.22")

wf = wave.open(file_path2, "rb")
rec = vosk.KaldiRecognizer(model, 8000)

result = ''
last_n = False

while True:
        data = wf.readframes(8000)
        if len(data) == 0:
                break

        if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())

        if res['text'] != '':
                result += f" {res['text']}"
                last_n = False
        elif not last_n:
                result += '\n'
                last_n = True

res = json.loads(rec.FinalResult())
result += f" {res['text']}"

print(result)

