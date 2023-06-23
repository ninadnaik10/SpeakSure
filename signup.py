import kivy
import pymongo as mn
kivy.require('1.11.1')
from kivy.uix.screenmanager import Screen
# from mongo import constr

from mongo import constr

class SignUpScreen(Screen):
    def go_to_login(self):
        self.manager.current = "login_screen"

    def insert(self,username,gender,email,password,cpassword):
        print(username)
        client = mn.MongoClient(constr)
        database = client["SpeechAnalysis"]
        collection = database["User"]
        document = {"username":username,"gender":gender,"email":email,"password":password}
        if cpassword!=password:
            pass
        else:
            collection.insert_one(document)
            self.manager.current = "login_screen"

