import datetime
from app.firebase_setup import db
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

            # A ordenação é feita aqui no Python: pedir where + order_by em campos
            # diferentes exigiria criar um índice composto no Firestore.
            transactions = [Transaction.from_dict(doc.to_dict(), doc.id) for doc in query.stream()]
            transactions.sort(key=self._sort_key, reverse=True)
            return transactions
        except Exception as e:
            print(f"Erro ao buscar transações: {e}")
            return []

    @staticmethod
    def _sort_key(transaction):
        ts = transaction.timestamp
        if not isinstance(ts, datetime.datetime):
            return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        if ts.tzinfo is None:
            return ts.replace(tzinfo=datetime.timezone.utc)
        return ts
