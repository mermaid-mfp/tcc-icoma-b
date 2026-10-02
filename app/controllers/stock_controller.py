from flask import Blueprint, request, redirect, url_for, flash, render_template, g
from app.auth_helpers import login_required
from app.formatting import parse_decimal
from app.services.product_service import ProductService

stock_bp = Blueprint('stock', __name__)
product_service = ProductService()


def read_form():
    """Lê os campos do formulário de produto. Levanta ValueError se algum número for inválido."""
    try:
        quantidade = parse_decimal(request.form.get('quantidade') or "0")
        valor_unitario = parse_decimal(request.form.get('valor_unitario') or "0")
    except ValueError:
        raise ValueError("Informe números válidos na quantidade e no valor, por exemplo 12,50.")
    return {
        "nome": request.form.get('nome', ''),
        "quantidade": quantidade,
        "valor_unitario": valor_unitario,
    }


@stock_bp.route('/estoque')
@login_required
def stock_page():
    products = product_service.list_products(g.user_id)
    return render_template("dashboards/stock.html", products=products, item_count=len(products))


@stock_bp.route('/estoque/novo', methods=['POST'])
@login_required
def add_product():
    try:
        product_service.add_product(g.user_id, **read_form())
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('stock.stock_page'))
    except Exception as e:
        print("Erro ao adicionar produto:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return redirect(url_for('stock.stock_page'))

    flash("Produto adicionado.", "success")
    return redirect(url_for('stock.stock_page'))


@stock_bp.route('/estoque/<product_id>/editar', methods=['POST'])
@login_required
def edit_product(product_id):
    try:
        product_service.update_product(g.user_id, product_id, **read_form())
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('stock.stock_page'))
    except Exception as e:
        print("Erro ao editar produto:", e)
        flash("Não foi possível salvar agora. Tente de novo em instantes.", "error")
        return redirect(url_for('stock.stock_page'))

    flash("Produto atualizado.", "success")
    return redirect(url_for('stock.stock_page'))


@stock_bp.route('/estoque/remover', methods=['POST'])
@login_required
def remove_product():
    try:
        product_service.delete_product(g.user_id, request.form.get('product_id', ''))
    except ValueError as ve:
        flash(str(ve), "error")
        return redirect(url_for('stock.stock_page'))
    except Exception as e:
        print("Erro ao remover produto:", e)
        flash("Não foi possível remover agora. Tente de novo em instantes.", "error")
        return redirect(url_for('stock.stock_page'))

    flash("Produto removido.", "success")
    return redirect(url_for('stock.stock_page'))
