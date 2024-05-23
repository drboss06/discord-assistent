from subprocess import Popen
import speech_recognition as sr


file_path = "/workspaces/assist/test_bot/recordings/331453981782048768-1716313968713.ogg"
file_path2 = "/workspaces/assist/test_bot/recordings/331453981782048768-1716313968713.wav"
file_path3 = "/workspaces/assist/test_bot/recordings/331453981782048768-1716313968713.mp3"

def ogg_to_wav(file):
    args = ['ffmpeg','-i', file, file_path3]
    process = Popen(args)
    process.wait()

r = sr.Recognizer()


with sr.AudioFile(file_path2) as source:
    audio_data = r.record(source)
    text = r.recognize_google(audio_data, language="ru-RU")
    print(text)