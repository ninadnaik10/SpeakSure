import kivy
import pymongo as mn
from kivy.core.window import Window
kivy.require('1.11.1')
from kivy.uix.screenmanager import (ScreenManager,Screen,NoTransition)
from tkinter import messagebox
import gridfs
# from mongo import constr
from kivy.uix.button import Button

import matplotlib
from kivy.lang import Builder
from kivy.app import App
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.uix.floatlayout import FloatLayout
import matplotlib.pyplot as plt

from mongo import constr

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)

    def save(self):
        rec_screen = self.manager.get_screen('rec_screen')
        # b = rec_name.hi
        # b()
        self.transcript = rec_screen.transcripted_audio
        print(self.transcript)
        rec_name = rec_screen.ids.recording_name.text
        percent_filler = rec_screen.percent_filler
        pace = rec_screen.pace
        prediction = rec_screen.prediction
        score = rec_screen.score

        client = mn.MongoClient(constr)
        db = client.grid_file
        temp = "temp.wav"
        file_location = "C:/Users/Admin/Desktop/SpeakSure-master/recordings/" + temp

        file_data = open(file_location,"rb")

        data = file_data.read()
        fs= gridfs.GridFS(db)
        login_screnn = self.manager.get_screen('login_screen')
        username = login_screnn.ids.username.text
        fs.put(data, filename = rec_name, metadata = {"username":username,"percent_filler":percent_filler,"pace":pace,"transcript":self.transcript,"prediction":prediction,"score":score})

        # # name = "temp.wav"
        login_screen = self.manager.get_screen('login_screen')
        x = login_screen.ids.username.text
        data = db.fs.files.find({"metadata.username": x})

        d = self.manager.get_screen('dash_screen')
        # d.add_widget(Label(text="Username"))
        x = 0.498
        y = 0.95
        info_filename = []
        info_score = []
        info_pace = []

        s = {}
        for doc in data:
            # print("hi")
            y = y - 0.1
            text = doc["filename"]
            s = Button(text = text, size_hint = (1, 0.1) ,pos_hint= {"center_x": x, "center_y": y})
            s.bind(on_press = d.result)
            d.ids.history.add_widget(s)
            info_filename.append(doc["filename"])
            s = doc["metadata"]
            info_score.append(s["score"])
            info_pace.append(s["pace"])

        fig, ax = plt.subplots()
        x = []
        y = info_score
        q = 1
        for i in range(len(info_score)):
            x.append(q)
            q = q + 1

        plt.xticks(x,info_filename)
        plt.plot(x,y,'w.-', markersize =15, markeredgecolor = "yellow")
        plt.ylabel("Filler words",color="white")
        plt.xlabel("Previous recordings",color="white")
        ax.plot(x, y)         
        
        ax.tick_params(axis='both', which='both', color='white')
        ax.tick_params(axis='both', which='both', labelcolor='white') #c60024
        
        fig.set_facecolor('black')
        ax.set_facecolor("#232323")

        box = d.ids.box
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

# =========================================================================================================
        fig, ax = plt.subplots()

        x = []
        y = info_pace
        q = 1
        for i in range(len(info_score)):
            x.append(q)
            q = q + 1

        plt.xticks(x,info_filename)
        plt.plot(x,y,'w.-', markersize =15, markeredgecolor = "yellow")
        plt.ylabel("Pace",color="white")
        plt.xlabel("Previous recordings",color="white")
        ax.plot(x, y)         
        
        ax.tick_params(axis='both', which='both', color='white')
        ax.tick_params(axis='both', which='both', labelcolor='white') #c60024

        fig.set_facecolor('black')
        ax.set_facecolor("#232323")

        box = d.ids.box1
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        self.manager.current = "dash_screen"
        

    def go_to_dash(self):
        print('hi')
        self.manager.current = "dash_screen"