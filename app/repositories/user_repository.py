from app.firebase_setup import db

class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    def get_name(self, user_id):
        """Devolve o nome salvo no cadastro, ou None se não encontrar."""
        if not db or not user_id:
            return None

        try:
            doc = db.collection(self.collection_name).document(user_id).get()
            if doc.exists:
                return (doc.to_dict() or {}).get("nome")
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
        return None
