import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_latest_data():
    docs = db.collection("water_data")\
             .order_by("timestamp", direction=firestore.Query.DESCENDING)\
             .limit(20).stream()

    data = []
    for doc in docs:
        data.append(doc.to_dict())

    return data