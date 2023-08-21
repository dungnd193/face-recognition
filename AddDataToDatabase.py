import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("db/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://face-recognition-dungnd-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('Check')

data = {
    "1930100": {
        "name": "Chipu",
        "major": "Singer",
        "starting_year": 2000,
        "standing": "G",
        "year": 4,
        "attendance_times": ["2023-06-12 00:54:34"],
    },
    "1930101": {
        "name": "Sơn Tùng",
        "major": "Singer",
        "starting_year": 2003,
        "standing": "G",
        "year": 2,
        "attendance_times": ["2023-06-14 00:54:34"],
    },
    "1930102": {
        "name": "Thuy Duong",
        "major": "Singer",
        "starting_year": 2002,
        "standing": "G",
        "year": 3,
        "attendance_times": ["2023-06-18 00:54:34"],
    },
    "1930103": {
        "name": "Nguyễn Dũng",
        "major": "IT",
        "starting_year": 2001,
        "standing": "G",
        "year": 4,
        "attendance_times": ["2023-07-12 00:54:34"],
    },
}

for key, value in data.items():
    ref.child(key).set(value)
