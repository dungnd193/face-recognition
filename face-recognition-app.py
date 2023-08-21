import os.path
import datetime
import sys
sys.path.insert(1, '/Users/dungnd/Desktop/Workspace/AI/face-recognition/server/Silent-Face-Anti-Spoofing')
import numpy as np
import pickle
import cv2
import datetime
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, request, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid
import subprocess
import EncodeGenerator
from test import test

UPLOAD_FOLDER = '/Users/dungnd/Desktop/Workspace/AI/face-recognition/server/Images'
CHECK_FOLDER = '/Users/dungnd/Desktop/Workspace/AI/face-recognition/server/Check'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

server = Flask(__name__)
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
server.config['CHECK_FOLDER'] = CHECK_FOLDER

cred = credentials.Certificate("db/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://face-recognition-dungnd-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'face-recognition-dungnd.appspot.com'
})

    
# Load the encoding file
print("Loading Encode File ...")
file = open('db/EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
print("Encode File Loaded")
encodeListKnown, peopleIds =  encodeListKnownWithIds

def check(image, filename):
    label = test(image=image, 
                    model_dir="Silent-Face-Anti-Spoofing/resources/anti_spoof_models", 
                    device_id=0)
    if label == 1:
        imgS = cv2.resize(image, (0, 0), None, 0.25, 0.25)
        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
        
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                
                id = peopleIds[matchIndex]
                personInfo = db.reference(f'Check/{datetime.datetime.now().strftime("%Y-%m-%d")}/{id}').get()
                if not (personInfo and ('attendance_times' in personInfo)):
                    personInfo = db.reference(f'People/{id}').get()
                    if not personInfo:
                        return {"message": "Please create your account!", "code": 400}, 400           
                        
                    for key in ['major', 'standing', 'starting_year', 'year']:
                        personInfo.pop(key)
                    personInfo['attendance_times'] = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    personInfo['filename'] = [filename]
                    data = {}
                    data[id] = personInfo
                    ref = db.reference(f'Check/{datetime.datetime.now().strftime("%Y-%m-%d")}')
                    for key, value in data.items():
                        ref.child(key).set(value)
                else:
                    ref = db.reference(f'Check/{datetime.datetime.now().strftime("%Y-%m-%d")}/{id}')
                    personInfo['attendance_times'].append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    personInfo['filename'].append(filename)
                    ref.child('attendance_times').set(personInfo['attendance_times'])
                    ref.child('filename').set(personInfo['filename'])
                return {"message": f"Xin chào {personInfo['name']}", "code": 200}, 200
        return {"message": "Can not recognize your face, please try again!", "code": 400}, 400           
        
    else:
        return {"message": "Can not recognize your face, please try again!", "code": 400}, 400           
    
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@server.route('/api/create-user', methods=['POST'])
def create_user():
    # check if the post request has the file part
    form_data = request.form
    if 'file' not in request.files:
        flash('No file part')
        return {"message": "Error"}
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return {"message": "Error", "code": 400}, 400
    if file and allowed_file(file.filename):
        file.save(os.path.join(server.config['UPLOAD_FOLDER'], form_data.get('id')+'.jpeg'))
        data = {}
        data[form_data.get('id')] = {
            'name': form_data.get('name'),
            'major': form_data.get('major'),
            'starting_year': int(form_data.get('starting_year')),  
            'standing': form_data.get('standing'),
            'year': int(form_data.get('year')),
        }
        ref = db.reference(f'People')
        for key, value in data.items():
            ref.child(key).set(value)

    return {"message": "Create user successfully!", "code": 200}, 200
    
@server.route('/api/check-face', methods=['POST'])
def check_face():
    if 'file' not in request.files:
        flash('No file part')
        return {"message": "Error"}
    file = request.files['file']
    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return {"message": "Error"}
    if file:
        folder_path = os.path.join(server.config['CHECK_FOLDER'], datetime.datetime.now().strftime("%Y-%m-%d"))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = str(uuid.uuid4()) + '.jpeg'
        path = os.path.join(folder_path, filename)
        file.save(path)
        
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)    
        image = cv2.resize(image, (500, 280))
        return check(image, filename)

if __name__ == "__main__":
    subprocess.run(['python', 'EncodeGenerator.py'])
    server.run()
    

