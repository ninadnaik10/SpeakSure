import kivy
from kivy.core.window import Window
kivy.require('1.11.1')
import pymongo as mn
from kivy.uix.screenmanager import (ScreenManager,Screen,NoTransition)
from tkinter import messagebox
from kivy.uix.label import Label
from kivy.uix.button import Button
# from mongo import constr

from mongo import constr

class DashScreen(Screen):
    def __init__(self, **kwargs):
        super(DashScreen, self).__init__(**kwargs)

    def result(self,widget):

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

        client = mn.MongoClient(constr)
        db = client.grid_file
        # # name = "temp.wav"
        login_screen = self.manager.get_screen('login_screen')
        x = login_screen.ids.username.text
        data = db.fs.files.find_one({"filename":widget.text,"metadata.username": x})

        metadata = data["metadata"]
        self.pace = metadata["pace"]
        self.score = metadata["score"]
        self.transcript = metadata["transcript"]
        self.percent_filler = metadata["percent_filler"]
        print(self.percent_filler)

        r = self.transcript
        result = self.manager.get_screen('result_screen')

        for word in filler_words:
            r = r.replace(word, '[color=ff3333]{}[/color]'.format(word))
        result.ids.transcript.text = r

        
        result.ids.pace.text = str(int(self.pace))
        result.ids.filler.text = str(int(self.percent_filler))+"%"
        result.ids.score.text = str(int(self.score))
        # result.ids.pace.text = str(self.pace)

        # result.ids.p = self.pace
        self.manager.current = 'result_screen'    
        pass

    def record(self):
        self.manager.current = "rec_screen"
        
    # def jj(self):
    #     h = self.manager.get_screen('rec_screen')
    #     # self.transcript = h.cam
    #     client = mn.MongoClient(constr)
    #     db = client.grid_file
    #     name = "temp.wav"
    #     data = db.fs.files.find({"metadata.username":"ashop"})
    #     for doc in data:
            # print(doc)
        # ref_to_other_screen = self.screen_manager.get_screen("rec_screen")
        # self.ids.other_title.text = ref_to_other_screen.ids.your_message.text
        # NaagApp.