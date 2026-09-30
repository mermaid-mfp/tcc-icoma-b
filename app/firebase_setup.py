import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        if os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        else:
            firebase_creds = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
            if firebase_creds:
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            else:
                try:
                    firebase_admin.initialize_app()
                except Exception as e:
                    print("Erro ao inicializar firebase padrão:", e)
    
    try:
        return firestore.client()
    except Exception as e:
        print("Erro ao obter cliente firestore:", e)
        return None

db = initialize_firebase()
