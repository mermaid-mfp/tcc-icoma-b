from app.firebase_setup import db

class UserRepository:
    def __init__(self):
        self.collection_name = "users"

    def get_profile(self, user_id):
        """Devolve os dados salvos no cadastro (nome, email, created_at) ou None."""
        if not db or not user_id:
            return None

        try:
            doc = db.collection(self.collection_name).document(user_id).get()
            if doc.exists:
                return doc.to_dict() or {}
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
        return None

    def get_name(self, user_id):
        """Devolve o nome salvo no cadastro, ou None se não encontrar."""
        profile = self.get_profile(user_id)
        return profile.get("nome") if profile else None

    def update_name(self, user_id, nome):
        if not db or not user_id:
            return False

        db.collection(self.collection_name).document(user_id).set({"nome": nome}, merge=True)
        return True
