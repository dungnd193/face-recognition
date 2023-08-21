import cv2
import face_recognition
import pickle
import os
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# from firebase_admin import storage

# cred = credentials.Certificate("db/serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://face-recognition-dungnd-default-rtdb.asia-southeast1.firebasedatabase.app/',
#     'storageBucket': 'face-recognition-dungnd.appspot.com'
# })


# #importing student images
folderPath = "Images"
pathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])
    
    fileName = f'{folderPath}/{path}'
    # bucket = storage.bucket()
    # blob = bucket.blob(fileName)
    # blob.upload_from_filename(fileName)
    
def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    
    return encodeList

print("Encoding Started ...")
encodeListKnow = findEncoding(imgList)
encodeListKnowWithIds = [encodeListKnow, studentIds]
print("Encoding Complete")

file = open("db/EncodeFile.p", 'wb')
pickle.dump(encodeListKnowWithIds, file)
file.close()
print("File Saved")

