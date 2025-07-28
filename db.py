import pymongo, os
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

MONGODB_URI = os.getenv("DB_URI")
DATABASE_NAME = "birthday-reminder"

client = pymongo.MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
users = db['users']

def create_user(name, number, password, birthday):
    if users.find_one({"number": number}):
        return None
    hashed = generate_password_hash(password)
    user_doc = {
        "name": name,
        "number": number,
        "password": hashed,
        "birthday": birthday,
        "reminders": []
    }
    users.insert_one(user_doc)
    return user_doc

def authenticate_user(number, password):
    user = users.find_one({"number": number})
    if not user or not check_password_hash(user["password"], password):
        return None
    return user

def add_reminder(user_number, friend_name, friend_number, date, note):
    new_reminder = {
        "_id": ObjectId(),
        "name": friend_name,
        "number": friend_number,
        "date": date,
        "note": note
    }
    result = users.update_one(
        {"number": user_number},
        {"$push": {"reminders": new_reminder}}
    )
    return str(new_reminder["_id"]) if result.modified_count > 0 else None

def get_reminders(user_number):
    user = users.find_one({"number": user_number}, {"reminders": 1, "_id": 0})
    return user['reminders'] if user else []

def delete_reminder(user_number, reminder_id):
    try:
        oid = ObjectId(reminder_id)
    except:
        return False
    result = users.update_one(
        {"number": user_number},
        {"$pull": {"reminders": {"_id": oid}}}
    )
    return result.modified_count > 0

def update_reminder(user_number, reminder_id, **fields):
    allowed_fields = {'name', 'number', 'date', 'note'}
    update_fields = {f"reminders.$.{k}": v for k, v in fields.items() if k in allowed_fields and v is not None}
    if not update_fields:
        return False
    try:
        oid = ObjectId(reminder_id)
    except:
        return False
    filter_query = {"number": user_number, "reminders._id": oid}
    update_query = {"$set": update_fields}
    result = users.update_one(filter_query, update_query)
    return result.modified_count > 0

def get_user_profile(number):
    user = users.find_one({"number": number}, {"password": 0})
    return user
