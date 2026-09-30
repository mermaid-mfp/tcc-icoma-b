from app.firebase_setup import db
from firebase_admin import firestore
from app.models.transaction import Transaction

class TransactionRepository:
    def __init__(self):
        self.collection_name = "transactions"
    
    def add_transaction(self, transaction: Transaction):
        if not db:
            print("DB não inicializado")
            return None
            
        doc_ref = db.collection(self.collection_name).document()
        transaction.id = doc_ref.id
        doc_ref.set(transaction.to_dict())
        return transaction.id

    def get_all_transactions(self, user_id=None):
        if not db:
            return []
            
        try:
            query = db.collection(self.collection_name)
            if user_id:
                query = query.where("user_id", "==", user_id)
            
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            transactions = []
            for doc in docs:
                transactions.append(Transaction.from_dict(doc.to_dict(), doc.id))
            return transactions
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return []
