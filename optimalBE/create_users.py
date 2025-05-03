from pymongo import MongoClient
import bcrypt

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.optimalDB
users = db.users

user_list = [
    {
        "name": "Lorcan M",
        "username": "lorcanm",
        "prSquat": 120,
        "prBenchPress": 107,
        "prDeadlift": 140,
    }
]

for new_user in user_list:
    users.insert_one(new_user)
