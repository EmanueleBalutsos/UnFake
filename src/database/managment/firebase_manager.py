import os
import firebase_admin
from firebase_admin import credentials, firestore

class FirebaseManager:
    def __init__(self, cert_path):
        """Initializes the Firebase app if it hasn't been initialized yet."""
        if not firebase_admin._apps:
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def save_feedback(self, event, rating, comment=""):
        """Saves a new feedback record to Firestore."""
        doc_ref = self.db.collection("feedbacks").document()
        doc_ref.set({
            "event_query": event,
            "rating": int(rating),
            "comment": comment,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "language": "en"
        })

    def get_all_feedbacks(self):
        """Retrieves all feedback records from Firestore."""
        docs = self.db.collection("feedbacks").stream()
        return [doc.to_dict() for doc in docs]
