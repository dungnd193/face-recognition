import os.path
import datetime
import sys
sys.path.insert(1, '/Users/dungnd/Desktop/Workspace/AI/face-recognition/Silent-Face-Anti-Spoofing')
import numpy as np
import subprocess
import pickle
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import datetime
import cvzone
import face_recognition
import EncodeGenerator
import util
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from werkzeug.utils import secure_filename
from test import test

class App:
    def __init__(self):
        self.cred = credentials.Certificate("db/serviceAccountKey.json")
        firebase_admin.initialize_app(self.cred, {
            'databaseURL': 'https://face-recognition-dungnd-default-rtdb.asia-southeast1.firebasedatabase.app/',
            'storageBucket': 'face-recognition-dungnd.appspot.com'
        })
        
        self.personInfo = None
        
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+150+50")

        self.check_button_main_window = util.get_button(self.main_window, 'Check face', 'gray', self.check, fg='black')
        self.check_button_main_window.place(x=750, y=200)


        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=300)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.load_encode_file()
    
    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()
        
    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)
        if self.personInfo:
            cvzone.cornerRect(self.most_recent_capture_arr, self.bbox, rt=0)
        
    def check(self):
        label = test(image=self.most_recent_capture_arr, 
                     model_dir="Silent-Face-Anti-Spoofing/resources/anti_spoof_models", 
                     device_id=0)
        if label == 1:
            imgS = cv2.resize(self.most_recent_capture_arr, (0, 0), None, 0.25, 0.25)
            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
            
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    self.bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    
                    id = self.peopleIds[matchIndex]
                    self.personInfo = db.reference(f'People/{id}').get()
                    print(self.personInfo)
                    util.msg_box('Welcome back!', 'Welcome, {}.'.format(self.personInfo['name']))
        else:
            util.msg_box('Hey, you are a spoofer!', 'You are fake !')
    
    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+170+70")
        
        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'gray', self.accept_register_new_user, fg='black')
        self.accept_button_register_new_user_window.place(x=750, y=300)
        
        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'gray', self.try_again_register_new_user, fg='black')
        self.try_again_button_register_new_user_window.place(x=750, y=400)
        
        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)
        
        self.add_img_to_label(self.capture_label)
        
        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)
        
        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput your ID:')
        self.text_label_register_new_user.place(x=750, y=70)
        
    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()
        
    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        id = self.entry_text_register_new_user.get(1.0, "end-1c")
        cv2.imwrite(os.path.join('Images', '{}.jpeg'.format(id)), self.register_new_user_capture)
        subprocess.run(['python', 'EncodeGenerator.py'])
        util.msg_box('Success!', 'User was registered successfully !')
        self.register_new_user_window.destroy()
    
    def load_encode_file(self):
        # Load the encoding file
        print("Loading Encode File ...")
        file = open('db/EncodeFile.p', 'rb')
        encodeListKnownWithIds = pickle.load(file)
        file.close()
        self.encodeListKnown, self.peopleIds = encodeListKnownWithIds
        print("Encode File Loaded")
              
    def start(self):
        self.main_window.mainloop()
        
app = App()
if __name__ == "__main__":
    app.start()
    

