import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

_db = None

def _get_db():
    """Return Firestore client, initializing Firebase only once."""
    global _db
    if _db is not None:
        return _db
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db

def upload_sensor_value(value: int) -> bool:
    """
    Upload one real sensor reading to Firestore → collection: water_data
    Only call this with real values (not None).
    Returns True on success, False on failure.
    """
    try:
        db = _get_db()
        db.collection("water_data").add({
            "value": int(value),
            "timestamp": datetime.utcnow().isoformat()
        })
        return True
    except Exception as e:
        print(f"[Firebase] Upload failed: {e}")
        return False
