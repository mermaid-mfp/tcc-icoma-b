from services.firebase_auth import sign_up
from app.firebase_setup import db
import time

class AuthService:
    def register_user(self, nome, email, senha, confirma_senha=None):
        if not email or not senha or not nome:
            raise ValueError("Preencha todos os campos obrigatórios.")
            
        if confirma_senha and senha != confirma_senha:
            raise ValueError("As senhas não coincidem.")
            
        # Cadastra no Firebase Auth
        response = sign_up(email, senha)
        
        if 'error' in response:
            raise ValueError(response['error'].get('message', 'Erro ao cadastrar usuário'))
            
        # Salva informações adicionais no Firestore
        user_id = response.get('localId')
        if db:
            user_data = {
                "nome": nome,
                "email": email,
                "created_at": time.time()
            }
            db.collection("users").document(user_id).set(user_data)
            
        return True, "Usuário cadastrado com sucesso!"
