from flask import Flask, render_template, redirect, session
import os
from app.controllers.transaction_controller import transaction_bp
from app.controllers.auth_controller import auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key')

app.register_blueprint(transaction_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    nome = 'icoma.com.br'
    return render_template('index.html', site=nome)

@app.route('/recovery')
def recovery():
    return render_template('login/recovery.html')

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboards/dashboard.html")

def main():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    main()