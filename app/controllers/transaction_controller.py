import datetime

from flask import Blueprint, request, redirect, url_for, flash, render_template, g
from app.auth_helpers import login_required
from app.formatting import BRT, parse_decimal
from app.services.transaction_service import TransactionService, parse_date

transaction_bp = Blueprint('transaction', __name__)
transaction_service = TransactionService()


def back_to(default_endpoint):
    """Volta para a página de onde o formulário foi enviado (só endereços do próprio site)."""
    target = request.form.get("back", "")
    if target.startswith(("/dashboard", "/transacoes")) and not target.startswith("//"):
        return redirect(target)
    return redirect(url_for(default_endpoint))


def read_form():
    """Lê os campos do formulário de transação. Levanta ValueError se o valor não for um número."""
    try:
        amount = parse_decimal(request.form.get('amount'))
    except ValueError:
        raise ValueError("Informe um valor válido, por exemplo 12,50.")
    return {
        "type_trans": request.form.get('type_trans'),  # 'sale' ou 'cost'
        "amount": amount,
        "description": request.form.get('description', ''),
        "payment_method": request.form.get('payment_method', ''),
        "status": request.form.get('status', 'concluido'),
    }


@transaction_bp.route('/transacoes')
@login_required
def transactions_page():
    today = datetime.datetime.now(BRT).date()
    if "de" in request.args or "ate" in request.args:
        date_from = parse_date(request.args.get("de"))
        date_to = parse_date(request.args.get("ate"))
    else:
        date_from, date_to = today.replace(day=1), today  # primeira visita: o mês atual

    if date_from and date_to and date_from > date_to:
        date_from, date_to = date_to, date_from

    query = request.args.get("q", "").strip()
    data = transaction_service.list_transactions(g.user_id, date_from, date_to, query)
    return render_template(
        "dashboards/transactions.html",
        date_from=date_from.isoformat() if date_from else "",
        date_to=date_to.isoformat() if date_to else "",
        query=query,
        **data
    )


@transaction_bp.route('/transacoes/nova', methods=['POST'])
@login_required
def add_transaction():
    try:
        fields = read_form()
        transaction_service.add_transaction(
            type_trans=fields["type_trans"],
            category='sale' if fields["type_trans"] == 'sale' else 'expense',
            amount=fields["amount"],
            description=fields["description"],
            client_name=request.form.get('client_name', '').strip(),
            user_id=g.user_id,
            payment_method=fields["payment_method"],
            status=fields["status"]
        )
    except ValueError as ve:
        flash(str(ve), "error")
        return back_to('dashboard')
    except Exception as e:
        print("Erro ao adicionar transação:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return back_to('dashboard')

    flash("Venda registrada." if fields["type_trans"] == 'sale' else "Despesa registrada.", "success")
    return back_to('dashboard')


@transaction_bp.route('/transacoes/<transaction_id>/editar', methods=['POST'])
@login_required
def edit_transaction(transaction_id):
    try:
        fields = read_form()
        transaction_service.update_transaction(g.user_id, transaction_id, **fields)
    except ValueError as ve:
        flash(str(ve), "error")
        return back_to('transaction.transactions_page')
    except Exception as e:
        print("Erro ao editar transação:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return back_to('transaction.transactions_page')

    flash("Transação atualizada.", "success")
    return back_to('transaction.transactions_page')


@transaction_bp.route('/transacoes/<transaction_id>/excluir', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    try:
        transaction_service.delete_transaction(g.user_id, transaction_id)
    except ValueError as ve:
        flash(str(ve), "error")
        return back_to('transaction.transactions_page')
    except Exception as e:
        print("Erro ao excluir transação:", e)
        flash("Não foi possível excluir agora. Tente de novo em instantes.", "error")
        return back_to('transaction.transactions_page')

    flash("Transação excluída.", "success")
    return back_to('transaction.transactions_page')
