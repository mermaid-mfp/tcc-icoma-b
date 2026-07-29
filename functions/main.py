import os
from flask import Flask, render_template, request, redirect, url_for

from services.firebase_auth import sign_in, sign_up, reset_password

app = Flask(__name__)
app.secret_key = "icoma_secret"

@app.route("/")
def index():
    nome = "icoma.com"
    return render_template('index.html', site=nome)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboards/dashboard.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            result = sign_in(email, password)
            if 'error' in result:
                error = "E-mail ou senha inválidos."
                # You can log result['error']['message'] for details
            else:
                # Login successful
                # TODO: Salvar idToken na sessão do Flask
                return redirect(url_for('dashboard'))
        except Exception as e:
            error = "Erro ao conectar com servidor de autenticação."
            
    return render_template('login/login.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        if password != confirm_password:
            error = "As senhas não coincidem."
        else:
            try:
                result = sign_up(email, password)
                if 'error' in result:
                    error = result['error']['message']
                else:
                    # Cadastro bem sucedido
                    return redirect(url_for('login'))
            except Exception as e:
                error = "Erro ao conectar com servidor de autenticação."
                
    return render_template('login/register.html', error=error)

@app.route("/recovery", methods=['GET', 'POST'])
def recovery():
    message = None
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            result = reset_password(email)
            if 'error' in result:
                error = result['error']['message']
            else:
                message = "E-mail de recuperação enviado com sucesso!"
        except Exception as e:
            error = "Erro ao conectar com servidor de autenticação."
            
    return render_template('login/recovery.html', error=error, message=message)

def main():
    app.run(port=int(os.environ.get('PORT', 80)), debug=True)

if __name__ == "__main__":
    main()
