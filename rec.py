import kivy
kivy.require('1.11.1')
from kivy.clock import Clock 
from kivy.graphics import *
import sounddevice as sd
from kivy.uix.screenmanager import Screen
import queue
import soundfile as sf
import threading
from tkinter import messagebox
from os import path
import requests
import time
import testing as t

UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPTION_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

api_key = API_KEY
headers = {"authorization": api_key, "content-type": "application/json"}
 
class RecScreen(Screen):
    def __init__(self, **kwargs):

        super(RecScreen, self).__init__(**kwargs)
        self.c = []
        self.c  = Clock
        self.cam = False
        self.audio = False
        self.time = True
        self.index = 0
        self.q = queue.Queue()
        self.recording = False
        self.file_exists = False
        self.transcripted_audio = ""
        self.filler_count = 0
        self.score = 0
        # self.pace = 0
        self.filename = self.filename = path.join("recordings", "temp" +".wav")

    def on_start1(self):

        if self.ids.recording_name.text == "" :
            messagebox.showinfo(message="Enter Recording Name first")
            pass
        elif not self.audio and self.time :
            if self.index == 0:
                self.c.schedule_interval(self.update_label, 1)
                self.c.schedule_interval(self.update_label_min, 60)
            self.audio = True
            self.time = False
            self.threading_rec(1)

    def on_stop(self):

        if  self.audio:
            self.audio = False
            self.threading_rec(2)

    def update_label(self,*args):

        if self.audio:
            self.ids.sec_counter.text = str(int(self.ids.sec_counter.text) + 1)
            if(int(self.ids.sec_counter.text) > 60.0):
                self.ids.sec_counter.text = str(0)
 
    def update_label_min(self,*args):
        if self.audio:
            self.ids.min_counter.text = str(int(self.ids.min_counter.text) + 1)

    def camera_start(self):

        if not self.cam:
            self.ids.camera.play = True
            self.ids.img.size_hint = 0,0
            self.cam = True
        else:
            self.ids.camera.play = False
            self.ids.img.size_hint = 0.8,0.6
            self.cam = False
            self.index = 1

    def reset(self):
        self.cam = False
        self.audio = False
        self.time = True
        self.ids.camera.play = False
        self.ids.min_counter.text = "00"
        self.ids.sec_counter.text = "00"
        self.ids.img.size_hint = 0.8,0.6
        self.index = self.index + 1

    def threading_rec(self,x):
        if x == 1:
            t1 = threading.Thread(target=self.record_audio)
            t1.start()
        elif x == 2:
            self.recording = False
            messagebox.showinfo(message="Recording finished")
        elif x == 3:
            if self.file_exists:
                data, fs = sf.read(self.filename, dtype='float32')
                sd.play(data, fs)
                sd.wait()
            else:
                messagebox.showerror(message="Record something to play")

    def callback(self,indata, frames, time, status):
        self.q.put(indata.copy())

    # def transcription(self):
    #     r = sr.Recognizer()
    #     with sr.AudioFile(self.filename) as source:
    #         audio = r.record(source)
    #     try:
    #         print("The audio file contains: " + r.recognize_google(audio))
    #     except sr.UnknownValueError:
    #         print("Google Speech Recognition could not understand audio")


    def read_file(self):
        with open(self.filename, 'rb') as _file:
            while True:
                data = _file.read(5242880)
                if not data:
                    break
                yield data

    def record_audio(self):
        # self.recording = True
        # with sf.SoundFile(self.filename, mode='w', samplerate=44100,
        #                 channels=1) as file:
        #     with sd.InputStream(samplerate=44100, channels=1, callback=self.callback):
        #         while self.recording:
        #             self.file_exists = True
        #             file.write(self.q.get())

        self.recording = True

        with sf.SoundFile(self.filename, mode='w', samplerate=44100,
                        channels=1) as file:
            with sd.InputStream(samplerate=44100, channels=1, callback=self.callback):
                while self.recording:
                    self.file_exists = True
                    file.write(self.q.get())

    def hi(self):
        print('hi')

    def transcription(self):

        upload_response = requests.post(UPLOAD_ENDPOINT, headers=headers, data=self.read_file())
        audio_url = upload_response.json()["upload_url"]
        transcript_request = {'audio_url': audio_url, 'disfluencies': True}
        transcript_response = requests.post(TRANSCRIPTION_ENDPOINT, json=transcript_request, headers=headers)
        _id = transcript_response.json()["id"]
        polling_response = requests.get(TRANSCRIPTION_ENDPOINT + "/" + _id, headers=headers)
        while True:
            polling_response = requests.get(TRANSCRIPTION_ENDPOINT + "/" + _id, headers=headers)

            if polling_response.json()['status'] == 'completed':
                # print(polling_response.json()['text'])
                break
            elif polling_response.json()['status'] == 'error':
                raise Exception("Transcription failed. Make sure a valid API key has been used.")
            else:
                print("Transcription queued or processing ...")
            # time.sleep(5)
        self.transcripted_audio = polling_response.json()['text']
        self.numOfWords = len(self.transcripted_audio.split())
        print("numofwords:",self.numOfWords)
        self.detectFillers()

    def dashboard(self):
        self.manager.current = "dash_screen"

    def detectFillers(self):

        filler_words = [
        ' um ', ' uh ', ' er ', 'ah ', 'you know', 'so so', ' well ', 
        'basically', 'literally', 'somewhat', 'more or less', 'kind of', 'sort of', 'maybe', 'perhaps', 'right']

        count = 0
        for word in filler_words:
            count += self.transcripted_audio.lower().count(word)
        self.filler_count = count

        self.percent_filler = self.filler_count/self.numOfWords*100
        # print("percent:",self.percent_filler)
        print("percent_filler:",self.percent_filler)

        # try:
        self.pace = self.numOfWords *60 /(int(self.ids.min_counter.text) * 60 + int(self.ids.sec_counter.text))
        self.predictModel()

        # except:
        #     messagebox.showinfo(message="Try Again! Error")
            # self.reset()

    def predictModel(self):

        filler_words1 = [
        'um','uh', 'ur','er', 'ah', 'you know', 'so so', ' well ', 'Ur','Uh','Er','Um','Ah',
        'basically', 'literally', 'somewhat', 'more or less', 'kind of', 'sort of', 'maybe', 'perhaps', 'right']

        filler_words = []
        for i in filler_words1:
            h = " " + i + " "
            filler_words.append(h)
        for i in filler_words1:
            h = i + "."
            filler_words.append(h)
        for i in filler_words1:
            h = "." + i
            filler_words.append(h)
        for i in filler_words1:
            h = i + ","
            filler_words.append(h)

        features = t.extract_feature(self.filename, mfcc=True, chroma=True, mel=True)
        features = features.reshape(1,-1)
        prediction = t.pickled_model.predict(features)
        self.prediction = prediction[0]
        print(self.prediction)
        self.calculateScore()

        result_screen = self.manager.get_screen('result_screen')
        result_screen.ids.filler.text = str(int(self.percent_filler))+"%"
        result_screen.ids.pace.text = str(int(self.pace))
        result_screen.ids.score.text = str(int(self.score))

        r = self.transcripted_audio
        for word in filler_words:
            r = r.replace(word, '[color=ff3333]{}[/color]'.format(word))
        result_screen.ids.transcript.text = r

    def calculateScore(self):
        if self.prediction == "yes":

            print("prev:",self.score)
            self.score = self.score + 60
            if self.pace>139 and self.pace<181:
                self.score = self.score + 20
            if self.percent_filler < 10 :
                self.score = self.score + 10
            elif self.percent_filler < 5:
                self.score = self.score + 20
            elif self.percent_filler > 20:
                self.score = self.score + 5
                
            print(self.score)
        else:
            #calculate score
            self.score = self.score + 10
            if self.pace>139 and self.pace<181:
                self.score = self.score + 25
            if self.percent_filler<5:
                self.score = self.score + 25
            elif self.percent_filler<10:
                self.score = self.score + 15

            print(self.score) 

    def message(self):
        messagebox.showinfo(message="This may take some. Please Wait!!")

    def show_results(self):
        t3 = threading.Thread(target=self.message)
        t3.start()
        self.transcription()

        self.manager.current = "result_screen"


        