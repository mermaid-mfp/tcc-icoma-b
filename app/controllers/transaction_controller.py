from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.services.transaction_service import TransactionService

transaction_bp = Blueprint('transaction', __name__, url_prefix='/livro_caixa')
transaction_service = TransactionService()

@transaction_bp.route('/')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, faça login para acessar o dashboard.", "error")
        return redirect(url_for('auth.login'))
        
    metrics = transaction_service.get_dashboard_metrics(user_id=user_id)
    return render_template('dashboards/dashboard.html', metrics=metrics)

@transaction_bp.route('/add', methods=['POST'])
def add_transaction():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        
        type_trans = request.form.get('type_trans') # 'cost' ou 'sale'
        category = request.form.get('category')
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', '')
        client_name = request.form.get('client_name', '')
        
        transaction_service.add_transaction(
            type_trans=type_trans,
            category=category,
            amount=amount,
            description=description,
            client_name=client_name,
            user_id=user_id
        )
        
        return redirect(url_for('transaction.dashboard'))
    except Exception as e:
        print("Erro ao adicionar transação:", e)
        return "Erro ao processar", 500
