import datetime

class Transaction:
    def __init__(self, type_trans, category, amount, description="", timestamp=None, client_name="", user_id=None, id=None, payment_method=""):
        """
        type_trans: 'cost' ou 'sale'
        category: 'raw_material', 'production', 'sales_input', 'sale', 'expense'
        amount: float
        payment_method: 'pix', 'dinheiro', 'debito' ou 'credito' (só para vendas)
        """
        self.id = id
        self.type_trans = type_trans
        self.category = category
        self.amount = float(amount)
        self.description = description
        self.timestamp = timestamp if timestamp else datetime.datetime.now(datetime.timezone.utc)
        self.client_name = client_name
        self.user_id = user_id
        self.payment_method = payment_method

    def to_dict(self):
        return {
            "type_trans": self.type_trans,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
            "timestamp": self.timestamp,
            "client_name": self.client_name,
            "user_id": self.user_id,
            "payment_method": self.payment_method
        }

    @staticmethod
    def from_dict(data, doc_id=None):
        return Transaction(
            id=doc_id,
            type_trans=data.get("type_trans"),
            category=data.get("category"),
            amount=data.get("amount", 0.0),
            description=data.get("description", ""),
            timestamp=data.get("timestamp"),
            client_name=data.get("client_name", ""),
            user_id=data.get("user_id"),
            payment_method=data.get("payment_method", "")
        )
