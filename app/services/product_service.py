from app.formatting import MAX_VALUE, format_brl, format_money_input, format_quantity
from app.models.product import Product
from app.repositories.product_repository import ProductRepository

NAME_LIMIT = 60


def _validated(nome, quantidade, valor_unitario):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("Informe o nome do produto.")
    if len(nome) > NAME_LIMIT:
        raise ValueError(f"O nome pode ter até {NAME_LIMIT} caracteres.")
    if quantidade < 0:
        raise ValueError("A quantidade não pode ser negativa.")
    if valor_unitario < 0:
        raise ValueError("O valor unitário não pode ser negativo.")
    if quantidade > MAX_VALUE or valor_unitario > MAX_VALUE:
        raise ValueError("O valor é alto demais.")
    return nome


class ProductService:
    def __init__(self):
        self.repo = ProductRepository()

    def list_products(self, user_id):
        products = sorted(self.repo.get_all_products(user_id), key=lambda p: p.nome.casefold())
        return [{
            "id": p.id,
            "nome": p.nome,
            "quantity": format_quantity(p.quantidade),
            "quantity_input": format_quantity(p.quantidade),
            "price": format_brl(p.valor_unitario),
            "price_input": format_money_input(p.valor_unitario),
        } for p in products]

    def add_product(self, user_id, nome, quantidade, valor_unitario):
        nome = _validated(nome, quantidade, valor_unitario)
        product = Product(nome=nome, quantidade=quantidade, valor_unitario=valor_unitario, user_id=user_id)
        return self.repo.add_product(product)

    def update_product(self, user_id, product_id, nome, quantidade, valor_unitario):
        self._own(user_id, product_id)
        nome = _validated(nome, quantidade, valor_unitario)
        self.repo.update_product(product_id, {
            "nome": nome,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
        })

    def delete_product(self, user_id, product_id):
        self._own(user_id, product_id)
        self.repo.delete_product(product_id)

    def _own(self, user_id, product_id):
        """Só o dono do produto pode mexer nele."""
        product = self.repo.get_product(product_id) if product_id else None
        if product is None or product.user_id != user_id:
            raise ValueError("Produto não encontrado.")
        return product
