from flask import Flask, render_template, session, g
import os
from app.auth_helpers import login_required
from app.controllers.transaction_controller import transaction_bp, transaction_service
from app.controllers.stock_controller import stock_bp
from app.controllers.profile_controller import profile_bp
from app.controllers.auth_controller import auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key')
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # o login não vale para pedidos vindos de outros sites

app.register_blueprint(transaction_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    nome = 'icoma.com.br'
    return render_template('index.html', site=nome)

@app.route('/recovery')
def recovery():
    return render_template('login/recovery.html')

@app.route("/dashboard")
@login_required
def dashboard():
    fallback_name = session.get("email", "").split("@")[0]
    data = transaction_service.get_dashboard_data(g.user_id, fallback_name=fallback_name)
    return render_template("dashboards/dashboard.html", **data)

def main():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    main()
