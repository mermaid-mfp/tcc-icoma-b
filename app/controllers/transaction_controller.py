from flask import Blueprint, request, redirect, url_for, session, flash
from app.services.transaction_service import TransactionService

transaction_bp = Blueprint('transaction', __name__, url_prefix='/livro_caixa')
transaction_service = TransactionService()

def parse_amount(text):
    """Aceita '12,50', '1.234,56', 'R$ 12,50' ou '12.50'."""
    text = (text or "").replace("R$", "").strip()
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    return float(text)

@transaction_bp.route('/')
def dashboard():
    # O dashboard fica em /dashboard (main.py)
    return redirect(url_for('dashboard'))

@transaction_bp.route('/add', methods=['POST'])
def add_transaction():
    user_id = session.get('user')
    if not user_id:
        return redirect(url_for('auth.login'))

    type_trans = request.form.get('type_trans')  # 'sale' ou 'cost'
    try:
        amount = parse_amount(request.form.get('amount'))
    except ValueError:
        flash("Informe um valor válido, por exemplo 12,50.", "error")
        return redirect(url_for('dashboard'))

    try:
        transaction_service.add_transaction(
            type_trans=type_trans,
            category='sale' if type_trans == 'sale' else 'expense',
            amount=amount,
            description=request.form.get('description', '').strip(),
            client_name=request.form.get('client_name', '').strip(),
            user_id=user_id,
            payment_method=request.form.get('payment_method', '')
        )
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('dashboard'))
    except Exception as e:
        print("Erro ao adicionar transação:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return redirect(url_for('dashboard'))

    flash("Venda registrada." if type_trans == 'sale' else "Despesa registrada.", "success")
    return redirect(url_for('dashboard'))
