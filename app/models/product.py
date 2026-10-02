import datetime

class Product:
    def __init__(self, nome, quantidade, valor_unitario, user_id=None, created_at=None, id=None):
        self.id = id
        self.nome = nome
        self.quantidade = float(quantidade)
        self.valor_unitario = float(valor_unitario)
        self.user_id = user_id
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc)

    def to_dict(self):
        return {
            "nome": self.nome,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "user_id": self.user_id,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data, doc_id=None):
        return Product(
            id=doc_id,
            nome=data.get("nome", ""),
            quantidade=data.get("quantidade", 0.0),
            valor_unitario=data.get("valor_unitario", 0.0),
            user_id=data.get("user_id"),
            created_at=data.get("created_at")
        )
