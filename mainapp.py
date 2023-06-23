# from logging import root
import kivy
from kivy.app import App
kivy.require('1.11.1')
import pymongo as mn
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.uix.screenmanager import (ScreenManager,Screen,NoTransition)

# from mongo import constr
from resultClass import ResultScreen
from rec import RecScreen
from signup import SignUpScreen
from dashboard import DashScreen

import matplotlib
from kivy.lang import Builder
from kivy.app import App
matplotlib.use("module://kivy.garden.matplotlib.backend_kivy")
from kivy.garden.matplotlib import FigureCanvasKivyAgg
from kivy.uix.floatlayout import FloatLayout
import matplotlib.pyplot as plt

from mongo import constr

class LoginScreen(Screen):

    def hoop(self):
        self.manager.current = "result_screen"

    def loop(self):
        client = mn.MongoClient(constr)
        db = client.grid_file
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
            y = y - 0.1
            s = doc["metadata"]
            info_score.append(s["score"])
            info_pace.append(s["pace"])
            text = doc["filename"]
            info_filename.append(text)

            s = Button(text = text,background_color =(0.5,.5,.5,.5), size_hint = (1, 0.1) ,pos_hint= {"center_x": x, "center_y": y})
            s.bind(on_press = d.result)
            d.ids.history.add_widget(s)          

        fig, ax = plt.subplots()
        # Define what we want to graph
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
        
        # ax = plt.axes(x,y)
        fig.set_facecolor('black')
        ax.set_facecolor("#232323")

        box = d.ids.box
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
# =========================================================================================================
        fig, ax = plt.subplots()
        # Define what we want to graph
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
        
        # ax = plt.axes(x,y)
        fig.set_facecolor('black')
        ax.set_facecolor("#232323")

        box = d.ids.box1
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        self.manager.current = "dash_screen"

    def result(self):
        print("hi")

    def go_to_signup(self):
        self.manager.current = "signup_screen"

    def login(self,username,password):
        client = mn.MongoClient(constr)
        database = client["SpeechAnalysis"]
        collection = database["User"]
       
        for i in  collection.find({"username":username}):
            if i["password"] == password:
                self.loop()
                # self.manager.current = "rec_screen"
            else:
                print("hi")

class RootWidget(ScreenManager):
    pass

class NaagApp(App):

    def build(self):
        self.title = "SpeakSure"
        sm = RootWidget(transition = NoTransition())
        return  sm

if __name__ == '__main__':
    # s = NaagApp()
    NaagApp().run()