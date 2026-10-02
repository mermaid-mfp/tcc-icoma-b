import datetime

from app.formatting import to_local
from app.repositories.user_repository import UserRepository
from services.firebase_auth import reset_password

NAME_LIMIT = 80


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def get_profile(self, user_id, fallback_email=""):
        data = self.repo.get_profile(user_id) or {}
        nome = (data.get("nome") or "").strip()
        email = data.get("email") or fallback_email

        created = data.get("created_at")
        if isinstance(created, (int, float)):
            created = datetime.datetime.fromtimestamp(created, datetime.timezone.utc)
        local = to_local(created)

        return {
            "nome": nome,
            "email": email,
            "initial": (nome or email or "?")[0].upper(),
            "member_since": local.strftime("%d/%m/%Y") if local else "",
        }

    def update_name(self, user_id, nome):
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Informe o seu nome.")
        if len(nome) > NAME_LIMIT:
            raise ValueError(f"O nome pode ter até {NAME_LIMIT} caracteres.")
        self.repo.update_name(user_id, nome)

    def send_password_reset(self, email):
        """Pede ao Firebase para enviar o e-mail de redefinição. Devolve True se enviou."""
        if not email:
            return False
        try:
            response = reset_password(email)
        except Exception as e:
            print("Erro ao pedir redefinição de senha:", e)
            return False
        return isinstance(response, dict) and "error" not in response
